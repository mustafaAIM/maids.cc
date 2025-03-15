# MAIDS Project Documentation

## Introduction

When I applied for this job, I understood that any framework would be acceptable. However, upon opening the quiz, I was surprised to discover that it specifically required Spring Boot. Despite this requirement, I decided to build the project using Django, leveraging my expertise with this framework.

This documentation provides a comprehensive guide to understanding, setting up, and running the MAIDS project. If you're interested in how I structured and built this Django project instead of using Spring Boot, I would greatly appreciate your feedback.

## Project Overview

MAIDS appears to be with the following components:

- Books management
- Patron management
- Borrowing management
- Authentication system

The project follows modern Django and software development best practices, including:

- Modular settings following the Two Scoops of Django recommendations
- Docker containerization for easy deployment
- RESTful API using Django REST Framework
- JWT-based authentication
- Internationalization support

## Project Structure

```
maids/
├── apps/                                   # Django applications
│ ├── authentication/                       # User authentication
│ ├── books/                                # Book management
│ ├── patrons/                              # Patron management
│ ├── borrowings/                           # Borrowing management
│ └── core/                                 # Core functionality
├── maids/                                  # Main project configuration
│ └── settings/                             # Modular settings
│ ├──── base.py                             # Base settings
│ └──── dev.py                              # Development settings
├── media/                                  # User-uploaded files
├── static/                                 # Static files
├── locale/                                 # Internationalization files
├── logs/                                   # Application logs
├── docker-compose.yml                      # Docker Compose configuration
├── Dockerfile                              # Docker configuration
├── entrypoint-django.sh                    # Docker entrypoint script
├── manage.py                               # Django command-line utility
└── requirements.txt                        # Python dependencies
```

## How to Run the Project

### Prerequisites

- Docker and Docker Compose installed on your system

