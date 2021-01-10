### Crafts GraphQL API 
Core API for arts/crafts website, extending and customising the [Saleor](https://github.com/mirumee/saleor) (2.11) eCommerce platform.

### Running on Linux:
Running on an EC2 instance (Ubuntu 20.04), I found I needed a few extra packages: libpangocairo-1.0-0 libpango-1.0-0 pango-1.0 libcairo2-dev. With these added, everything ran smoothly, and should do for you too.

Since there isn't a manual installation guide for Saleor on Ubuntu I've written up an updated version of [Neerajgupta2407](https://github.com/neerajgupta2407/saleor_course_resources/blob/master/setup_saleor_core.txt)'s setup guide for Python 3.8:

Initial setup of machine:
```
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get -y upgrade
```
Python:
```
sudo apt-get install python3.8 libpython3.8-dev python3-all-dev
sudo apt install virtualenv postgresql uwsgi libpangocairo-1.0-0 libpango-1.0-0 pango-1.0 libcairo2-dev
sudo apt-get install build-essential python3-dev
```
Node and Node Version Manager:
```
sudo apt install npm

curl https://raw.githubusercontent.com/creationix/nvm/master/install.sh | bash

source ~/.profile 
source ~/.bashrc
nvm install v12
```

Setup directories, and clone code:
```
mkdir -p code/backend
cd code/backend
git clone https://github.com/Luka-Abey/ruthfully-graphql-api
virtualenv -p python3.8 venv
source venv/bin/activate
cd ruthfully-graphql-api
pip install -r requirements.txt
```

Set up a Postgres user:
```
sudo su - postgres
psql

CREATE ROLE saleor WITH LOGIN PASSWORD 'saleor';
CREATE DATABASE saleor;
ALTER USER saleor WITH SUPERUSER;

GRANT ALL PRIVILEGES ON DATABASE saleor TO saleor;
ALTER USER saleor CREATEDB;
```

Export variables:
```
export ALLOWED_HOSTS=<your-public-IP>
export ALLOWED_CLIENT_HOSTS=<your-public-IP>
export DEBUG=True
export SECRET_KEY=<your-secret-key>
export INTERNAL_IPS=127.0.0.1,<your-public-IP>,
export DEFAULT_COUNTRY=UK
export DEFAULT_CURRENCY=GBP
```
Applying migrations, generating dummy data, and creating superuser:
```
python manage.py migrate

python manage.py populatedb
 
python manage.py createsuperuser
```
Run server:
```
python manage.py runserver 0.0.0.0:8000
```
 
### Built With

- [GraphQL](https://graphql.org/), [Apollo Client](https://www.apollographql.com/client), [React](https://reactjs.org/) and [Typescript](https://www.typescriptlang.org/)
- [Braintree Payment Gateway](https://www.braintreepayments.com/)

 By [Mirumee](https://github.com/mirumee) and Luka-Abey
