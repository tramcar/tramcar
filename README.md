# Welcome!

Tramcar is a _multi-site_, _self-hosted_ __job board__ built using
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

You can now browse http://127.0.0.1:8000/ to access your job board, and
http://127.0.0.1:8000/admin/ to access the admin panel.

## Fixtures

We have a fixtures file in `job_board/fixtures/countries.json`, which you can
load into your database by running the following:

```
(.venv) $ python manage.py loaddata countries.json
```

This will save you having to import your own list of countries.  However, be
aware that any changes made to the `job_board_country` table will be lost if
you re-run the above.

## Job Expiration

Jobs can be expired manually by logging in as an admin user and then clicking
the `Expire` button under `Job Admin` when viewing a given job.  A simpler
solution is to run this instead:

```
(.venv) $ python manage.py expire
```

The above will scan through all jobs across all sites and expire out any jobs
older than the site's `expire_after` value.  Ideally, the above should be
scheduled with cron so that jobs are expired in a consistent manner.
