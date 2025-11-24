# Website Service

This is the main web interface for the Ultimate Map for Academic Strategy & Success (UMASS) project. It is a monolithic Django project that serves as the primary user-facing application, integrating functionality from various backend microservices.

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