### Setup and Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd maids.cc
   ```

2. **Start the application with Docker Compose**
   ```bash
   docker-compose up -d
   ```
3. **Verify the application is running**
   - The Django application will be available at: http://localhost:8000
   - PgAdmin will be available at: http://localhost:5051

## Accessing the Database

The project uses PostgreSQL as its database with the following configuration:

### Direct Database Access

- **Database Name**: maids
- **Username**: maids_developer
- **Password**: moustafa@123
- **Host**: localhost (when accessing from outside Docker)
- **Port**: 5432

### Using PgAdmin

For a graphical interface to the database:

1. Access PgAdmin in your browser at http://localhost:5051
2. Login with:

   - Email: admin@example.com
   - Password: admin

3. Add a new server:
   - Name: MAIDS Database (or any name you prefer)
   - Host: maids_db (use this name within Docker network)
   - Port: 5432
   - Database: maids
   - Username: maids_developer
   - Password: moustafa@123

### Database Schema

The database schema includes tables for:

- Users/Authentication
- Books
- Patrons
- Borrowings

## To run unit tests :

1. **Running tests**

   ```bash
   docker exec -it maids_app python manage.py test
   ```

2. **Running tests in specific app**
   ```bash
   docker exec -it maids_app python manage.py test apps.<app_name>.tests
   ```

## Additional Information

- The project uses Django REST Framework for API development
- Authentication is handled using JWT (JSON Web Tokens)
- The application supports internationalization with translations in the `locale` directory
- Logs are stored in the `logs` directory
- Redis is included for caching.

## API Response Format

### Overview

The MAIDS API follows RESTful principles with a standardized JSON response format for both successful operations and error handling. The API is designed to provide consistent, predictable responses that include status indicators, messages, and appropriate data or error details.

### Response Structure

All API responses follow this standardized structure:

```json
{
  "success": true|false,
  "message": "Human-readable message",
  "status_code": 200,
  "data": {...},         // Present only in successful responses with data
  "errors": {...}        // Present only in error responses
}
```

### Success Responses

Successful responses include:

- `success: true` - Indicates successful operation
- `message` - A descriptive message about the operation
- `status_code` - HTTP status code (typically 200, 201, etc.)
- `data` - The requested resource or operation result

Example of a successful response when fetching a book:

```json
{
  "success": true,
  "message": "Book retrieved successfully",
  "status_code": 200,
  "data": {
    "id": 1,
    "title": "Django for Professionals",
    "author": "William S. Vincent",
    "isbn": "978-1983172663",
    "published_date": "2019-04-25",
    "quantity": 5
  }
}
```

### Error Responses

Error responses include:

- `success: false` - Indicates operation failure
- `message` - A descriptive error message
- `status_code` - HTTP status code (400, 401, 403, 404, 500, etc.)
- `errors` - Detailed error information, which may include field-specific validation errors

Example of a validation error response:

```json
{
  "success": false,
  "message": "Validation error occurred",
  "status_code": 400,
  "errors": {
    "title": ["This field is required."],
    "isbn": ["ISBN must be a valid format."]
  }
}
```

Example of a resource not found error:

```json
{
  "success": false,
  "message": "Resource not found",
  "status_code": 404,
  "errors": {
    "detail": "Not found"
  }
}
```

### Exception Handling System

The project implements a comprehensive exception handling system that captures and properly formats various error scenarios:

#### Custom Exception Classes

The system defines several custom exception types:

- `ValidationError` - For data validation failures (400)
- `NotFoundError` - For resource not found situations (404)
- `PermissionDeniedError` - For authorization failures (403)
- `ConflictError` - For resource conflicts (409)
- `ThrottledError` - For rate limiting (429)

All these exceptions extend a `BaseCustomException` class that ensures consistent error handling.

#### Global Exception Handler

A custom exception handler intercepts all exceptions raised during request processing:

- DRF validation errors maintain their field-specific details but conform to the standard format
- Http404 exceptions are reformatted with friendly messages
- All other exceptions are captured and presented in a consistent format

This ensures that the API never returns raw error messages and always maintains the defined response structure.

## Internationalization Support

The MAIDS project includes robust internationalization (i18n) support, enabling the API to respond in multiple languages based on client preferences.

### Language Selection Middleware

The project implements a custom `APILanguageMiddleware` that intelligently selects the appropriate language for each API response using the following priority:

1. **HTTP Accept-Language Header**: The middleware first checks if the client has specified preferred languages in the request header

   ```
   Accept-Language: ar,en
   ```

2. **Query Parameter**: If the header is not present or not usable, the middleware checks for a `lang` query parameter
   ```
   GET /api/books?lang=ar
   ```

### How to Use Internationalization

#### As an API Consumer

You can receive API responses in your preferred language by:

- Setting the `Accept-Language` header in your API requests

  ```
  "Accept-Language: ar"
  ```

- Adding a `lang` query parameter to the URL

  ```
  http://localhost:8000/api/books/1/?lang=ar
  ```

- Translation strings marked in the code using `gettext_lazy` as `_`
- Translation files stored in the `locale/` directory
- Support for multiple languages including error messages, validation errors, and response messages

Example of how messages are translated in the code:

```python
from django.utils.translation import gettext_lazy as _

