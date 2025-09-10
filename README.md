# Feetfirst Project

## Overview

Feetfirst is a comprehensive web application designed to manage user accounts, product catalogs, customer inquiries, and onboarding surveys. It provides a robust backend for handling various business processes, including secure authentication, product management, and PDF file uploads.

## Features

-   **User Account Management**: Secure user authentication, authorization, and profile management.
-   **Product Catalog**: Efficiently manage product categories, subcategories, and detailed product information.
-   **Contact Management**: Streamline handling of customer inquiries and contact information.
-   **Survey System**: Create and manage onboarding surveys for users.
-   **PDF File Uploads**: Securely upload, store, and manage PDF documents.

## API Endpoints

The Feetfirst project exposes a set of RESTful APIs to interact with its various functionalities. Below is a consolidated list of the main API endpoints:

### Core Endpoints (`/api/`)

-   `/admin/`: Django Admin interface.
-   `/api/users/`: Includes all user-related API endpoints.
-   `/api/products/`: Includes all product-related API endpoints.
-   `/api/surveys/`: Includes all survey-related API endpoints.
-   `/api/contactus/`: Endpoint for contact inquiries.
-   `/api/token/`: Obtain JWT authentication token.
-   `/api/token/refresh/`: Refresh JWT authentication token.

### Accounts Endpoints (`/api/users/`)

-   `/api/users/`: User list and creation.
-   `/api/users/update/`: Update user profile.
-   `/api/users/reset-password/`: Reset user password.
-   `/api/users/get-otp/`: Get OTP for verification.
-   `/api/users/login/`: User login.
-   `/api/users/logout/`: User logout.
-   `/api/users/signup/`: User registration.
-   `/api/users/verify-otp/`: Verify OTP.
-   `/api/users/google/callback/`: Google OAuth callback.
-   `/api/users/change-password/`: Change user password.
-   `/api/users/addresses/`: List and create user addresses.
-   `/api/users/addresses/<int:pk>/`: Retrieve, update, or delete a specific user address.
-   `/api/users/deletion-request/`: Request account deletion.

### Products Endpoints (`/api/products/`)

-   `/api/products/`: List all products.
-   `/api/products/<int:id>/`: Retrieve a specific product by ID.
-   `/api/products/upload-pdf/`: Upload PDF files related to products.
-   `/api/products/view/`: View product details.

### Surveys Endpoints (`/api/surveys/`)

-   `/api/surveys/onboarding-surveys/`: List and create onboarding surveys.

### Contact Endpoints (`/api/contactus/`)

-   `/api/contactus/`: Handle customer inquiries.

## Setup Instructions

To set up the Feetfirst project locally, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/mhraju69/Feet-First.git
    cd Feetfirst/core
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/Scripts/activate  # On Windows
    # source venv/bin/activate    # On macOS/Linux
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Apply database migrations:**
    ```bash
    python manage.py migrate
    ```

5.  **Create a superuser (for admin access):**
    ```bash
    python manage.py createsuperuser
    ```

6.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```

    The application will be accessible at `http://127.0.0.1:8000/`.

## Docker Setup

This project includes a `Dockerfile` and `docker-compose.yml` for containerized deployment.

1.  **Build Docker images:**
    ```bash
    docker-compose build
    ```

2.  **Run Docker containers:**
    ```bash
    docker-compose up
    ```

    The application will be accessible via the exposed port (usually `8000`).

## Contributing

Contributions are highly welcome! If you'd like to contribute, please follow these steps:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Make your changes and ensure tests pass.
4.  Submit a pull request with a clear description of your changes.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

## Contact

For any inquiries or support, please contact [Your Contact Information/Email].