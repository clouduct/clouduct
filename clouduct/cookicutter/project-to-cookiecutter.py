import os
import re
from shutil import copyfile

from pathmatch import wildmatch

exclude_dirs = [".git", ".mvn/repository"]

# which kind of project?

# INPUT src directory, target directory
package2path = str.maketrans(".", "/")
path2package = str.maketrans("/", ".")

execute_flag = True

group_id = "ch.mibelle.skincare"
artifact_id = "mibsvc"
package_path = group_id.translate(package2path)

cookiecutter_file = "cookiecutter.json"

src_dir = "/Users/vivo/workspaces/cc/mibelle/mibsvc"
target_dir = "/Users/vivo/workspaces/cc/mibelle/mibsvc-cookiecutter"
cookie_cutter_target_dir = os.path.join(target_dir, "{{ cookiecutter.project_slug }}")

local_gitignore = os.path.join(src_dir, ".gitignore")
global_gitginore = os.path.join(os.path.expanduser("~"), ".gitignore")

gitignore_filter = re.compile(r"^\s*(#.*)?$")


def load_gitignores(gitignore_filename):
    if os.path.exists(gitignore_filename):
        with open(gitignore_filename, 'r') as gitignore_file:
            return [line.rstrip("\n") for line in gitignore_file.readlines() if not gitignore_filter.match(line)]
    return []


ignore = load_gitignores(global_gitginore)
ignore.extend(load_gitignores(local_gitignore))
ignore.extend(exclude_dirs)

pom_file = os.path.join(src_dir, "pom.xml")
if os.path.exists(pom_file):
    pass
else:
    gradle_file = os.path.join(src_dir, "build.gradle")
    if os.path.exists(gradle_file):
        pass

src_main_dir = os.path.join(src_dir, "src", "main")
if os.path.exists(src_main_dir):
    pass

if os.path.exists(target_dir):
    # check --force?
    print("target directory", target_dir, "already exists. stopping")
    # sys.exit(1)


def handle_file(src_dir, target_dir, file):
    pass


os.makedirs(cookie_cutter_target_dir, exist_ok=True)


def path_exclude1(src_dir, dir, exclude_dirs):
    for exd in exclude_dirs:
        if exd.startswith("/"):  # absolute dir
            if os.path.join(src_dir, exd[1:]) == dir:
                return True
        elif dir.endswith(exd):
            return True
    return False


def pathmatch_exclude(src_dir, file_or_dir, ignore):
    rel_path = os.path.relpath(file_or_dir, src_dir)
    result = False
    for pattern in ignore:
        if pattern.startswith("!"):
            if wildmatch.match(pattern[1:], file_or_dir):
                result = False
        elif wildmatch.match(pattern, rel_path):
            result = True
    return result


for root, dirs, files in os.walk(src_dir):
    # We are pruning the list of dirs here: os.walk will only use the remaining dirs to go on
    # (os.walk() lazily 'generates' the files)

    dirs[:] = [d for d in dirs if not pathmatch_exclude(src_dir, os.path.join(root, d), ignore)]

    for file in files:
        src_filename = os.path.join(root, file)
        if not pathmatch_exclude(src_dir, src_filename, ignore):

            rel_dir = os.path.relpath(root, src_dir)
            # print("ROOT: {}\n  REL: {}\n  new_rel_dir: {}".format(root, rel_dir, new_rel_dir))
            if rel_dir != ".":
                new_rel_dir = rel_dir.replace(package_path, "{{cookiecutter.package_path}}")
                new_abs_target_dir = os.path.join(cookie_cutter_target_dir, new_rel_dir)
            else:
                new_abs_target_dir = cookie_cutter_target_dir
            # IF in _copy_without_render?
            #     simply copy
            # ELSE
            if execute_flag:
                os.makedirs(new_abs_target_dir, exist_ok=True)

            target_filename = os.path.join(new_abs_target_dir, file)

            if execute_flag:
                try:
                    with open(src_filename, 'r') as src_file, open(target_filename, 'w') as target_file:
                        for src_line in src_file:
                            target_file.write(src_line.replace(group_id, "{{cookiecutter.package}}"))
                except UnicodeDecodeError:
                    print("probably binary", src_filename, "copying ...")
                    if execute_flag:
                        copyfile(src_filename, target_filename)

if execute_flag:
    copyfile(os.path.join(src_dir, "cookiecutter.json"), os.path.join(target_dir, "cookiecutter.json"))
