# HBnB - Detailed Class Diagram: Business Logic Layer

## Overview

This document explains the class diagram defined in [`1.class_diagram.mermaid`](./1.class_diagram.mermaid). It represents the internal structure of the **Business Logic Layer** of the HBnB application, showing the key entities, their attributes, methods, and the relationships between them.

---

## Classes

### BaseModel
The parent class inherited by all entities in the system. It provides common attributes and methods shared across every model.

**Attributes:**
- `id: UUID` — unique identifier for every object
- `created_at: datetime` — timestamp of when the object was created
- `updated_at: datetime` — timestamp of the last update

**Methods:**
- `save()` — persists the current state of the object
- `update(data)` — updates the object's attributes with new data
- `delete()` — removes the object from storage
- `to_dict()` — serializes the object into a dictionary

---

### User
Represents a registered user of the application. Inherits from `BaseModel`.

**Attributes:**
- `first_name: string` — user's first name
- `last_name: string` — user's last name
- `email: string` — user's email address (used for login)
- `password: string` — hashed password
- `is_admin: bool` — whether the user has admin privileges

**Methods:**
- `register()` — creates a new user account
- `update_profile(data)` — updates the user's personal information
- `delete_account()` — removes the user's account from the system
- `authenticate(password)` — verifies the user's credentials

---

### Place
Represents a property listing created by a user. Inherits from `BaseModel`.

**Attributes:**
- `title: string` — name of the place
- `description: string` — detailed description of the place
- `price: float` — price per night
- `latitude: float` — geographic latitude
- `longitude: float` — geographic longitude
- `owner_id: UUID` — reference to the User who owns the place
- `amenities: list` — list of associated Amenity objects

**Methods:**
- `create_place()` — creates a new place listing
- `update_place(data)` — updates the place's information
- `delete_place()` — removes the listing
- `add_amenity(amenity)` — associates an amenity with the place
- `remove_amenity(amenity)` — removes an amenity from the place
- `update_details(data)` — updates specific place details
- `validate_price()` — ensures the price is a valid positive value
- `validate_location()` — ensures latitude and longitude are within valid ranges

---

### Review
Represents a review submitted by a user for a place. Inherits from `BaseModel`.

**Attributes:**
- `text: string` — the written content of the review
- `rating: integer` — numeric rating given to the place
- `user_id: UUID` — reference to the User who wrote the review
- `place_id: UUID` — reference to the Place being reviewed

**Methods:**
- `submit_review()` — submits a new review
- `update_review()` — edits an existing review
- `delete_review()` — removes the review
- `validate_rating()` — ensures the rating is within the accepted range

---

### Amenity
Represents a feature or facility that can be associated with a place. Inherits from `BaseModel`.

**Attributes:**
- `name: string` — name of the amenity (e.g., "WiFi", "Pool")
- `description: string` — brief description of the amenity

**Methods:**
- `create_amenity()` — creates a new amenity
- `update_amenity(data)` — updates the amenity's information
- `delete_amenity()` — removes the amenity
- `validate_name()` — ensures the amenity name is not empty or invalid

---

## Relationships

| Relationship | Type | Description |
|---|---|---|
| `BaseModel <\|-- User` | Inheritance | User inherits all base attributes and methods |
| `BaseModel <\|-- Place` | Inheritance | Place inherits all base attributes and methods |
| `BaseModel <\|-- Review` | Inheritance | Review inherits all base attributes and methods |
| `BaseModel <\|-- Amenity` | Inheritance | Amenity inherits all base attributes and methods |
| `User "1" --> "0..*" Place` | Association | A user can own zero or more places |
| `User "1" --> "0..*" Review` | Association | A user can write zero or more reviews |
| `Place "1" --> "0..*" Review` | Association | A place can have zero or more reviews |
| `Place "0..*" o-- "0..*" Amenity` | Aggregation | Places and amenities have a many-to-many relationship |

---

## Communication Flow

```
BaseModel
    │
    ├── User ──owns──► Place ──has──► Review
    │                    │
    │                    └──contains──► Amenity
    │
    ├── Place
    ├── Review
    └── Amenity
```
