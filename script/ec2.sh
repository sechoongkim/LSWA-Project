#!/bin/bash

apt-get update -y
apt-get install gcc -y
apt-get install git -y
# apt-get install python-dev python-pip -y
apt-get install apache2 apache2-dev -y
apt-get install libmysqlclient-dev -y
apt-get install python-virtualenv -y
apt-get install python3-dev -y
apt-get install python3-setuptools -y
easy_install3 pip

export DEBIAN_FRONTEND=noninteractive
apt-get -q -y install mysql-server -y

mkdir /home/ubuntu/tmp
chmod -R 777 /home/ubuntu/tmp

# In working dir
wget https://github.com/GrahamDumpleton/mod_wsgi/archive/4.5.22.tar.gz
tar xzvf 4.5.22.tar.gz
cd mod_wsgi-4.5.22/
./configure --with-python=python3.4
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
git checkout new-deployment
./first_install.sh
cd db
curl -sSL https://get.docker.com/ | sh
source ./run_docker_dbs.sh
start_docker_dbs
for (( i = 1 ; i <= 60 ; i++ )); do
  sleep 1
./install_db.sh
cd ../../
source depot/env/bin/activate
mv depot/web/web web
cd web
python3 manage.py makemigrations
python3 manage.py migrate --database auth_db
python3 manage.py migrate --database db1
python3 manage.py migrate --database db2
python3 manage.py collectstatic --noinput

# Use the following config.
cat <<EOF > /etc/apache2/sites-available/web.conf
WSGIScriptAlias / /var/www/site/web/web/wsgi.py
WSGIDaemonProcess web python-path=/var/www/site/web:/var/www/site/depot/env/lib/python2.7/site-packages
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
a2ensite web
service apache2 reload
# We should be able to serve now.
