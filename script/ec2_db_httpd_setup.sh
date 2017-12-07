#!/bin/bash

sudo apt-get update -y
sudo apt-get install gcc -y
sudo apt-get install git -y
sudo apt-get install python-dev python-pip -y
sudo apt-get install apache2 apache2-dev -y
sudo apt-get install libmysqlclient-dev -y
sudo apt-get install python-virtualenv -y

sudo export DEBIAN_FRONTEND=noninteractive
sudo apt-get -q -y install mysql-server -y

sudo mkdir /home/ubuntu/tmp
sudo chmod -R 777 /home/ubuntu/tmp

# In working dir
sudo wget https://github.com/GrahamDumpleton/mod_wsgi/archive/4.4.13.tar.gz
sudo tar xzvf 4.4.13.tar.gz
cd mod_wsgi-4.4.13/
sudo ./configure
make
make install
# Enable the module
sh -c "echo 'LoadModule wsgi_module /usr/lib/apache2/modules/mod_wsgi.so' > /etc/apache2/mods-available/wsgi.load"
a2enmod wsgi
service apache2 restart
make clean

# Prepare the directory structure.
mkdir /var/www/site
mkdir /var/www/site/static
# Logs (this is a bad location for permanant logs).
touch /tmp/db.debug.log
chmod 777 /tmp/db.debug.log

cd /var/www/site
# Get the source code.
git clone https://github.com/WilliamTsao/LSWA-Project.git depot
cd depot
git checkout deployment
./first_install.sh
cd db
./install_db.sh
cd ../
source env/bin/activate
cd web
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput

# Use the following config.
cat <<EOF > /etc/apache2/sites-available/streeTunes.conf
WSGIScriptAlias / /var/www/site/depot/web/web/wsgi.py
WSGIDaemonProcess streeTunes python-path=/var/www/site/depot/web:/var/www/site/depot/env/lib/python3.0/site-packages
WSGIProcessGroup streeTunes
<Directory /var/www/site/web>
  <Files wsgi.py>
    Require all granted
  </Files>
</Directory>

Alias /static/ /var/www/site/static/
<Directory /var/www/site/static>
  Require all granted
</Directory>

EOF
a2ensite streeTunes
service apache2 reload
# We should be able to serve now.
