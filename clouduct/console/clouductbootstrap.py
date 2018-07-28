#!/usr/bin/env python

"""Command Line Interface for 'clouduct'."""

import urllib.request

import boto3
import click
import click_completion
import yaml

import clouduct

click_completion.init(complete_options=True)

profiles = boto3.session.Session().available_profiles

template_names = ["blah-1.0", "foo-1.0"]
# templates = json.load(open("templates.json"))
# template_names = [template["name"] + "-" + template["version"] for template in templates]

environments = ["dev", "test", "prod"]

TEMPLATES_CONFIG = "https://raw.githubusercontent.com/clouduct/clouduct-cli/master/clouduct-templates.yaml"


@click.group(help)
def completion():
    """Needed for click_completion."""
    pass


@completion.command()
# @click.option('--execute', is_flag=True,
#               help='clouduct will only show the execution plan unless you give this flag')
@click.option('--profile', type=click.Choice(profiles),
              help='One of your locally configured AWS profiles (see'
                   ' https://docs.aws.amazon.com/cli/latest/userguide/cli-multiple-profiles.html)')
@click.option('--template', "template_key", type=click.Choice(template_names),
              help='The template your new project will be based on'
                   ' (see https://clouduct.org/templates.html)')
@click.option('--templates-config',
              help='A URL where that returns a list of templates (either as text or as application/json)')
@click.option('--tag', 'tags', multiple=True, metavar='<key>:<value>',
              help='Tag for the created resources: <key>:<value> (can be provided multiple times)')
# @click.option('--env', default='dev', type=click.Choice(environments),
#               help='Default: "dev".\n'
#                    'The kind of environment you want to create (used for naming and tagging). Some'
#                    ' templates create different kind/sizes of resources based on this parameter'
#                    ' (if you are not sure, do not set this param)')
@click.argument('project_name')
def create(project_name, profile, templates_config=TEMPLATES_CONFIG, template_key=None, tags={}):
    """Generate an initial project on AWS based on a template.

    The CodeCommit repo will be named NAME and all other resources will contain
    NAME as well to be easily identifiable.
    """
    if profile:
        print("profile:", profile)

    if templates_config:

        with urllib.request.urlopen(templates_config) as resource:
            templates = yaml.load(resource)

            template = None

            if template_key is not None:
                template = templates.get(template_key)
            elif template_key is None and len(templates.keys()) == 1:
                (template_key, template), = templates.items()

    clouduct.generate(project_name, profile, template, tags, "dev")


def verify_prerequisites():
    """Check for terraform."""
    pass


def main():
    verify_prerequisites()
    create()


if __name__ == '__main__':
    verify_prerequisites()
    create()
