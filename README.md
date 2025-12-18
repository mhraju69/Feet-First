# Feetfirst Project

## Overview

Feetfirst is a comprehensive web application designed to manage user accounts, product catalogs, customer inquiries, and onboarding surveys. It provides a robust backend for handling various business processes, including secure authentication, product management, and PDF file uploads.

## ✨ Key Features

### 👤 User Management
- **Secure Authentication**: JWT token-based authentication with email/password and Google OAuth
- **OTP Verification**: Secure account verification via one-time passwords
- **Password Management**: Reset, change, and recover passwords
- **Profile Management**: Update user details, addresses, and preferences
- **Account Security**: Deletion requests and suspension handling

### 👟 Product Catalog
- **Multi-level Categorization**: Main categories and subcategories
- **Advanced Filtering**: By size, color, gender, brand, and price
- **Product Matching**: AI-powered foot scan matching with percentage scores
- **Size Recommendations**: Personalized sizing based on foot scans
- **Favorites System**: Save and manage favorite products
- **PDF Specifications**: Technical documentation uploads and downloads

### 🦶 Foot Scanning
- **Scan Analysis**: Detailed foot measurements (length, width, arch index)
- **Size Conversion**: Automatic size recommendations across brands
- **Excel Reports**: Download detailed scan reports
- **Product Matching**: Algorithm to find best-fitting footwear

### 🔍 Discovery Features
- **Smart Suggestions**: Recommended products based on scans and preferences
- **Q&A Matching**: Find products matching user questionnaire answers
- **Viewing History**: Track recently viewed products

### 📊 Surveys & Engagement
- **Onboarding Surveys**: Customizable user preference questionnaires
- **Contact System**: Customer inquiry management
- **Feedback Collection**: Gather user experience data

### 🛠️ Admin Features
- **Django Admin**: Comprehensive backend management
- **Content Management**: Add/edit products, categories, and specifications
- **User Management**: View and manage all user accounts
- **Analytics**: Track system usage and engagement

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
-   `/api/users/addresses/int:pk/`: Retrieve, update, or delete a specific user address.
-   `/api/users/deletion-request/`: Request account deletion.

### Products Endpoints (`/api/products/`)

-   `/api/products/`: List all products.
-   `/api/products/int:id/`: Retrieve a specific product by ID.
-   `/api/products/upload-pdf/`: Upload PDF files related to products.
-   `/api/products/view/`: View product details.
-   `/api/products/favorites/`: View favourite products.
-   `/api/products/footscans/`: View footscan details.
-   `/api/products/qna-match/`: View QnA match products .
-   `/api/products/footscan/download/`: Download footscan details as exel.
-   `/api/products/suggestions/int:product_id/`: View suggestion products.


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