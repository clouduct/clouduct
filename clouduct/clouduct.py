#!/usr/bin/env python

#  This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""."""

import git
import os

import clouduct.reseed


def generate(project_name, profile, template, tags, env, execute=False):
    """Generate a new project in AWS."""

    print("CURDIR1:", os.path.realpath(os.path.curdir))
    print("cloning {}".format(template["application"]))
    git.Repo.clone_from(template["application"], ".clouduct-seed", depth=1)
    clouduct.reseed(".clouduct-seed", input={"project_name": project_name})
    print("CURDIR2:", os.path.realpath(os.path.curdir))
    git.Repo.clone_from(template["infrastructure"], "{}-infra".format(project_name), depth=1)

    # clouduct_tf = os.path.join(os.path.dirname(
    #     os.path.dirname(
    #         os.path.dirname(os.path.realpath(__file__)))), "clouduct-bin/clouduct-tf")

    if execute:
        # execute terraform
        pass
    else:
        # terraform plan
        pass
