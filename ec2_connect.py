from io import StringIO
import boto3, paramiko, time, os, io

class EC2Connect():
    """A class that provides utility functions to work with an EC2 instance"""

    def __init__(self, path_to_pem, instance_ip, username = "ubuntu"):
        self.client = self.open_ssh_client(path_to_pem = path_to_pem, instance_ip = instance_ip, username = username)
        self.pempath = path_to_pem
        self.instance_ip = instance_ip


    def open_ssh_client(self, path_to_pem, instance_ip, username):
        #opens a connection to an EC2 instance using paramiko
        f = open(path_to_pem)
        s = f.read()
        keyfile = io.StringIO(s)
        key = paramiko.RSAKey.from_private_key(keyfile)
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=instance_ip, username = username, pkey = key)
        return client

    def execute_commands(self, cmds, print_output = True, print_error = True):
        for cmd in cmds:
            stdin, stdout, stderr = self.client.exec_command(cmd)
            time.sleep(0.1)
            if print_output:
                print(stdout.read())
            if print_error:
                print(stderr.read())

    def put_to_remote(self, localpath, remotepath):
        #copies a file from localpath to the remotepath (on the EC2 instance)
        ftp_client = self.client.open_sftp()
        ftp_client.put(localpath, remotepath)
        ftp_client.close()

    def get_from_remote(self, remotepath, localpath):
        #copies a file from the remotepath to the localpath
        ftp_client = self.client.open_sftp()
        ftp_client.get(remotepath, localpath)
        ftp_client.close()

    def execute_bash_on_remote(self, bash_path):
        #bash_path is the path to a local bash script, which is copied and executed on the EC2 instance
        self.put_to_remote(bash_path, "/tmp/script.sh")
        self.execute_commands(["chmod +x /tmp/script.sh", "bash /tmp/script.sh"])

    def nb_copy_and_start(self, localfilepath, custom_token):
        self.put_to_remote(localfilepath, "/home/ubuntu/notebook/test.ipynb")
        self.execute_commands(["cd /home/ubuntu/notebook", "jupyter notebook --no-browser --port=8080 --NotebookApp.token="+custom_token])
        os.system("ssh -i "+self.pempath+" -N -L 8080:localhost:8080 "+"ubuntu@"+self.instance_ip)
        print("Jupyter notebook now running on EC2 instance, accessible via http://localhost:8080, token = " + custom_token)

    def close(self):
        self.client.close()