error_message = _("Resource not found")
```

## Authentication API

The MAIDS API provides a secure JWT-based authentication system. The authentication endpoints handle user registration, login, token refresh, and logout operations.

### API Endpoints

#### Base URL: `/api/`

```table
| Endpoint       | Method | Description                               |
| --------------- | ------ | ----------------------------------------- |
| `register/`     | POST   | Register a new user account               |
| `login/`        | POST   | Authenticate a user and obtain JWT tokens |
| `refresh/`      | POST   | Refresh an expired access token           |
```
### User Registration

Create a new user account.

**Endpoint:** `POST /api/register/`

**Request Body:**

```json
{
    "email": "librarian@library.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "librarian",
    "password": "SecurePassword123!",
    "confirm_password": "SecurePassword123!"
}
```

**Success Response (201 Created):**

```json
{
	"success": true,
	"message": "User registered successfully",
	"status_code": 201,
	"data": {
		"id": 1,
		"email": "librarian@library.com",
		"first_name": "John",
		"last_name": "Doe",
		"role": "librarian",
		"is_librarian": true,
		"date_joined": "2025-03-14T14:20:06.735397Z",
		"is_active": true
	}
}
```

**Error Response (400 Bad Request):**

```json
{
	"success": false,
	"message": "Validation error occurred",
	"status_code": 400,
	"errors": {
		"email": [
			"user with this Email Address already exists."
		]
	}
}
```

### User Login

Authenticate a user and obtain JWT tokens.

**Endpoint:** `POST /api/login/`

**Request Body:**

```json
{
	"email":"librarian@library.com",
	"password":"SecurePassword123!"
}
```

**Success Response (200 OK):**

```json
{
	"success": true,
	"message": "Login successful",
	"status_code": 200,
	"data": {
		"refresh": "access_token",
		"access": "refresh_token",
		"user_id": 1,
		"email": "librarian@library.com",
		"full_name": "John Doe",
		"role": "librarian",
		"is_librarian": true
	}
}
```

**Error Response (401 Unauthorized):**

```json
{
	"success": false,
	"message": "Invalid credentials",
	"status_code": 401
}
```

### Token Refreshing

Refresh an expired access token using a valid refresh token.

**Endpoint:** `POST /api/refresh/`

**Request Body:**

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Success Response (200 OK):**

```json
{
	"success": true,
	"message": "Token refreshed successfully",
	"status_code": 200,
	"data": {
		"access": "access_token",
		"refresh": "refresh_token"
	}
}
``` 

**Error Response (401 Unauthorized):**

```json
{
	"success": false,
	"message": "{'detail': ErrorDetail(string='Token is invalid or expired', code='token_not_valid'), 'code': ErrorDetail(string='token_not_valid', code='token_not_valid')}",
	"status_code": 401,
	"errors": {
		"detail": "Token is invalid or expired",
		"code": "token_not_valid"
	}
}
```


### Authentication in API Requests

Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...

```

### Token Lifespan

- Access tokens are valid for 15 minutes
- Refresh tokens are valid for 24 hours

