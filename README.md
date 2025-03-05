# ssh_key_setup
A Python script to Set Up SSH Passwordless Login Automatically

## Prerequisites
1. Make sure OpenSSH is installed (Run `ssh -v`)
2. Install python3.5+
3. pip install paramiko

## Usage:

user@localhost%>> python3 ./ssh_key_setup.py  remote_username@remote_hostname

If the SSH port is not the default 22:

user@localhost%>> python3 ./ssh_key_setup.py --port 1234 remote_username@remote_hostname
