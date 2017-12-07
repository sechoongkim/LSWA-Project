#!/bin/bash

sudo apt-get update -y
sudo apt-get install gcc -y
sudo apt-get install git -y
sudo apt-get install python-dev python-pip -y
sudo apt-get install apache2 apache2-dev -y
sudo apt-get install libmysqlclient-dev -y
sudo apt-get install python-virtualenv -y
sudo apt-get install python3-dev
sudo apt-get install python3-setuptools -y
sudo easy_install3 pip -y

export DEBIAN_FRONTEND=noninteractive
sudo apt-get -q -y install mysql-server -y

sudo mkdir /home/ubuntu/tmp
sudo chmod -R 777 /home/ubuntu/tmp

# In working dir
wget https://github.com/GrahamDumpleton/mod_wsgi/archive/4.4.13.tar.gz
tar xzvf 4.4.13.tar.gz
cd mod_wsgi-4.4.13/
./configure
make
sudo make install
# Enable the module
sudo sh -c "echo 'LoadModule wsgi_module /usr/lib/apache2/modules/mod_wsgi.so' > /etc/apache2/mods-available/wsgi.load"
sudo a2enmod wsgi
sudo service apache2 restart
make clean

# Prepare the directory structure.
sudo mkdir /var/www/site
sudo mkdir /var/www/site/static
# Logs (this is a bad location for permanant logs).
touch /tmp/db.debug.log
chmod 777 /tmp/db.debug.log

cd /var/www/site
# Get the source code.
sudo git clone https://github.com/WilliamTsao/LSWA-Project.git depot
cd depot
sudo git checkout new-deployment
sudo ./first_install.sh
cd db
sudo curl -sSL https://get.docker.com/ | sh
source ./run_docker_dbs.sh
start_docker_dbs
sudo ./install_db.sh
cd ../../
source depot/env/bin/activate
sudo mv depot/web/ web/
cd web
sudo python3 manage.py makemigrations streeTunes
python3 manage.py migrate --database auth_db
python3 manage.py migrate --database db1
python3 manage.py migrate --database db2
sudo python3 manage.py collectstatic --noinput

# Use the following config.
cat <<EOF > /etc/apache2/sites-available/web.conf
WSGIDaemonProcess web python-path=/var/www/site/web:/var/www/site/depot/env/lib/python3.5/site-packages
WSGIProcessGroup web
<Directory /var/www/site/web/web>
  <Files wsgi.py>
    Require all granted
  </Files>
</Directory>

Alias /static/ /var/www/site/static/
<Directory /var/www/site/static>
  Require all granted
</Directory>

EOF
sudo a2ensite web
sudo service apache2 reload
# We should be able to serve now.
