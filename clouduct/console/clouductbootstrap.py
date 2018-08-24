#!/usr/bin/env python

"""Command Line Interface for 'clouduct'."""

import os
import sys
import urllib.request

import boto3
import click
import click_completion
import yaml

import clouduct


def click_completion_match_incomplete(choice, incomplete):
    return incomplete in choice


click_completion.init(match_incomplete=click_completion_match_incomplete, complete_options=True)

profiles = boto3.session.Session().available_profiles

DEFAULT_TEMPLATES_CONFIG = \
    "https://raw.githubusercontent.com/clouduct/clouduct-bootstrap/master/clouduct-templates.yaml"

# print(default_template_names)

environments = ["dev", "test", "prod"]


def template_names():
    argx = sys.argv

    # command line completion
    COMMANDLINE = os.environ.get("COMMANDLINE")
    if COMMANDLINE:  # zsh only
        argx = COMMANDLINE.split(" ")
    COMP_WORDS = os.environ.get("COMP_WORDS")
    if COMP_WORDS:  # bash only
        argx = COMP_WORDS.split("\t")

    try:
        tmpix = argx.index("--templates-config")
        templates_config = argx[tmpix + 1]
    except ValueError:
        templates_config = DEFAULT_TEMPLATES_CONFIG
    try:
        templates_config = templates_config.strip('\'"')
        with urllib.request.urlopen(templates_config) as resource:
            templates = yaml.load(resource)
        return list(templates.keys())
        # TODO: Caching
    except ValueError as err:
        click.echo("HERE", file=sys.stderr, err=True)
        click.echo(err, file=sys.stderr, err=True)
        sys.exit(1)
    except Exception as err:
        click.echo(err, file=sys.stderr, err=True)
        sys.exit(1)


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
@click.option('--template', "template_key", type=click.Choice(template_names()),
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
def create(project_name, profile, templates_config=None, template_key=None, tags={}):
    """Generate an initial project on AWS based on a template.

    The CodeCommit repo will be named NAME and all other resources will contain
    NAME as well to be easily identifiable.
    """
    if profile:
        print("profile:", profile)

    if templates_config is None:
        templates_config = DEFAULT_TEMPLATES_CONFIG
    with urllib.request.urlopen(templates_config) as resource:
        templates = yaml.load(resource)

        template = None

        if template_key is not None:
            template = templates.get(template_key)
            if template is None:
                print("Could not find template {} in {}".format(template_key, templates_config))
                sys.exit(1)
        elif template_key is None:
            if len(templates.keys()) == 1:
                (template_key, template), = templates.items()
            else:
                print("template name missing {}. Should be one of {}".format(template_key, list(templates.keys())))
                sys.exit(1)

    clouduct.generate(project_name, profile, template, tags, "dev")


def verify_prerequisites():
    """Check for terraform."""
    pass


def main():
    create()


if __name__ == '__main__':
    print("sys.argv", sys.argv, file=sys.stderr)
    verify_prerequisites()
    create()
