from ec2_connect import *
from tkinter import Tk
from tkinter.filedialog import askopenfilename

instance_ip = "3.144.33.225"

Tk().withdraw()

pempath = "/home/daniel/Downloads/myawskeys.pem"

ec2client = EC2Connect(pempath, instance_ip)

localfilepath = askopenfilename() 

ec2client.nb_copy_and_start(localfilepath, custom_token="abcdef")

ec2client.close()