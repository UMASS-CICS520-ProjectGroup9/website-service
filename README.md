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

To run this service:

1.  Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2.  Run the development server:
    ```bash
    cd website
    python manage.py runserver
    ```
