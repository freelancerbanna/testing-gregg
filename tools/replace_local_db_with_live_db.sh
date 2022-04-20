#!/bin/bash
heroku pg:backups capture --app instelligentcmo-staging
curl -o /vagrant/data/latest.dump `heroku pgbackups:url --app intelligentcmo-staging`
sudo -u postgres psql -U postgres -d postgres -c "DROP DATABASE icmo_dev";
sudo -u postgres psql -U postgres -d postgres -c "CREATE DATABASE icmo_dev";
sudo -u postgres pg_restore -x --no-privileges --no-owner -d icmo_dev /vagrant/data/latest.dump
sudo -u postgres psql -U postgres -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE icmo_dev to icmo_dev;"
sudo -u postgres psql -U postgres -d icmo_dev -c "GRANT ALL ON ALL TABLES IN SCHEMA public to icmo_dev;"
sudo -u postgres psql -U postgres -d icmo_dev -c "GRANT ALL ON ALL SEQUENCES IN SCHEMA public to icmo_dev;"
sudo -u postgres psql -U postgres -d icmo_dev -c "GRANT ALL ON ALL FUNCTIONS IN SCHEMA public to icmo_dev;"
sudo -u postgres /vagrant/tools/change_db_owner.sh -o icmo_dev -d icmo_dev
