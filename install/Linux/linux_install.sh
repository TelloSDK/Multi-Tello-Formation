#!/bin/sh
sudo apt-get update -y

# install python 2.7
sudo apt-get install python2.7 python-pip -y
sudo pip install --upgrade pip

#switch to python2.7
sudo update-alternatives --install /usr/bin/python python /usr/bin/python2 150 
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3 100

sudo apt-get update -y


# install dependencies
sudo pip install netifaces
sudo pip install netaddr

echo 'Installation Done!'
