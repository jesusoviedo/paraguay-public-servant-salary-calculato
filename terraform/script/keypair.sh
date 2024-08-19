#!/usr/bin/env bash
SSH_KEY_PASSPHRASE=$KEY_PASSPHRASE
SSH_EMAIL=$EMAIL

ssh-keygen -t rsa -b 4096 -C "${SSH_EMAIL}" -f .ssh/aws-key-par-paraguay-public-servan -N "${SSH_KEY_PASSPHRASE}"
