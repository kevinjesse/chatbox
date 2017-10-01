# chatbox
**To install Chatbox Standalone**

Checkout Repo:

        git clone https://github.com/kevinjesse/chatbox.git
        git checkout -b standalone

For Ubuntu:

        Install Apache:
          sudo apt-get update
          sudo apt-get install apache2

        Install PHP 7.0:
          sudo apt-get install python-software-properties
          sudo add-apt-repository ppa:ondrej/php
          sudo apt-get update
          sudo apt-get install -y php7.0

        Checkout chatbox offline repo:
          check out chatbox-standalone and put in ~/

        Copy frontend code for apache:
          sudo rm -rf /var/www/html/
          sudo cp -r ~/chatbox-offline/frontend/* /var/www/

        Start Apache server:
          sudo /etc/init.d/apache2 start

        Run server.py:
          cd ~/chatbox-offline/backend
          python server.py

        Go to webpage:
          localhost/chatbox.php

For Windows:

        
 
This page will function just like the movie recommendation but stop before recommending movies since it
cannot access the database.


  
