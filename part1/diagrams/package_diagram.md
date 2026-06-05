# HBnB - High-Level Package Diagram

## Overview

The HBnB application is structured around a **three-layer architecture**, where each layer has a distinct responsibility. Communication between layers is mediated exclusively through the **Facade pattern**, keeping the layers decoupled and independently maintainable.

The diagram is defined in [`0.package_diagram.mermaid`](./0.package_diagram.mermaid).

---

## Layers

### 1. Presentation Layer
Handles all interaction between the client and the application. It exposes API endpoints for each core resource:

- `UserAPI` — handles user-related requests (registration, profile management)
- `PlaceAPI` — handles place listing requests
- `ReviewAPI` — handles review submission and retrieval
- `AmenityAPI` — handles amenity management

This layer never communicates directly with the Business Logic or Persistence layers. Every request is forwarded through the Facade.

---

### 2. HBnBFacade
The `HBnBFacade` is the single entry point between the Presentation Layer and the rest of the application. It implements the **Facade design pattern**, providing a unified interface that hides the complexity of the underlying layers.

It exposes the following operations:

- **User:** `create_user()`, `get_user()`, `delete_user()`
- **Place:** `create_place()`, `get_place()`, `delete_place()`
- **Review:** `create_review()`, `get_review()`, `delete_review()`
- **Amenity:** `create_amenity()`, `get_amenity()`, `delete_amenity()`

By centralizing communication through the Facade, the Presentation Layer remains unaware of how business logic is applied or how data is stored.

---

### 3. Business Logic Layer
Contains the service classes that implement the core business rules for each entity:

- `UserService` — handles user-related business logic
- `PlaceService` — handles place-related business logic
- `ReviewService` — handles review-related business logic
- `AmenityService` — handles amenity-related business logic

This layer receives instructions from the Facade and applies the appropriate business operations before delegating data persistence to the Persistence Layer.

---

### 4. Persistence Layer
Handles all data storage and retrieval. It provides a repository for each entity and manages the database connection:

- `UserRepository` — stores and retrieves user records
- `PlaceRepository` — stores and retrieves place records
- `ReviewRepository` — stores and retrieves review records
- `AmenityRepository` — stores and retrieves amenity records
- `DatabaseConnection` — manages the connection to the underlying database

---

## Communication Flow

```
Client Request
     │
     ▼
Presentation Layer (UserAPI, PlaceAPI, ReviewAPI, AmenityAPI)
     │  uses (Facade Pattern)
     ▼
HBnBFacade
     │  manages business operations
     ▼
Business Logic Layer (UserService, PlaceService, ReviewService, AmenityService)
     │  Database operations (stores / retrieves data)
     ▼
Persistence Layer (UserRepository, PlaceRepository, ReviewRepository, AmenityRepository, DatabaseConnection)
```
