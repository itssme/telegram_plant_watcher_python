import setuptools
import os
import subprocess


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


if os.getuid() != 0:
    print(Colors.FAIL + "[!] please run this program as root for installation" + Colors.ENDC)
    quit(1)

print(Colors.OKGREEN + "[!] installing python3-systemd via apt" + Colors.ENDC)
child = subprocess.Popen(["apt-get", "install", "python3-systemd", "-y"])
streamdata = child.communicate()[0]
rc = child.returncode

if rc != 0:
    print(Colors.FAIL + "[!] failed to run apt install python3-systemd")
    quit(1)

print(Colors.OKGREEN + "[!] installed python3-systemd successfully" + Colors.ENDC)

print(Colors.OKGREEN + "[!] installing python-telegram-bot via pip3" + Colors.ENDC)
child = subprocess.Popen(["pip3", "install", "python-telegram-bot"])
streamdata = child.communicate()[0]
rc = child.returncode

if rc != 0:
    print(Colors.FAIL + "[!] failed to run pip3 install python-telegram-bot")
    quit(1)

print(Colors.OKGREEN + "[!] installed python-telegram-bot successfully" + Colors.ENDC)

print(Colors.OKGREEN + "[!] creating working directory in /home/plant_watcher" + Colors.ENDC)
child = subprocess.Popen(["mkdir", "/home/plant_watcher", "--parent"])
streamdata = child.communicate()[0]
rc = child.returncode

if rc != 0:
    print(Colors.FAIL + "[!] failed create directory /home/plant_watcher")
    quit(1)

child = subprocess.Popen(["chmod", "777", "/home/plant_watcher"])
streamdata = child.communicate()[0]
rc = child.returncode

if rc != 0:
    print(Colors.FAIL + "[!] failed to change permissions of working directory" + Colors.ENDC)
    quit(1)

print(Colors.OKBLUE + "[!] Type in your bot token for telegram" + Colors.ENDC)

service_file_writer = open(os.path.dirname(os.path.abspath(__file__)) + "/plant_watcher.service", "w")

service_file = """[Unit]
Description=Monitoring service
[Service]
ExecStart=/usr/bin/python3 """ + os.path.dirname(os.path.abspath(__file__)) + """/main.py
Environment="PYTHONUNBUFFERED=1"
Environment="take_picture=12h00m"
Environment="bot_token=""" + input("?: ") + """"
Environment="working_dir=/home/plant_watcher"
Environment="debug=False"
Restart=on-failure
Type=notify
[Install]
WantedBy=default.target"""

service_file_writer.write(service_file)
service_file_writer.close()

child = subprocess.Popen(["cp", "plant_watcher.service", "/etc/systemd/system/plant_watcher.service"])
streamdata = child.communicate()[0]
rc = child.returncode

if rc != 0:
    print(Colors.FAIL + "[!] failed to move service file to systemd directory" + Colors.ENDC)
    quit(1)

child = subprocess.Popen(["chown", "root:root", "/etc/systemd/system/plant_watcher.service"])
streamdata = child.communicate()[0]
rc = child.returncode

if rc != 0:
    print(Colors.FAIL + "[!] failed to change owner of service file to root " + Colors.ENDC)
    quit(1)

child = subprocess.Popen(["chmod", "644", "/etc/systemd/system/plant_watcher.service"])
streamdata = child.communicate()[0]
rc = child.returncode

if rc != 0:
    print(Colors.FAIL + "[!] failed to change permissions of service file" + Colors.ENDC)
    quit(1)

base_dir = os.path.dirname(__file__)
readme_path = os.path.join(base_dir, "readme.md")
if os.path.exists(readme_path):
    with open(readme_path) as stream:
        long_description = stream.read()
else:
    long_description = ""

setuptools.setup(
    name="plant_watcher",
    version="0.0.1",
    author="itssme",
    author_email="itssme3000@gmail.com",
    description="Python bot that sends images of my plant to me in telegram",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/itssme/plant_watcher",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
)
