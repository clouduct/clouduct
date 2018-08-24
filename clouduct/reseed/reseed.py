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

PATHSPEC_IGNORE = ["/.mvn/repository", '/.git', '/target', '/.clouduct*', '/reseed*']

spec = pathspec.PathSpec.from_lines('gitwildmatch', PATHSPEC_IGNORE)


class SimpleLineReplacer:

    def __init__(self, match, replacement):
        self.match = match
        self.replacement = replacement

    def replace(self, line):
        return line.replace(self.match, self.replacement)

    def __repr__(self):
        return self.match + " => " + self.replacement


class Reseed:

    def __init__(self, src_dir, target_dir=None, config_file=None, input={}, force=False):
        self.src_dir = src_dir
        self.input = input
        self.target_dir = target_dir
        self.replacers = []
        self.dir_replacer = None
        self.force = force
        if config_file is None:
            self.config_file = ".clouduct-reseed"
        else:
            self.config_file = config_file

        with open(os.path.join(self.src_dir, self.config_file), "r") as file:
            data = yaml.load(file, yaml.Loader)
            for (name, old_value) in data.items():
                if type(old_value) == dict:
                    (old_value, new_value), = old_value.items()
                    self.input[name] = new_value.format(**self.input)
                new_value = self.ask(name)
                self.input[name] = new_value

                self.replacers.append(SimpleLineReplacer(old_value, new_value))
                if name == 'package':
                    self.dir_replacer = SimpleLineReplacer(old_value.replace('.', os.sep),
                                                           new_value.replace('.', os.sep))
                if self.target_dir is None and name == 'artifactid':
                    self.target_dir = os.path.join("..", new_value)

    def ask(self, prompt):
        if prompt in self.input:
            print("  # {}: {}".format(prompt, self.input[prompt]))
            return self.input[prompt]
        else:
            return input("  {}: ".format(prompt))

    def simple_patch_file(self, file_name, replacers):
        with fileinput.input(files=(file_name), inplace=True) as file:
            for line in file:
                for replacer in replacers:
                    line = replacer.replace(line)
                print(line, end='')

    def copy_func(self):
        def _copy_func(src, dst, *, follow_symlinks=True):
            """Copies and patches file.
            """

            renamed_dst = self.dir_replacer.replace(dst)

            # create parent dir if directory has been renamed
            if renamed_dst != dst:
                renamed_dir = os.path.dirname(renamed_dst)
                if not os.path.exists(renamed_dir):
                    os.makedirs(renamed_dir)

            shutil.copy2(src, renamed_dst, follow_symlinks=follow_symlinks)
            try:
                self.simple_patch_file(renamed_dst, self.replacers)
            except UnicodeDecodeError:
                # Copy again because fileinput truncates the file.
                # When using fileinput to _copy_ the file, we would need to do the meta attribute handling
                # of the file ourselves
                shutil.copy2(src, renamed_dst, follow_symlinks=follow_symlinks)

        return _copy_func

    def ignore_func(self):
        def _ignore_func(path, names):
            """Returns files to ignore.
            shutil.copytree calls this function once fore each directory.
            The 'path' parameter contains the directory, the 'names' parameter contains all file names in the directory.
            copytree expects a set of names to be ignored as return value
            """
            ignored_names = []

            for name in names:
                full_path = os.path.join(path, name)
                if spec.match_file(full_path):
                    ignored_names.append(name)

            result2 = set(ignored_names)
            return result2

        return _ignore_func

    def reseed(self):
        print(self.src_dir, "=>", self.target_dir.replace("../", ""))
        current_dir = os.path.realpath(os.path.curdir)
        os.chdir(self.src_dir)
        shutil.copytree(".", self.target_dir, copy_function=self.copy_func(), ignore=self.ignore_func())
        os.chdir(current_dir)


def reseed(src_dir, input={}, target_dir=None, config_file=None, force=False):
    Reseed(src_dir, target_dir, config_file, input).reseed()


if __name__ == "__main__":
    SRC_DIR = "."

    if len(sys.argv) > 1:
        SRC_DIR = sys.argv[1]

    if len(sys.argv) > 2:
        target_dir = sys.argv[2]

    # TODO: argparse for -f etc.

    reseed(SRC_DIR)
