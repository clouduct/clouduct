#!/usr/bin/env python

#  This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""."""

import git
import os
import shutil

import clouduct.reseed

SEED_DIR = ".clouduct-seed"
CLOUDUCT_TF_FILE = "clouduct-bin/clouduct-tf"
INFRA_CONFIG_FILE = ".clouduct-tf"

def generate(project_name, profile, template, tags, env, region, seed_config = None, execute=False):
    """Generate a new project in AWS."""

    print("cloning {}".format(template["application"]))
    if os.path.exists(SEED_DIR):
        shutil.rmtree(SEED_DIR)
    git.Repo.clone_from(template["application"], SEED_DIR, depth=1)
    if seed_config is None:
        seed_config = {}
    seed_config["project_name"] = project_name
    clouduct.reseed(SEED_DIR, input=seed_config)
    infra_dir_name = "{}-infra".format(project_name)
    git.Repo.clone_from(template["infrastructure"], infra_dir_name, depth=1)

    # when installed, clouduct-tf should be at ../../clouduct-bin/clouduct-tf relative to _this_ file
    clouduct_tf_fullpath = os.path.join(os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.realpath(__file__)))), CLOUDUCT_TF_FILE)

    # when running locally, clouduct-tf should be at "clouduct-bin/clouduct-tf
    if not os.path.exists(clouduct_tf_fullpath):
        clouduct_tf_fullpath = CLOUDUCT_TF_FILE
    os.chmod(clouduct_tf_fullpath, 0o774)
    shutil.copy(clouduct_tf_fullpath, infra_dir_name)

    # create terraform config file
    config = {}
    config["TF_VAR_project_name"] = project_name
    config["TF_VAR_region"] = region
    clouduct_config_file = os.path.join(infra_dir_name, INFRA_CONFIG_FILE)
    with open(clouduct_config_file, "w") as file:
        for (key, value) in config.items():
            print("{}={}".format(key, value), file=file)

    if execute:
        # execute terraform
        pass
    else:
        # terraform plan
        pass
