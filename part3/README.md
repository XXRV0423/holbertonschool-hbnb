# HBnB — Part 3: Enhanced Backend with Authentication and Database Persistence

This part of the project rebuilds the HBnB backend (Flask + Flask-RESTx) from Part 2 on top of a real, persistent database using SQLAlchemy, and adds authentication, authorization, and role-based access control. It also includes raw SQL scripts and ER diagrams documenting the schema independently of the ORM.

## Folder structure

```
part3/
├── app/
│   ├── __init__.py                 # App factory: extensions, namespaces, db.create_all(), admin seed
│   ├── api/
│   │   └── v1/
│   │       ├── users.py            # /api/v1/users        (admin-only create, self/admin update)
│   │       ├── amenities.py        # /api/v1/amenities     (admin-only create/update)
│   │       ├── places.py           # /api/v1/places        (owner/admin update)
│   │       ├── reviews.py          # /api/v1/reviews       (author/admin update & delete)
│   │       └── auth.py             # /api/v1/auth/login, /api/v1/protected
│   ├── models/
│   │   ├── base_model.py           # Abstract SQLAlchemy base: id (UUID), created_at, updated_at
│   │   ├── user.py                 # User model (bcrypt password hashing, validation)
│   │   ├── place.py                # Place model + Place_Amenity association table
│   │   ├── review.py               # Review model
│   │   └── amenity.py              # Amenity model
│   ├── persistence/
│   │   └── repository.py           # Repository interface, InMemoryRepository, SQLAlchemyRepository
│   └── services/
│       ├── facade.py                # HBnBFacade — single entry point used by all API endpoints
│       └── repositories/            # Entity-specific repositories (User/Place/Review/Amenity)
├── sql/
│   ├── schema.sql                   # Raw MySQL DDL for the full schema (independent of the ORM)
│   └── data.sql                     # Seed data: admin user + initial amenities
├── diagrams/
│   ├── er_diagram.mmd               # Mermaid ER diagram source
│   ├── er_diagram.md                # Write-up explaining entities/relationships
│   └── er_diagram.svg               # Rendered diagram image
├── tests/
│   └── test_endpoints.py            # Automated endpoint tests (see "Testing" note below)
├── config.py                        # Config classes (SECRET_KEY, SQLALCHEMY_DATABASE_URI, JWT_SECRET_KEY)
├── requirements.txt
└── run.py                           # Entry point: `python run.py`
```

## Setup and installation

```bash
cd part3
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Dependencies: `flask`, `flask-restx`, `flask-bcrypt`, `flask-jwt-extended`, `sqlalchemy`, `flask-sqlalchemy`.

## Running the application

```bash
python run.py
```

The Swagger UI is available at `http://127.0.0.1:5000/api/v1/`.

