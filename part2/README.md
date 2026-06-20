# HBnB Evolution - Part 2: Implementation of Business Logic and API Endpoints

## Description

Part 2 of the HBnB Evolution project implements the core Business Logic layer and RESTful API endpoints for the HBnB application using Flask and Flask-RESTx. The architecture follows a three-layer design pattern with a Facade to decouple the layers.

## Architecture

```
Presentation Layer (API)
        │
        ▼
   Facade (Services)
        │
        ▼
Business Logic Layer (Models)
        │
        ▼
Persistence Layer (In-Memory Repository)
```

### Layers

- **Presentation Layer** (`app/api/v1/`): Flask-RESTx namespaces and resources that handle HTTP requests and responses.
- **Business Logic Layer** (`app/models/`): Entity classes with validation logic.
- **Facade** (`app/services/facade.py`): Single entry point between the API and the models/persistence layers.
- **Persistence Layer** (`app/persistence/`): In-memory repository (to be replaced with SQLAlchemy in Part 3).

## Project Structure

```
part2/
├── app/
│   ├── __init__.py             # App factory
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── users.py        # User endpoints
│   │       ├── amenities.py    # Amenity endpoints
│   │       ├── places.py       # Place endpoints
│   │       └── reviews.py      # Review endpoints
│   ├── models/
│   │   ├── base_model.py       # BaseModel with id, created_at, updated_at
│   │   ├── user.py             # User model
│   │   ├── amenity.py          # Amenity model
│   │   ├── place.py            # Place model
│   │   └── review.py           # Review model
│   ├── persistence/
│   │   └── repository.py       # Abstract repo + InMemoryRepository
│   └── services/
│       └── facade.py           # HBnBFacade singleton
├── tests/
│   ├── __init__.py
│   └── test_endpoints.py       # Unit tests for all endpoints
├── config.py                   # App configuration
├── requirements.txt
└── run.py                      # Entry point
```

## Installation

```bash
# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install flask flask-restx
```

## Running the Application

```bash
python run.py
```

The API will be available at `http://127.0.0.1:5000`.
Swagger documentation is served at `http://127.0.0.1:5000/api/v1/`.

## API Endpoints

### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/users/` | Create a new user |
| GET | `/api/v1/users/` | Retrieve all users |
| GET | `/api/v1/users/<user_id>` | Retrieve a user by ID |
| PUT | `/api/v1/users/<user_id>` | Update a user |

### Amenities

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/amenities/` | Create a new amenity |
| GET | `/api/v1/amenities/` | Retrieve all amenities |
| GET | `/api/v1/amenities/<amenity_id>` | Retrieve an amenity by ID |
| PUT | `/api/v1/amenities/<amenity_id>` | Update an amenity |

### Places

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/places/` | Create a new place |
| GET | `/api/v1/places/` | Retrieve all places |
| GET | `/api/v1/places/<place_id>` | Retrieve a place by ID (with owner, amenities, reviews) |
| PUT | `/api/v1/places/<place_id>` | Update a place |
| GET | `/api/v1/places/<place_id>/reviews` | Retrieve all reviews for a place |

### Reviews

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/reviews/` | Create a new review |
| GET | `/api/v1/reviews/` | Retrieve all reviews |
| GET | `/api/v1/reviews/<review_id>` | Retrieve a review by ID |
| PUT | `/api/v1/reviews/<review_id>` | Update a review |
| DELETE | `/api/v1/reviews/<review_id>` | Delete a review |

## Models and Validation

### User
- `first_name`: required, max 50 characters
- `last_name`: required, max 50 characters
- `email`: required, must be a valid email format, unique

### Amenity
- `name`: required, max 50 characters

### Place
- `title`: required, max 100 characters
- `description`: optional string
- `price`: required, must be a non-negative number
- `latitude`: required, must be between -90 and 90
- `longitude`: required, must be between -180 and 180
- `owner_id`: required, must reference an existing user

### Review
- `text`: required string
- `rating`: required integer, must be between 1 and 5
- `user_id`: required, must reference an existing user
- `place_id`: required, must reference an existing place

## Running Tests

```bash
python -m pytest tests/test_endpoints.py -v
```

The test suite covers 44 test cases across all four entities, including success scenarios, validation errors, boundary values, and 404 handling.

## Authors

- Xander Roldan Villarrubia
