#!/usr/bin/env bash


# For SSH access to CodeCommit we need the "SSH key ID" which is something cryptic like AJHAJZRYAGZT23ANT3ZQ
# But it is not the Access key ID
# (see https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_ssh-keys.html?icmpid=docs_iam_console#ssh-keys-code-commit)
#
# To get the SSH key ID, we first need to get the user name of the current user (`aws iam get-user`).
#
# The AWS CLI allows to filter its output using: http://jmespath.org/tutorial.html


cd "$(dirname "$0")"

# The remote repository URL
REMOTE_URL=$1

# Get the user name of the IAM user executing this script
#
# $> aws iam get-user
# {
#    "User": {
#        "Path": "/",
#        "UserName": "vivo-admin",
#        ...
#    }
# }
USER=$(aws iam get-user --query "User.UserName" | sed 's/"//g')
echo "USER: ${USER}"

# Get the SSH key ID.
#
# $> aws iam list-ssh-public-keys
# {
#    "SSHPublicKeys": [
#        {
#            "SSHPublicKeyId": "APNJLZRYOYZT81ANT9PQ",
#            "Status": "Active",
#            ...
#        }
#    ]
# }
#
SSH_CODECOMMIT_USER=$(aws iam list-ssh-public-keys --user-name $USER --query 'SSHPublicKeys[?Status==`Active`] | [0].SSHPublicKeyId' | sed 's/"//g' )

REMOTE_URL_WITH_USER=$(echo "$REMOTE_URL" | sed "s%\(ssh://\)\(.*\)$%\1${SSH_CODECOMMIT_USER}@\2%")
echo "$REMOTE_URL_WITH_USER"

test -d .git && rm -rf .git
git init
git remote add origin $REMOTE_URL_WITH_USER
git add -A
git commit -m "initial commit"
git push -u origin master
