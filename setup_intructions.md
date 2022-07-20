# Project Defination / Working Functionality

The are two roles in the system; `LIBRARIAN` and `MEMBER`

### As a User
  - I can signup either as `LIBRARIAN` and `MEMBER` using username and password
  - I can login using username/password and get JWT access token

#### As a Librarian
  - I can add, update, and remove Books from the system
  - I can add, update, view, and remove Member from the system

#### As a Member/Student
  - I can view, borrow, and return available Books
  - Once a book is borrowed, its status will change to `BORROWED`
  - Once a book is returned, its status will change to `AVAILABLE`
  - I can delete my own account



## Dependencies
This project relies mainly on Django. Mainly:
    - Python 3.8+
    - Django 3+ or 4+
    - Django Rest Framework

## Requirements:
    - Create `Virtualenv` to avoid/manage the package/library related mismatch issue
    - As of now I consider default `sqllite3` DB as default but you can install MySQL or PostgreSQL and change the DB configuration from settings.py file of proect
    - I have used Token base system with the help of JWT, so must knowlege of JWT
    - Will create DRF API so must have knowlge of DRF

## Installation before project Setup
1. Virtualenv
2. Python 3.8+ with updated pip version (as of now I considered pip3.9)


## Project Setup Steps
- To manage project in common folder just create one common folder under your workspace directory
- $ mkdir Workspace
- $ cd Workspace
- $ mkdir VirtuENV
- $ mkdir DjangoProjects

## Create a virtual environment to install dependencies in and activate it:
- $ cd Workspace/VirtualENV
- $ virtualenv lib_mgmt_env
- $ source lib_mgmt_env/bin/activate

## The first thing to do is to clone the repository:
- $ cd Workspace/DjangoProjects
- $ git clone https://github.com/true-value-access/django-interview-assignment.git -b feature/library-management-rest
- $ cd django-interview-assignment


## Special files in this repository
```
django-interview-assignment/         - Library Management
|__ authusers -  User Management logic
    |__ migrations -  DB Migrations
        |__ __init__.py -  Constructor
    |__ admin.py -  DB table register
    |__ apps.py -  app related configurations
    |__ __init__.py -  Constructor
    |__ models.py -  DB table architecture classes
    |__ serializers.py -  API related Searializer classes
    |__ tasks.py -  Common asynchronous function but right now only common function without asynchronous logic
    |__ tests.py -  Test cases
    |__ tokens.py -  User Account activatation Hash Generator
    |__ urls.py -  Constructor
    |__ utils.py -  Common/Generic functions
    |__ views.py -  User Account related Business

|__ book_management -  Book Management logic
    |__ migrations -  DB Migrations
        |__ __init__.py -  Constructor
    |__ admin.py -  DB table register
    |__ apps.py -  app related configurations
    |__ __init__.py -  Constructor
    |__ models.py -  DB table architecture classes
    |__ serializers.py -  API related Searializer classes
    |__ tests.py -  Test cases
    |__ urls.py -  Constructor
    |__ views.py -  User Account related Business

|__ LibraryManagement -  Main Project which manage all the stuff related to project logic/requirements
    |__ asgi.py -  ASGI configuration related to project
    |__ __init__.py -  Constructor
    |__ settings.py -  Project related all the settings
    |__ urls.py -  All APIs related to project
    |__ wsgi.py -  WSGI configuration related to project

|__ static -  Whole project relaated static files
    |__ css -  This folder contains all the CSS provided by the designer
    |__ fonts -  This folder contains all the fonts provided by the designer
    |__ images -  This folder contains all the static images provided by the designer
    |__ js -  This folder contains all the js provided by the designer
    |__ lib -  This folder contains all the 3rd party js/css/images/fonts etc static contents

|__ templates -  Whole project related HTML content as static or dynamic with jinja syntax
    |__ lms -  Front end side content management stuff
    |__ account_activation -  HTML for user activation message page/content
        |__ activate.html
    |__ dashboard -  HTML for homepage rendering
        |__ dashboard.html
    |__ emails -  HTML for user account verification email
        |__ user_registration_email.html
    |__ base_footer.html -  Common footer HTML
    |__ base_header.html -  Common header HTML
    |__ base_main.html -  Main HTML
    |__ index.html -  Homepage HTML inherited from base_main.html

|__ assignment-scorecard.md
|__ db.sqlite3 - Project default database
|__ manage.py - project manager file
|__ README.md - Project related defination
|__ requirements.txt- list of dependencies
|__ setup_intructions.md - project setup configuration / instructions

```

## Install the dependencies:
- (lib_mgmt_env)$ pip install -r requirements.txt

**NOTE:** the (lib_mgmt_env) in front of the prompt. This indicates that this terminal session operates in a virtual environment set up by virtualenv.
Once pip has finished downloading the dependencies:

# Migration the table to db
- (lib_mgmt_env)$ python manage.py makemigrations

## Create a development database:
- (lib_mgmt_env)$ python manage.py migrate
- (lib_mgmt_env)$ python manage.py createsuperuser

## Collect static
- (lib_mgmt_env)$ python manage.py collectstatic

## If everything is alright, you should be able to start the Django development server:
- (lib_mgmt_env)$ python manage.py runserver 0.0.0.0:8000

## Open your browser and go to http://127.0.0.1:8000, you will be greeted with a welcome page or homepage.

## NOTE:
    - 43.205.67.206 is belongs with server URL

## For Local:
- Homepage URL: http://127.0.0.1:8000/ or http://43.205.67.206/
- Admin site URL: http://127.0.0.1:8000/admin/ or http://43.205.67.206/admin

## Admin Credentials:
    - Username: admin
    - Password: admin


## Main features
    * User Account management with CRUD
    * Lirarian & Member as Role management
    * Example app with custom user model
    * Bootstrap static files included
    * User, Librarian registration and logging in as demo
    * Procfile for easy deployments
    * Separated requirements files
    * SQLite by default if no env variable is set
