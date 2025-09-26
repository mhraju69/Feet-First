# Setup Instructions

This document provides detailed instructions on how to set up the Feet First project locally for development and testing.

## Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.8+
- pip (Python package installer)
- Git
- Docker (optional, for containerized development)

## 1. Clone the Repository

First, clone the project repository from your version control system:

```bash
git clone <repository_url>
cd Feetfirst/core
```

## 2. Create a Virtual Environment

It is highly recommended to use a virtual environment to manage project dependencies:

```bash
python -m venv venv
```

### Activate the Virtual Environment

- **Windows:**
  ```bash
  .\venv\Scripts\activate
  ```
- **macOS/Linux:**
  ```bash
  source venv/bin/activate
  ```

## 3. Install Dependencies

Install the required Python packages using pip:

```bash
pip install -r requirements.txt
```

## 4. Environment Variables

Create a `.env` file in the `core` directory (e.g., `c:\Users\Raju\Projects\Feetfirst\core\.env`) and add the following environment variables. Replace the placeholder values with your actual settings:

```
SECRET_KEY='your_secret_key_here'
DEBUG=True
DATABASE_URL='sqlite:///db.sqlite3' # Example for SQLite, use your actual database URL
EMAIL_HOST_USER='your_email@example.com'
EMAIL_HOST_PASSWORD='your_email_password'
# Add any other necessary environment variables
```

## 5. Database Setup

### 5.1. Apply Migrations

Apply the database migrations to create the necessary tables:

```bash
python manage.py migrate
```

### 5.2. Create a Superuser

Create a superuser account to access the Django admin panel:

```bash
python manage.py createsuperuser
```

Follow the prompts to set up your superuser credentials.

## 6. Run the Development Server

Start the Django development server:

```bash
python manage.py runserver
```

The application should now be accessible at `http://127.0.0.1:8000/`.

## 7. Access the Admin Panel

You can access the Django administration panel at `http://127.0.0.1:8000/admin/` using the superuser credentials you created.

## 8. Running Tests

To run the project's test suite:

```bash
python manage.py test
```