import os
import paramiko
import argparse
import getpass

def connect_to_server(hostname, username, password, port=22):
    """Establish an SSH connection to the remote server."""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, port=port, username=username, password=password)
    return ssh

def read_remote_file(ssh, remote_path):
    """Read a file from the remote server."""
    try:
        sftp = ssh.open_sftp()
        with sftp.open(remote_path, 'r') as remote_file:
            content = remote_file.read()
        sftp.close()
        return content.decode('utf-8')
    except Exception as e:
        print(f"reading file: {e} {remote_path}")
        return None
    
def append_remote_file(ssh, remote_path, content):
    """Write data to a file on the remote server."""
    try:
        sftp = ssh.open_sftp()
        # create the dir if it doesn't exist 
        ssh.exec_command(f"mkdir -p $(dirname {remote_path})")

        # create the file if it doesn't exist
        with sftp.open(remote_path, 'a') as remote_file:
            remote_file.write(content)
        sftp.close()
        print(f"File written successfully to {remote_path}")
    except Exception as e:
        print(f"Error writing file: {e} {remote_path}")


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="SSH Setup Script")
    parser.add_argument("--port", help="SSH port (default is 22)", type=int, default=22)
    parser.add_argument("--password", help="Password for SSH login")
    parser.add_argument("--public_key", help="Path to public key file")
    parser.add_argument("destination", help="Username and hostname in the format username@hostname")
    args = parser.parse_args()

    destination = args.destination.split('@')
    if len(destination) != 2:
        print("Invalid destination format. Use username@hostname.")
        exit(1)    

    username, hostname = destination
    if args.password:
        password = args.password
    else:
        password = getpass.getpass(prompt="Enter SSH password: ")

    # find the public key in the local machine, default is ~/.ssh/id_rsa.pub
    local_key_path = args.public_key or "~/.ssh/id_rsa.pub"
    local_key_path = os.path.expanduser(local_key_path)
    if not os.path.exists(local_key_path):
        print(f"Public key file not found: {local_key_path}")
        create_key = input("Do you want to generate a new key pair? (y/n): ")
        if create_key.lower() == 'y':
            local_key_path = local_key_path.replace(".pub", "")
            os.system(f"ssh-keygen -t rsa -b 4096 -f {local_key_path} -N ''")
            local_key_path = local_key_path + ".pub"
            print(f"RSA key pair generated. Public key path: {local_key_path}") 
        else:
            exit(1)

    # validate the public key
    public_key = open(local_key_path).read().strip()
    if not public_key.startswith("ssh-rsa"):
        print("Invalid public key format. Please check the file.")
        exit(1)
    
    # find remote authorized_keys path, relative to the user's home directory
    authorized_keys_path = f".ssh/authorized_keys"

    # append the public key to the remote authorized_keys file
    ssh_client = connect_to_server(hostname, username, password, port=args.port)
    home_dir = ssh_client.exec_command("echo $HOME")[1].read().strip().decode('utf-8')
    authorized_keys_path = f"{home_dir}/{authorized_keys_path}"

    # check if the public key is already in the authorized_keys file
    file_content = read_remote_file(ssh_client, authorized_keys_path)

    if not file_content or public_key not in file_content:
        append_remote_file(ssh_client, authorized_keys_path, "\n" + public_key + "\n")
    else:
        print("Public key already exists in the authorized_keys file.")

    # Close the SSH connection
    ssh_client.close()