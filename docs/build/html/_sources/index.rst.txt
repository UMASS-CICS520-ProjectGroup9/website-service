website-service documentation
============================

Welcome to the documentation for the website-service Django project.

Overview
--------
This project is a modular Django web application for academic strategy and success, including account, courses, professors, events, discussions, and authentication services.

Setup
-----
1. Install dependencies:
   ::
      pip install -r requirements.txt

2. Apply migrations:
   ::
      python manage.py migrate

3. Run the development server:
   ::
      python manage.py runserver

Usage
-----
- Access the web app at http://localhost:8000/
- Log in or register for an account.
- Explore courses, professors, events, and discussions.

Testing
-------
See the :doc:`testing` page for test instructions and reports.

Project Structure
-----------------
- accountService/: Account management
- coursesService/: Courses and enrollment
- professorsService/: Professors and ratings
- eventsService/: Events and calendar
- discussionsService/: Discussions and forums
- userauthen/: User authentication
- website/: Main Django project

API & App Documentation
-----------------------
*Add more .rst files for each app as needed and include them below.*

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   testing

