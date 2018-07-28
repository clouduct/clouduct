#!/usr/bin/env python
"""Creating a new project based on an existing one.
"""

import fileinput
import os
import shutil
import sys

import pathspec
import yaml

try:
    import readline  # noqa: F401
except:  # noqa E722
    pass

# ----------------------------------------------------------------------------------------

SRC_DIR = "."

if len(sys.argv) > 1:
    SRC_DIR = sys.argv[1]

if len(sys.argv) > 2:
    target_dir = sys.argv[2]
else:
    target_dir = input("Target Dir: ")

# TODO: argparse for -f etc.

# ----------------------------------------------------------------------------------------

PATHSPEC_IGNORE = ["/.mvn/repository", '/.git', '/target', '/.clouduct*', '/reseed*']

spec = pathspec.PathSpec.from_lines('gitwildmatch', PATHSPEC_IGNORE)


class SimpleLineReplacer:

    def __init__(self, match, replacement=None):
        self.match = match
        self.replacement = replacement

    def replace(self, line):
        return line.replace(self.match, self.replacement)

    def __repr__(self):
        return self.match + " => " + self.replacement


class LinePatcher:

    def __init__(self, gitfilematches):
        self.gitfilematches = gitfilematches
        self.compiled_gitfilematches = map(pathspec.patterns.GitWildMatchPattern, gitfilematches)
        self.replacers = []

    def replacer(self, replacer):
        self.replacers.append(replacer)
        return self

    def __repr__(self):
        return "{} {}".format(self.gitfilematches, self.replacers)


class Reseed:

    def __init__(self, binaries, dir_rename, excludes):
        self.binaries = map(pathspec.patterns.GitWildMatchPattern, binaries)
        self.patchers = []
        self.excludes = map(pathspec.patterns.GitWildMatchPattern, excludes)
        self.dir_rename = dir_rename

    def patcher(self, patcher):
        self.patchers.append(patcher)
        return self

    def __repr__(self):
        return "dir: {}\npatch: {}".format(self.dir_rename, self.patchers.__repr__())


class JavaReseed(Reseed):

    def __init__(self, old_package, new_package, binaries, excludes):
        super().__init__(binaries,
                         SimpleLineReplacer(old_package.replace(".", os.sep), new_package.replace(".", os.sep)),
                         excludes)
        self.patchers.append(LinePatcher(["*"]).replacer(SimpleLineReplacer(old_package, new_package)))


with open(os.path.join(SRC_DIR, ".reseed.yaml")) as file:
    reseed_conf = yaml.load(file)
    old_package = reseed_conf["package"]
    new_package = input("Package name (old: '{}'): ".format(old_package))
    reseed = JavaReseed(old_package, new_package, reseed_conf.get("binary"), reseed_conf.get("exclude"))

    if "patching" in reseed_conf:
        for patch in reseed_conf["patching"]:
            files = patch["files"]
            if type(files) == str:
                files = [files]
            patcher = LinePatcher(files)
            reseed.patcher(patcher)
            for (prompt, old_value) in patch["replacing"].items():
                new_value = input("{}: ".format(prompt))
                patcher.replacer(SimpleLineReplacer(old_value, new_value))

    print(reseed)

sys.exit(0)


def simple_patch_file(file_name, replacers):
    with fileinput.input(files=(file_name), inplace=True) as file:
        for line in file:
            for replacer in replacers:
                line = replacer.replace(line)
            print(line, end='')


replacers = []
dir_replacer = None


def copy_func(src, dst, *, follow_symlinks=True):
    """Copies and patches file.
    """

    renamed_dst = dir_replacer.replace(dst)

    # create parent dir if directory has been renamed
    if renamed_dst != dst:
        renamed_dir = os.path.dirname(renamed_dst)
        if not os.path.exists(renamed_dir):
            os.makedirs(renamed_dir)

    shutil.copy2(src, renamed_dst, follow_symlinks=follow_symlinks)
    try:
        simple_patch_file(renamed_dst, replacers)
    except UnicodeDecodeError:
        # Copy again because fileinput truncates the file.
        # When using fileinput to _copy_ the file, we would need to do the meta attribute handling of the filw ourselves
        shutil.copy2(src, renamed_dst, follow_symlinks=follow_symlinks)


def ignore_func(path, names):
    """Returns files to ignore.
    shutil.copytree calls this function once fore each directory.
    The 'path' parameter contains the directory, the 'names' parameter contains all file names in thet directory.
    copytree expects a set of names to be ignored as return value
    """
    ignored_names = []

    for name in names:
        full_path = os.path.join(path, name)
        if spec.match_file(full_path):
            ignored_names.append(name)

    result2 = set(ignored_names)
    return result2


print(SRC_DIR, "=>", target_dir)

os.chdir(SRC_DIR)

# shutil.copytree(".", target_dir, copy_function=copy_func, ignore=ignore_func)
