# Welcome!

Tramcar is a _multi-site_, _self-hosted_ __job board__ built using
[Django](https://www.djangoproject.com/).  This project is still in its infancy,
but we welcome your involvement to help us get Tramcar ready for production
installs.

## Features

* Host multiple job boards on the same instance using Django's "sites" framework
* Allow free or paid job postings, with paid postings using Stripe Checkout for payment processing
* Automatically tweet job details when a post is activated
* Automatically expire jobs after an admin-defined period
* E-mail notifications alert the admin when a post is made and the job owner when their job has expired
* Job posts support Markdown for creating rich text descriptions and application information
* Send weekly Mailchimp e-mail containing list of jobs posted in last 7 days

## Installation

First, clone and install dependencies.  This requires python 3.5, pip, and
virtualenv to already be installed.

```
$ git clone https://github.com/tramcar/tramcar
$ cd tramcar
$ virtualenv .venv
$ source .venv/bin/activate
(.venv) $ pip install -r requirements.txt
```

Tramcar defaults `SECRET_KEY` in `tramcar/settings.py` to an empty string
which will prevent Django from starting up.  This is done to ensure that
deployers do not accidentally deploy with a default value.  Before proceeding,
set a unique value for `SECRET_KEY` in `tramcar/settings.py`.  If you have `pwgen`
installed, simply do this:

```
$ RANDOM_PWD=$(pwgen -s 50 1)
$ sed -i.bak "s/^SECRET_KEY = ''$/SECRET_KEY = '$RANDOM_PWD'/g" tramcar/settings.py
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
```

The default site has a domain of `example.com`, this will need to be changed to
`localhost` for development testing or to whatever live domain you will be
using in production.  For example, to test Tramcar locally, issue the following
command:

```
(.venv) $ sqlite3 db.sqlite3 "UPDATE django_site SET domain='localhost' WHERE name='example.com';"
```

## Fixtures

We have a fixtures file in `job_board/fixtures/countries.json`, which you can
load into your database by running the following:

```
(.venv) $ python manage.py loaddata countries.json
```

This will save you having to import your own list of countries.  However, be
aware that any changes made to the `job_board_country` table will be lost if
you re-run the above.

## Start Tramcar

To run Tramcar in a development environment, you can now start it using the
light-weight development web server:

```
(.venv) $ python manage.py runserver
```

To run Tramcar using Apache2 and mod_wsgi, see the
[following](https://github.com/tramcar/tramcar/wiki/Production-Deployment-Notes)
for more information.

## Final Steps

At this point, Tramcar should be up and running and ready to be used.  Before
you can create a company and job, log into <http://localhost:8000/admin> using
the username and password defined above.  Once in, click Categories under
JOB_BOARD and add an appropriate category for the localhost site.

That's it!  With those steps completed, you can now browse
<http://localhost:8000> to create a new company, and then post a job with that
newly created company.

(If deploying with a non-localhost domain, replace `localhost` above with
the domain you are using)

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

## Mailshot Automation

If a site has `mailchimp_username`, `mailchimp_api_key`, and `mailchimp_list_id`
set, run the following to create and send a Mailchimp campaign containing a list
of all jobs posted in the last 7 days:

```
(.venv) $ python manage.py send_mailshot
```

Again, cron the above to run once a week so that these campaigns are built and
sent automatically.

If you're unsure what the `mailchimp_list_id` is for the list in question,
populate `mailchimp_username` and `mailchimp_api_key` for the site and then run
the following command to display all lists on this site's MailChimp account:

```
(.venv) $ python manage.py display_lists <site_domain>
```

The value under the ID column for the associated list is what should get
assigned to `mailchimp_list_id`.

## Support

Found a bug or need help with installation?  Please feel free to create an [issue](https://github.com/tramcar/tramcar/issues/new) and we will assist as soon as possible.
