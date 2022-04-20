#!/usr/bin/env bash
sudo apt-get update
# Add up to date nodejs sources
curl -sL https://deb.nodesource.com/setup | sudo bash -
wget -qO- https://toolbelt.heroku.com/install-ubuntu.sh | sh

sudo apt-get install -y nodejs ruby ruby-dev git python-pip curl python-virtualenv libpq-dev python-dev postgresql libffi-dev libssl-dev redis-server

sudo npm install -g npm
sudo npm install -g bower
sudo gem install rubygems-update
sudo update_rubygems
sudo gem install compass --version 0.12.7
sudo gem install modular-scale sass
sudo pip install --upgrade pip setuptools distribute
sudo pip install virtualenv

# create databases and user
# mysql -u root -p -e "create database icmo_dev;create database icmo_test;grant all privileges on *.* to 'icmo_dev'@'%' identified by 'cRak3R$';"


sudo -u postgres psql -U postgres -d postgres -c "UPDATE pg_database SET datistemplate=FALSE WHERE datname='template1';"
sudo -u postgres psql -U postgres -d postgres -c "DROP DATABASE template1;"
sudo -u postgres psql -U postgres -d postgres -c "CREATE DATABASE template1 WITH owner=postgres template=template0 encoding='UTF8' lc_collate='en_US.utf8' lc_ctype='en_US.utf8';"
sudo -u postgres psql -U postgres -d postgres -c "UPDATE pg_database SET datistemplate=TRUE WHERE datname='template1';"

sudo -u postgres psql -U postgres -d postgres -c "alter user postgres with password 'root';"

sudo -u postgres psql -U postgres -d postgres -c "CREATE USER icmo_dev WITH PASSWORD 'icmo_dev';"
sudo -u postgres psql -U postgres -d postgres -c "ALTER USER icmo_dev CREATEDB;" #for test database
# sudo -u postgres psql -U postgres -d postgres -c "DROP DATABASE icmo_dev";
sudo -u postgres psql -U postgres -d postgres -c "CREATE DATABASE icmo_dev";
# sudo -u postgres pg_restore -x --no-privileges --no-owner -d icmo_dev /vagrant/db-backup.dump
# sudo -u postgres psql -U postgres -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE icmo_dev to icmo_dev;"
# sudo -u postgres psql -U postgres -d icmo_dev -c "GRANT ALL ON ALL TABLES IN SCHEMA public to icmo_dev;"
# sudo -u postgres psql -U postgres -d icmo_dev -c "GRANT ALL ON ALL SEQUENCES IN SCHEMA public to icmo_dev;"
# sudo -u postgres psql -U postgres -d icmo_dev -c "GRANT ALL ON ALL FUNCTIONS IN SCHEMA public to icmo_dev;"
# sudo -u postgres /vagrant/tools/change_db_owner.sh -o icmo_dev -d icmo_dev


sudo -i -u vagrant virtualenv --no-site-packages --distribute ~/venv; source ~/venv/bin/activate; pip install -r /vagrant/reqs/dev.txt

