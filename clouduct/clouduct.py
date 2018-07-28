#!/usr/bin/env python

#  This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""."""

import git

import clouduct.reseed


def generate(project_name, profile, template, tags, env, execute=False):
    """Generate a new project in AWS."""

    print("cloning {}".format(template["application"]))
    git.Repo.clone_from(template["application"], ".clouduct-seed", depth=1)
    clouduct.reseed(".clouduct-seed", input={"project_name": project_name})

    # replace placeholders

    if execute:
        # execute terraform
        pass
    else:
        # terraform plan
        pass
