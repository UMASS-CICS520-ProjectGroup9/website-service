# Website Service

This is the main web interface for the Ultimate Map for Academic Strategy & Success (UMASS) project. It is a monolithic Django project that serves as the primary user-facing application, integrating functionality from various backend microservices.

## Python Version and Environment

- Python 3.10+ (tested with Django 5.2)
- Install dependencies from `requirements.txt`; use a virtual environment (`python -m venv .venv && source .venv/bin/activate`).
- Default SQLite database for local development (`website/db.sqlite3`).

## Application Structure & Pages

The `website-service` is organized into several Django apps, each responsible for a specific feature set and rendering a collection of pages:

*   **`base`**: Core application views and templates, including the main `index.html`.
*   **`courses`**: Handles displaying course information.
    *   Pages: Course lists, course details, search forms, and tables for displaying course data.
*   **`professors`**: Manages professor information.
    *   Pages: Professor lists, individual professor pages with ratings, and tables.
*   **`discussions`**: Powers the community discussion forum.
    *   Pages: List of discussions, detailed view of a discussion thread, and forms for creating new discussions.
*   **`events`**: Displays event information.
    *   Pages: Event listings, single event details, and forms for creating and updating events.
*   **`myworkplace`**: Provides a personalized workspace for students.
    *   Pages: A dashboard that includes tables for a user's selected courses, professors, discussions, and events.
*   **`authentication`**: Manages user login and registration pages.

## Service Integration

This service acts as an orchestrator, making API calls to the backend microservices to fetch data and present it to the user. It connects to:

*   `account-service`: For user profile management.
*   `courses-service`: To get course data.
*   `discussions-service`: For discussion threads and posts.
*   `events-service`: To retrieve event details.
*   `userauthen-service`: For user authentication and authorization.

## All Features

- Landing page with recent posts and navigation to all modules.
- Course browsing (lists, details, search).
- Professor browsing (lists, details, ratings).
- Discussion forum (threads, details, creation forms).
- Events listing, detail, search, sorting, create/update/delete with external API calls.
- Personalized “My Workplace” dashboard assembling a user’s selected items.
- User registration, login, and logout backed by the user authentication microservice.

## Getting Started

This service provides the user interface and depends on the various backend microservices for data. To see it in action, you should run at least one backend service (like `courses-service`) and then run this `website-service`.

### Step 1: Run a Backend Service (Example: Courses)

In a separate terminal, start the `courses-service`:

1.  Navigate to the `courses-service` directory:
    ```bash
    cd ../courses-service/coursesService
    ```
2.  Install dependencies and run the service:
    ```bash
    pip install -r ../requirements.txt
    python manage.py migrate
    python manage.py loaddata fixtures/initial_data.json
    python manage.py runserver
    ```
    This will typically run on `http://127.0.0.1:8000/`.

### Step 2: Run the Website Service

In a new terminal, start the `website-service`:

1.  Navigate to the `website` directory inside `website-service`:
    ```bash
    cd website
    ```
2.  Install the dependencies:
    ```bash
    pip install -r ../requirements.txt
    ```
3.  Run the development server on a different port (e.g., 8001):
    ```bash
    python manage.py runserver 8001
    ```

### Step 3: Access the Application

You can now access the website at [http://127.0.0.1:8001/](http://127.0.0.1:8001/). The "Courses" page should now be populated with data from the `courses-service`.

**Note:** For full functionality, you will need to run all the backend microservices, each on a different port.

## Testing

- Unit tests use `pytest` and `pytest-django`.
- Run all tests from the repo root:
  ```bash
  pytest
  ```
- Django settings are wired via `pytest.ini` (`DJANGO_SETTINGS_MODULE=website.settings`).

## Project Structure

Key directories and files:

- `website/website/` – Django project settings, URLs, WSGI/ASGI.
- `website/base/` – Landing/auth pages and shared templates.
- `website/events/` – Event listing, detail, search, create/update/delete views.
- `website/courses/`, `website/professors/`, `website/discussions/`, `website/myworkplace/` – Feature modules for their respective domains.
- `templates/` – Shared templates and page layouts.
- `static/` – Static assets.
- `pytest.ini` – Pytest configuration.
- `requirements.txt` – Python dependencies.

## Authentication

- Authentication delegates to `userauthen-service` at `http://127.0.0.1:9111`:
  - `POST /api/register/` for sign-up.
  - `POST /api/token/` for login.
- Access and refresh tokens are stored in the Django session (`access_token`, `refresh_token`), along with `email`, `user_id`, and `role`.
- Login-required flows (e.g., event creation/update) redirect to `login` when no session token is present.
