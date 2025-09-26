# API Reference

This section provides a comprehensive reference for all API endpoints available in the Feet First project.

## Base URL

The base URL for all API endpoints is `http://127.0.0.1:8000/api/v1/` (or your deployed domain).

## Authentication

All API endpoints require token-based authentication. To authenticate, include your authentication token in the `Authorization` header of your requests:

`Authorization: Token <your_auth_token>`

## Endpoints

### Accounts

#### `POST /api/v1/accounts/register/`

- **Description**: Registers a new user.
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "securepassword123",
    "name": "John Doe",
    "phone": "+1234567890"
  }
  ```
- **Response**:
  ```json
  {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "phone": "+1234567890",
    "token": "<generated_auth_token>"
  }
  ```

#### `POST /api/v1/accounts/login/`

- **Description**: Authenticates a user and returns an authentication token.
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "securepassword123"
  }
  ```
- **Response**:
  ```json
  {
    "token": "<generated_auth_token>"
  }
  ```

#### `GET /api/v1/accounts/me/`

- **Description**: Retrieves the authenticated user's profile.
- **Authentication**: Required.
- **Response**:
  ```json
  {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "phone": "+1234567890",
    "role": "customer",
    "is_active": true,
    "date_joined": "2023-01-01T12:00:00Z"
  }
  ```

### Products

#### `GET /api/v1/products/`

- **Description**: Retrieves a list of all products.
- **Authentication**: Optional.
- **Response**:
  ```json
  [
    {
      "id": 1,
      "name": "Running Shoe",
      "price": "99.99",
      "main_category": "Shoes",
      "sub_category": "Running",
      "gender": "Unisex",
      "is_active": true
    }
  ]
  ```

#### `GET /api/v1/products/<id>/`

- **Description**: Retrieves details of a specific product.
- **Authentication**: Optional.
- **Response**:
  ```json
  {
    "id": 1,
    "name": "Running Shoe",
    "description": "Comfortable running shoes for all terrains.",
    "price": "99.99",
    "stock_quantity": 100,
    "main_category": "Shoes",
    "sub_category": "Running",
    "gender": "Unisex",
    "brand": "Nike",
    "is_active": true,
    "colors": ["Red", "Blue"],
    "sizes": ["US 7", "US 8"]
  }
  ```

### Surveys

#### `POST /api/v1/surveys/onboarding/`

- **Description**: Submits an onboarding survey for the authenticated user.
- **Authentication**: Required.
- **Request Body**:
  ```json
  {
    "discovery_question": ["Social Media"],
    "product_preference": "Running Shoes",
    "foot_problems": "Flat feet"
  }
  ```
- **Response**:
  ```json
  {
    "id": 1,
    "user": 1,
    "discovery_question": ["Social Media"],
    "product_preference": "Running Shoes",
    "foot_problems": "Flat feet",
    "created_at": "2023-01-01T12:00:00Z"
  }
  ```

### Contact

#### `POST /api/v1/contact/`

- **Description**: Submits a contact inquiry.
- **Authentication**: Optional.
- **Request Body**:
  ```json
  {
    "name": "Jane Doe",
    "email": "jane.doe@example.com",
    "subject": "Inquiry about product X",
    "message": "I have a question about..."
  }
  ```
- **Response**:
  ```json
  {
    "id": 1,
    "name": "Jane Doe",
    "email": "jane.doe@example.com",
    "subject": "Inquiry about product X",
    "message": "I have a question about...",
    "created_at": "2023-01-01T12:00:00Z"
  }
  ```

This API reference is a starting point and should be expanded with more details for each endpoint, including possible error responses, query parameters, and more complex examples as the project evolves.