On startup, `create_app()` automatically runs `db.create_all()` (creating tables if they don't exist) and seeds a default administrator account if one isn't already present:

| Field | Value |
|---|---|
| email | `admin@hbnb.io` |
| password | `admin1234` |
| is_admin | `true` |

This is a development convenience, not a production practice — the password is a known default and `config.py`'s `SECRET_KEY` falls back to a hardcoded string if the `SECRET_KEY` environment variable isn't set.

## Configuration

`config.py` defines a `DevelopmentConfig` used by default (`SQLALCHEMY_DATABASE_URI = 'sqlite:///development.db'`). Note that Flask resolves this relative SQLite path against the app's `instance/` folder, so the actual file ends up at `part3/instance/development.db`, not the project root.

## API overview

All endpoints are namespaced under `/api/v1/`.

| Namespace | Endpoint | Access |
|---|---|---|
| `auth` | `POST /auth/login` | Public — returns a JWT (includes `is_admin` claim) |
| `auth` | `GET /protected/` | Any valid JWT |
| `users` | `GET /users/`, `GET /users/<id>` | Public |
| `users` | `POST /users/` | Admin only |
| `users` | `PUT /users/<id>` | Self (name only) or admin (any field, including email/password) |
| `amenities` | `GET /amenities/`, `GET /amenities/<id>` | Public |
| `amenities` | `POST /amenities/`, `PUT /amenities/<id>` | Admin only |
| `places` | `GET /places/`, `GET /places/<id>`, `GET /places/<id>/reviews` | Public |
| `places` | `POST /places/` | Any authenticated user (becomes the owner) |
| `places` | `PUT /places/<id>` | Owner or admin |
| `reviews` | `GET /reviews/`, `GET /reviews/<id>` | Public |
| `reviews` | `POST /reviews/` | Authenticated user (can't review own place, one review per place per user; admin bypasses both rules) |
| `reviews` | `PUT /reviews/<id>`, `DELETE /reviews/<id>` | Author or admin |

## Authentication and authorization

- Passwords are hashed with `flask-bcrypt` (`User.hash_password` / `User.verify_password`); plaintext passwords are never stored or returned by the API.
- `POST /auth/login` issues a JWT via `flask-jwt-extended`, with the user's ID as identity and `is_admin` as an additional claim.
- Ownership rules (place/review updates and deletes) compare the JWT identity against the resource's `owner_id`/`user_id`, with admins bypassing these checks.

## Database models and relationships

All models inherit from `BaseModel` (`app/models/base_model.py`), which provides a UUID string `id`, `created_at`, and `updated_at` as real SQLAlchemy columns.

- **User** — `first_name`, `last_name`, `email` (unique), `password` (hashed), `is_admin`.
- **Place** — `title`, `description`, `price`, `latitude`, `longitude`, `owner_id` (FK → `User.id`).
- **Review** — `text`, `rating` (1–5), `user_id` (FK → `User.id`), `place_id` (FK → `Place.id`).
- **Amenity** — `name` (unique).
- **Place_Amenity** — association table (composite primary key `place_id` + `amenity_id`) implementing the Place ↔ Amenity many-to-many relationship.

Relationships: `User` ↔ `Place` and `User` ↔ `Review` are one-to-many (`User.places`, `User.reviews`, with `Place.owner` / `Review.user` as the reverse side); `Place` ↔ `Review` is one-to-many (`Place.reviews`, `Review.place`); `Place` ↔ `Amenity` is many-to-many via `Place_Amenity` (`Place.amenities`, `Amenity.places`). See `diagrams/er_diagram.md` for the full breakdown.

Persistence goes through the repository pattern: `app/persistence/repository.py` defines a `Repository` interface with an `InMemoryRepository` and a `SQLAlchemyRepository` implementation, and each entity has its own repository under `app/services/repositories/`. `HBnBFacade` (`app/services/facade.py`) is the single object the API layer talks to — it owns one repository per entity and exposes plain CRUD-style methods (`create_user`, `get_place`, `update_review`, etc.).

## SQL scripts

`sql/schema.sql` and `sql/data.sql` define the same schema in raw MySQL DDL, independent of the SQLAlchemy models — useful for understanding or recreating the database without the ORM. `schema.sql` creates the five tables with the same columns, foreign keys, and constraints as the models (including a unique constraint on `Review(user_id, place_id)` and a composite primary key on `Place_Amenity`). `data.sql` seeds the same default admin account and three starter amenities (WiFi, Swimming Pool, Air Conditioning).

## Database diagrams

`diagrams/er_diagram.mmd` is the Mermaid ER diagram source (renders natively on GitHub); `diagrams/er_diagram.md` walks through each entity and relationship; `diagrams/er_diagram.svg` is an exported image version.

## Testing

`tests/test_endpoints.py` contains automated tests written earlier in the project (covering registration, JWT auth, ownership rules, and admin RBAC) against an in-memory-backed facade. It has not yet been updated for the SQLAlchemy-backed persistence layer introduced later — its `reset_facade()` helper assumes `InMemoryRepository`'s internal storage, which no longer applies now that `User`/`Place`/`Review`/`Amenity` are all backed by real database repositories. It's kept in the repo as a reference for the request/response contracts, but currently needs rework (e.g. clearing tables directly, or using a `sqlite:///:memory:` test config) before it will pass end-to-end.
