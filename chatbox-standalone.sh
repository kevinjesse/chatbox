#!/bin/bash
cd 
git clone https://github.com/kevinjesse/chatbox.git
cd ./chatbox
git fetch
git checkout standalone

sudo rm -rf /var/www/html/
sudo cp -rf ~/chatbox/frontend/* /var/www/

sudo apt-get update
sudo apt-get install apache

sudo apt-get install python-software-properties
sudo add-apt-repository ppa:ondrej/php
sudo apt-get update
sudo apt-get install -y php7.0

sudo /etc/init.d/apache2 start
cd ~/chatbox/backend

