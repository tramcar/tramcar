# Welcome!

Tramcar is a self-hosted job board built using
[Django](https://www.djangoproject.com/).  This project is still in its infancy,
but we welcome your involvement to help us get Tramcar ready for production
installs.

## Development Installation

First, clone and install dependencies.  This requires python 2.7, pip, and
virtualenv to already be installed.

```
$ git clone https://github.com/wfhio/tramcar
$ cd tramcar
$ virtualenv .venv
$ source .venv/bin/activate
(.venv) $ pip install -r requirements.txt
```

Now, apply database migrations, create an admin user, and start the
development server:

```
(.venv) $ python manage.py migrate
(.venv) $ python manage.py createsuperuser
Username (leave blank to use 'root'): admin
Email address: admin@tramcar.org
Password:
Password (again):
Superuser created successfully.
(.venv) $ python manage.py runserver
```

You can now browse (http://127.0.0.1:8000/) to access your job board, and
(http://127.0.0.1:8000/admin) to access the admin panel.