After the access token expires, use the refresh token to obtain a new access token without requiring the user to log in again.
```
## Books API

The Books API provides endpoints for managing books in the library system. It allows creating, retrieving, updating, and deleting book records.
### API Endpoints

#### Base URL: `/api/books/`

```| Endpoint        | Method | Description                          | Authorization Required |
|-----------------|--------|--------------------------------------|------------------------|
| `/`             | GET    | List all books with pagination       | No                     |
| `/`             | POST   | Create a new book                    | Yes (Librarian)        |
| `/{id}/`        | GET    | Retrieve details of a specific book  | No                     |
| `/{id}/`        | PUT    | Update a book's details              | Yes (Librarian)        |
| `/{id}/`        | DELETE | Delete a book                        | Yes (Librarian)        |
```
### List Books

Retrieve a paginated list of all books.

**Endpoint:** `GET /api/books/`


**Success Response (200 OK):**

```json
{
	"success": true,
	"message": "Books retrieved successfully",
	"status_code": 200,
	"data": [
		{
			"id": 2,
			"title": "Book One",
			"author": "Shobinhour",
			"isbn": "1234568978942",
			"publication_year": null,
			"is_available": true
		},
		{
			"id": 4,
			"title": "Book One",
			"author": "Shobinhour",
			"isbn": "1234568978943",
			"publication_year": 2024,
			"is_available": true
		},
		{
			"id": 3,
			"title": "Book One Test PUT",
			"author": "Author One Test PUT",
			"isbn": "1112233344453",
			"publication_year": null,
			"is_available": false
		}
	]
}
```

### Create a Book

Add a new book to the library collection.

**Endpoint:** `POST /api/books/`

**Authorization:** Bearer Token (Librarian role required)

**Request Body:**

```json
{
	"title":"Book One",
	"author":"Shobinhour",
	"isbn":"1234568978941",
	"available_copies": 1,
  "total_copies": 6,
	"publisher": "publisher-1",
	"description":"some descriotion",
	"publication_year": 2024
}
```

**Success Response (201 Created):**

```json
{
	"success": true,
	"message": "Book created successfully",
	"status_code": 201,
	"data": {
		"id": 5,
		"title": "Book One",
		"author": "Shobinhour",
		"isbn": "1234568978941",
		"publication_year": 2024,
		"publisher": "publisher-1",
		"description": "some descriotion",
		"available_copies": 6,
		"total_copies": 6,
		"is_available": true,
		"created_at": "2025-03-15T16:03:24.269561Z",
		"updated_at": "2025-03-15T16:03:24.269577Z"
	}
}
```

**Error Response (400 Bad Request):**

```json
{
	"success": false,
	"message": "Validation error occurred",
	"status_code": 400,
	"errors": {
		"isbn": [
			"Book with this ISBN already exists."
		],
		"total_copies": [
			"Ensure this value is greater than or equal to 0."
		]
	}
}
```

**Error Response (403 Forbidden):**

```json
{
  "success": false,
  "message": "Permission denied",
  "status_code": 403,
  "errors": {
    "detail": "You do not have permission to perform this action"
  }
}
```

### Retrieve a Book

Get detailed information about a specific book.

**Endpoint:** `GET /api/books/{id}/`

**Success Response (200 OK):**

```json
{
	"success": true,
	"message": "Book details retrieved successfully",
	"status_code": 200,
	"data": {
		"id": 5,
		"title": "Book One",
		"author": "Shobinhour",
		"isbn": "1234568978941",
		"publication_year": 2024,
		"publisher": "publisher-1",
		"description": "some descriotion",
		"available_copies": 6,
		"total_copies": 6,
		"is_available": true,
		"created_at": "2025-03-15T16:03:24.269561Z",
		"updated_at": "2025-03-15T16:03:24.269577Z"
	}
}
```

**Error Response (404 Not Found):**

```json
{
	"success": false,
	"message": "Resource not found",
	"status_code": 404,
	"errors": {
		"detail": "Not found"
	}
}
```

### Update a Book

Update information for an existing book.

**Endpoint:** `PUT /api/books/{id}/`

**Authorization:** Bearer Token (Librarian role required)

**Request Body:**

```json
{
	"title":"Book One",
	"author":"Shobinhour",
	"isbn":"1234568978941",
	"available_copies": 1,
  "total_copies": 21,
	"publisher": "publisher-1",
	"description":"some descriotion",
	"publication_year": 2024
}
```

**Success Response (200 OK):**

```json
{
	"success": true,
	"message": "Book updated successfully",
	"status_code": 200,
	"data": {
		"id": 5,
		"title": "Book One",
		"author": "Shobinhour",
		"isbn": "1234568978941",
		"publication_year": 2024,
		"publisher": "publisher-1",
		"description": "some descriotion",
		"available_copies": 1,
		"total_copies": 21,
		"is_available": true,
		"created_at": "2025-03-15T16:03:24.269561Z",
		"updated_at": "2025-03-15T16:09:41.210386Z"
	}
}
```

### Delete a Book

Remove a book from the library collection.

**Endpoint:** `DELETE /api/books/{id}/`

**Authorization:** Bearer Token (Librarian role required)

**Success Response (200 OK):**

```json
No body returned for response
```

## Patron API

The Patron API provides endpoints for managing patrons (library users) in the system. It allows creating, retrieving, updating, and deleting patron records .

### API Endpoints

#### Base URL: `/api/patrons/`
```
| Endpoint                | Method | Description                             | Authorization Required |
|-------------------------|--------|-----------------------------------------|------------------------|
| `/`                     | GET    | List all patrons with pagination        | Yes (Librarian)        |
| `/`                     | POST   | Create a new patron                     | Yes (Librarian)        |
| `/{id}/`                | GET    | Retrieve details of a specific patron   | Yes (Librarian/Self)   |
| `/{id}/`                | PUT    | Update a patron's details               | Yes (Librarian/Self)   |
| `/{id}/`                | DELETE | Delete a patron                         | Yes (Librarian)        |
```

### List Patrons

Retrieve a paginated list of all patrons.

**Endpoint:** `GET /api/patrons/`

**Authorization:** Bearer Token (Librarian role required)


**Success Response (200 OK):**

```json
{
	"success": true,
	"message": "Patrons retrieved successfully",
	"status_code": 200,
	"data": [
		{
			"id": 2393,
			"first_name": "Abigail",
			"last_name": "Alhaiba",
			"full_name": "Abigail Alhaiba",
			"email": "abigail.alhaiba.2354@outlook.com",
			"phone_number": "555-671-8192",
			"address": "3169 Main Street",
			"birth_date": null,
			"membership_date": "2025-03-15",
			"active": true,
			"member_id": "P102354",
			"created_at": "2025-03-15T12:52:21.205013Z",
			"updated_at": "2025-03-15T12:52:21.205016Z"
		},
  ]
}
```

### Create a Patron

Create a new patron record.

**Endpoint:** `POST /api/patrons/`

**Authorization:** Bearer Token (Librarian role required)

**Request Body:**

```json
{
	"first_name":"Mustafa",
	"last_name":"Alhaiba",
	"email":"moustafa.alhaiba.2002@gmail.com",
	"member_id":"75",
	"phone_number":"0984474371",
	"address":"Syria - Damscus",
	"birth_date":"2024-02-02"
}
```

**Success Response (201 Created):**

```json
{
	"success": true,
	"message": "Patron created successfully",
	"status_code": 201,
	"data": {
		"id": 100040,
		"first_name": "Mustafa",
		"last_name": "Alhaiba",
		"full_name": "Mustafa Alhaiba",
		"email": "moustafa.alhaiba.2002@gmail.com",
		"phone_number": "0984474371",
		"address": "Syria - Damscus",
		"birth_date": "2024-02-02",
		"membership_date": "2025-03-15",
		"active": true,
		"member_id": "75",
		"created_at": "2025-03-15T16:33:21.009020Z",
		"updated_at": "2025-03-15T16:33:21.009032Z"
	}
}
```

**Error Response (400 Bad Request):**

```json
{
	"success": false,
	"message": "Validation error occurred",
	"status_code": 400,
	"errors": {
		"email": [
			"النموذج Patron والحقل بريد إلكتروني موجود مسبقاً."
		],
		"birth_date": [
			"صيغة التاريخ غير صحيحة. عليك أن تستخدم واحدة من هذه الصيغ التالية: YYYY-MM-DD."
		],
		"member_id": [
			"النموذج Patron والحقل Member ID موجود مسبقاً."
		]
	}
}
```

### Retrieve a Patron

Get detailed information about a specific patron.

**Endpoint:** `GET /api/patrons/{id}/`

**Authorization:** Bearer Token (Librarian role or the patron themselves)

**Success Response (200 OK):**

```json
{
	"success": true,
	"message": "Patron details retrieved successfully",
	"status_code": 200,
	"data": {
		"id": 100040,
		"first_name": "Mustafa",
		"last_name": "Alhaiba",
		"full_name": "Mustafa Alhaiba",
		"email": "moustafa.alhaiba.2002@gmail.com",
		"phone_number": "0984474371",
		"address": "Syria - Damscus",
		"birth_date": "2024-02-02",
		"membership_date": "2025-03-15",
		"active": true,
		"member_id": "75",
		"created_at": "2025-03-15T16:33:21.009020Z",
		"updated_at": "2025-03-15T16:33:21.009032Z"
	}
}
```

**Error Response (404 Not Found):**

```json
{
	"success": false,
	"message": "Resource not found",
	"status_code": 404,
	"errors": {
		"detail": "Not found"
	}
}
```

### Update a Patron

Update information for an existing patron.

**Endpoint:** `PUT /api/patrons/{id}/`

**Authorization:** Bearer Token (Librarian role or the patron themselves)

**Request Body:**

```json
{
	"first_name":"Mustafa Test",
	"last_name":"Alhaiba Test",
	"email":"moustafa.test.2002@gmail.com",
	"member_id":"89",
	"phone_number":"098888888888",
	"address":"Syria - Aleppo",
	"birth_date":"2024-03-02"
}
```

**Success Response (200 OK):**

```json
{
	"success": true,
	"message": "Patron updated successfully",
	"status_code": 200,
	"data": {
		"id": 100040,
		"first_name": "Mustafa Test",
		"last_name": "Alhaiba Test",
		"full_name": "Mustafa Test Alhaiba Test",
		"email": "moustafa.test.2002@gmail.com",
		"phone_number": "098888888888",
		"address": "Syria - Aleppo",
		"birth_date": "2024-03-02",
		"membership_date": "2025-03-15",
		"active": true,
		"member_id": "89",
		"created_at": "2025-03-15T16:33:21.009020Z",
		"updated_at": "2025-03-15T16:36:06.042564Z"
	}
}
```

### Delete a Patron

Soft delete a patron record from the system.

**Endpoint:** `DELETE /api/patrons/{id}/`

**Authorization:** Bearer Token (Librarian role required)

**Success Response (200 OK):**

```json
No body returned for response
```

## Borrowings API
The Borrowings API provides endpoints for managing book borrowing operations in the library system, allowing librarians to handle book checkouts and returns for patrons.



### API Endpoints
### Base URL: /api/
```
| Endpoint | Method | Description | Authorization Required |
|-------------------------------|--------|----------------------------------------|------------------------|
| borrow/{book_id}/patron/{patron_id}/ | POST | Borrow a specific book for a specific patron | Yes (Librarian) |
| return/{book_id}/patron/{patron_id}/ | POST | Return a specific book from a specific patron | Yes (Librarian) |
```


### Borrow a Book for a Patron

Allows a librarian to check out a specific book to a specific patron.

**Endpoint:** `POST /api/borrow/{book_id}/patron/{patron_id}/`
**Authorization:** `Bearer Token (Librarian role required)`
***URL Parameters:***
**book_id:** `ID of the book to be borrowed`
**patron_id:** `ID of the patron borrowing the book`


**Success Response (200 OK):**

```json
{
	"success": true,
	"message": "Book borrowed successfully",
	"status_code": 201,
	"data": {
		"id": 6,
		"book": 5,
		"book_title": "Book One",
		"patron": 10040,
		"patron_name": "Charles Moore",
		"borrow_date": "2025-03-15T16:52:24.984410Z",
		"due_date": "2025-03-29T16:52:24.984413Z",
		"return_date": null,
		"status": "borrowed",
		"notes": "",
		"is_overdue": false,
		"created_at": "2025-03-15T16:52:24.986045Z",
		"updated_at": "2025-03-15T16:52:24.986056Z"
	}
}
```


**Error Response (400 Bad Request):**

```json
{
	"success": false,
	"message": "Validation error occurred",
	"status_code": 400,
	"errors": {
		"book_id": [
			"This book is not available for borrowing."
		]
	}
}


