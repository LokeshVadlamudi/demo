#! /bin/bash

# update apt-get packages
sudo apt-get update -y

# Install gunicorn3
sudo apt-get install -y gunicorn3

# Install supervisor
sudo apt-get install -y supervisor

# Install nginx
sudo apt-get install -y nginx

# Install python3-pip
sudo apt-get install -y python3-pip

# Pip install using the requirements.txt file
sudo pip3 install -r requirements.txt

# Copy configuration files
# Updating gunicorn conf in supervisor
sudo cp /home/ubuntu/sp20-cmpe-202-sec-49-team-project-fourreal/conf.d/gunicorn.conf /etc/supervisor/conf.d

# Updating nginx and django conf in nginx
sudo cp /home/ubuntu/sp20-cmpe-202-sec-49-team-project-fourreal/conf.d/django.conf /etc/nginx/sites-available
sudo cp /home/ubuntu/sp20-cmpe-202-sec-49-team-project-fourreal/conf.d/nginx.conf /etc/nginx/nginx.conf
sudo ln -s /etc/nginx/sites-available/django.conf /etc/nginx/sites-enabled/django.conf

# Update the supervisor and nginx configuration
sudo supervisorctl reread
sudo supervisorctl update
sudo nginx -s reload