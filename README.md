
# Website Service

This is the main web interface for the Ultimate Map for Academic Strategy & Success (UMASS) project. It is a modular Django project serving as the primary user-facing application, integrating functionality from various backend microservices.


## Python Version and Environment

- Python 3.10+ (tested with Django 5.2)
- Install dependencies from `requirements.txt`; use a virtual environment (`python -m venv .venv && source .venv/bin/activate`).
- Default SQLite database for local development (`website/db.sqlite3`).


## Project Structure

```
website-service/
├── assets/                # CSS and static assets
├── docs/                  # Sphinx documentation (source, build, test report)
│   ├── source/            # .rst files, conf.py, all_tests_report.html
│   └── build/html/        # Generated HTML docs
├── requirements.txt       # Python dependencies
├── pytest.ini             # Pytest configuration
├── website/               # Main Django project directory
│   ├── base/              # Core app: main views, templates
│   ├── courses/           # Courses app: models, views, urls, tests
│   ├── professors/        # Professors app: models, views, urls, tests
│   ├── discussions/       # Discussions app: models, views, urls, tests
│   ├── events/            # Events app: models, views, urls, tests
│   ├── myworkplace/       # Personalized dashboard app
│   ├── static/            # Static assets (images, js, styles, webfonts)
│   ├── templates/         # Shared and per-app HTML templates
│   │   └── pages/         # Subfolders for each app (authentication, courses, etc.)
│   └── manage.py          # Django management script
└── README.md
```

Each app contains:
- `models.py` — Data models
- `views.py` — View logic
- `urls.py` — URL routing
- `tests.py` — Unit/integration tests
- `templates/pages/<app>/` — App-specific templates
- `static/` — App-specific static files (if any)


## Service Integration

This service acts as an orchestrator, making API calls to backend microservices to fetch data and present it to the user. It connects to:
- `account-service`: User profile management
- `courses-service`: Course data
- `discussions-service`: Discussion threads and posts
- `events-service`: Event details
- `userauthen-service`: User authentication and authorization


## Features

- Landing page with recent posts and navigation
- Course browsing (lists, details, search)
- Professor browsing (lists, details, ratings)
- Discussion forum (threads, details, creation forms)
- Events listing, detail, search, sorting, create/update/delete with external API calls
- Personalized “My Workplace” dashboard
- User registration, login, and logout (via userauthen-service)


## Getting Started

1. **Run a backend service** (e.g., courses-service):
   ```bash
   cd ../courses-service/coursesService
   pip install -r ../requirements.txt
   python manage.py migrate
   python manage.py loaddata fixtures/initial_data.json
   python manage.py runserver
   ```
   (Runs on `http://127.0.0.1:8000/`)

2. **Run the website-service**:
   ```bash
   cd website
   pip install -r ../requirements.txt
   python manage.py runserver 8001
   ```
   (Access at [http://127.0.0.1:8001/](http://127.0.0.1:8001/))

**Note:** For full functionality, run all backend microservices on different ports.


## Testing

- Each app has its own `tests.py` for unit and integration tests
- Run all tests from the repo root:
    ```bash
    pytest
    ```
- Django settings are wired via `pytest.ini` (`DJANGO_SETTINGS_MODULE=website.settings`)
- HTML test report is generated and included in Sphinx docs (`docs/source/all_tests_report.html`)


## Documentation

- Sphinx documentation is in `docs/`
- Source files: `docs/source/`
- Build HTML: `docs/build/html/`
- To build docs:
    ```bash
    cd docs
    make html
    ```
- Open `docs/build/html/index.html` in your browser


## Authentication

- Authentication is handled by the `userauthen-service` (URL configurable in Django settings; default: `http://127.0.0.1:9111`)
    - `POST /api/register/` for sign-up
    - `POST /api/token/` for login
- Access and refresh tokens are stored in the Django session (`access_token`, `refresh_token`, `email`, `user_id`, `role`)
- Login-required flows (e.g., event creation/update) redirect to `login` if not authenticated
