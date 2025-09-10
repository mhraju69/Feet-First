# Feetfirst Project

## Project Overview

Feetfirst is a robust web application built with Django and Django REST Framework, designed to provide a comprehensive backend solution for managing various aspects of a business, including user accounts, product information, customer contacts, and surveys. It leverages a modular architecture, with distinct applications for different functionalities, ensuring scalability and maintainability.

## Features

-   **User Account Management**: Secure user authentication and authorization.
-   **Product Catalog**: Manage product categories, subcategories, and product details.
-   **Contact Management**: Handle customer inquiries and contact information.
-   **Survey System**: Create and manage onboarding surveys for users.
-   **PDF File Uploads**: Securely upload and manage PDF files.

## Technologies Used

-   **Backend**: Django, Django REST Framework
-   **Database**: (Assumed, typically PostgreSQL or SQLite for development)
-   **Task Queue**: Celery (indicated by `celery.py` and `celerybeat-schedule`)
-   **Containerization**: Docker, Docker Compose
-   **API Testing**: Postman (indicated by Postman collection files)

## Setup Instructions

To get the Feetfirst project up and running on your local machine, follow these steps:

### Prerequisites

-   Docker and Docker Compose installed.
-   Python 3.x (if running without Docker).
-   pip (Python package installer).

### Using Docker (Recommended)

1.  **Clone the repository**:
    ```bash
    git clone <repository_url>
    cd Feetfirst
    ```

2.  **Build and run Docker containers**:
    ```bash
    docker-compose up --build
    ```
    This command will build the Docker images, set up the necessary services (web, database, Celery), and start the application. The application will typically be accessible at `http://localhost:8000`.

3.  **Apply migrations**:
    Once the containers are running, you might need to apply database migrations. You can do this by executing a command inside the web service container:
    ```bash
    docker-compose exec web python manage.py migrate
    ```

4.  **Create a superuser (optional)**:
    To access the Django admin panel, create a superuser:
    ```bash
    docker-compose exec web python manage.py createsuperuser
    ```
    Follow the prompts to create your superuser account.

### Local Setup (Without Docker)

1.  **Clone the repository**:
    ```bash
    git clone <repository_url>
    cd Feetfirst/core
    ```

2.  **Create a virtual environment**:
    ```bash
    python -m venv env
    .env\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Apply migrations**:
    ```bash
    python manage.py migrate
    ```

5.  **Run the development server**:
    ```bash
    python manage.py runserver
    ```
    The application will be accessible at `http://127.0.0.1:8000/`.

## API Endpoints

The project exposes several API endpoints through Django REST Framework:

-   `/api/accounts/`: User authentication and management.
-   `/api/contact/`: Contact form submission.
-   `/api/products/`: Product listings, details, categories, and subcategories.
-   `/api/surveys/`: User survey submission.
-   `/api/files/upload/`: PDF file uploads.

(Note: Specific endpoint paths may vary based on `urls.py` configurations within each app.)

## Usage

Interact with the API using tools like Postman or `curl`. Refer to the Postman collection files in the `postman/` directory for example requests.

## Project Structure

```
Feetfirst/
├── core/                 # Main Django project and applications
│   ├── Accounts/         # User authentication and profiles
│   ├── Contact/          # Contact form and inquiries
│   ├── Products/         # Product catalog and management
│   ├── Surveys/          # User onboarding surveys
│   ├── core/             # Django project settings, URLs, WSGI, ASGI
│   ├── Dockerfile        # Dockerfile for the web application
│   ├── manage.py         # Django management script
│   ├── requirements.txt  # Python dependencies
│   └── README.md         # This file
├── env/                  # Python virtual environment
├── postman/              # Postman collection and environment files
└── docker-compose.yml    # Docker Compose configuration
```

## Contributing

Contributions are welcome! Please fork the repository and submit pull requests.

## License

This project is licensed under the MIT License.