OR

{
	"success": false,
	"message": "Validation error occurred",
	"status_code": 400,
	"errors": {
		"non_field_errors": [
			"This patron already has this book borrowed."
		]
	}
}
```


### Return a Book from a Patron
Allows a librarian to process a book return from a specific patron.

**Endpoint:** `POST /api/return/{book_id}/patron/{patron_id}/`
**Authorization:** `Bearer Token (Librarian role required)`
**URL Parameters:**
**book_id:** `ID of the book being returned`
**patron_id:** `ID of the patron returning the book`



**Success Response (200 OK):**

```json
{
	"success": true,
	"message": "Book returned successfully",
	"status_code": 200,
	"data": {
		"id": 7,
		"book": 2,
		"book_title": "Book One",
		"patron": 10040,
		"patron_name": "Charles Moore",
		"borrow_date": "2025-03-15T16:53:37.845918Z",
		"due_date": "2025-03-29T16:53:37.845923Z",
		"return_date": "2025-03-15T16:55:42.970970Z",
		"status": "returned",
		"notes": "",
		"is_overdue": false,
		"created_at": "2025-03-15T16:53:37.846707Z",
		"updated_at": "2025-03-15T16:55:42.972342Z"
	}
}
```




**Error Response (400 Bad Request):**

```json
{
	"success": false,
	"message": "Validation error occurred",
	"status_code": 400,
	"errors": {
		"non_field_errors": [
			"No active borrowing record found for this book and patron."
		]
	}
}
```
