# Connect-the-Dots Map Game

A web application for creating and playing 'connect-the-dots' games on custom map backgrounds. This project was developed as part of the [WWW apps course](https://mrd4rkne.github.io/www/) at MIMUW to explore modern web development practices.

## ✨ Features

-   **🗺️ Custom Map Backgrounds**: Upload and manage your own images as game boards via the admin panel.
-   **✍️ Route Creation**: Visually create, manage, and reorder points to define paths on your maps.
-   **🎮 Game Mode**: Play "connect the dots" games based on your custom routes, solo or with others.
-   **🧩 Board Management**: Define and organize multiple game boards.
-   **🔔 Real-Time Updates**: Receive instant notifications (via Server-Sent Events) when new boards or paths are created.

## 🛠️ Tech Stack

-   **Backend**: Django, Django REST Framework
-   **Frontend**: TypeScript, Tailwind CSS
-   **Database**: PostgreSQL
-   **DevOps**: Docker, Azure

## 🚀 Getting Started

### Prerequisites

-   [Docker](https://www.docker.com/get-started)
-   [Docker Compose](https://docs.docker.com/compose/install/)

### Installation

1.  Clone the repository:
    ```bash
    git clone <your-repository-url>
    cd www-webapp
    ```

2.  Build and run the application using Docker Compose:
    ```bash
    docker-compose up --build
    ```
3. Run migrations
    As it is not recommended to automaticcly run migrations on startup (as it kills ability to replicate the app) you must migrations. See `Migrations` below.

4.  Now you can access the application at [http://localhost:8000](http://localhost:8000) and the admin panel at [http://localhost:8000/admin](http://localhost:8000/admin).

#### Migrations
1. Create a virtual environment (optional, for running management commands locally):

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

2. Run migrations inside the running backend container:

    ```bash
    docker-compose exec backend python manage.py migrate
    ```

   This will apply all database migrations.

3. (Optional) Create a superuser for accessing the admin panel:

    ```bash
    docker-compose exec backend python manage.py createsuperuser
    ```