
#!/bin/sh
# install Homebrew

/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

brew update

# install pip

sudo easy_install pip

curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
sudo python get-pip.py

# install dependencies

sudo pip install netifaces --ignore-installed

sudo pip install netaddr --ignore-installed

echo 'Installation Done!'
