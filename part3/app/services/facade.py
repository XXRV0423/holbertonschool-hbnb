from app.persistence.repository import InMemoryRepository
from app.models.user import User
from app.models.amenity import Amenity
from app.models.place import Place
from app.models.review import Review


DEFAULT_ADMIN_ID = '36c9050e-ddd3-4c3b-9731-9f487208bbc1'
DEFAULT_ADMIN_EMAIL = 'admin@hbnb.io'
DEFAULT_ADMIN_PASSWORD = 'admin1234'


class HBnBFacade:
    def __init__(self):
        self.user_repo = InMemoryRepository()
        self.place_repo = InMemoryRepository()
        self.review_repo = InMemoryRepository()
        self.amenity_repo = InMemoryRepository()
        self._seed_admin()

    def _seed_admin(self):
        """Seed a default administrator account.

        Admin-only endpoints (creating users, managing amenities, etc.)
        need at least one admin to already exist so the API can be
        bootstrapped. This account is recreated with a fixed ID whenever
        the facade starts (or storage is reset in tests).
        """
        admin = User(
            first_name='Admin',
            last_name='HBnB',
            email=DEFAULT_ADMIN_EMAIL,
            password=DEFAULT_ADMIN_PASSWORD,
            is_admin=True
        )
        admin.id = DEFAULT_ADMIN_ID
        self.user_repo.add(admin)

    # --- User methods ---
    def create_user(self, user_data):
        user = User(**user_data)
        self.user_repo.add(user)
        return user

    def get_user(self, user_id):
        return self.user_repo.get(user_id)

    def get_user_by_email(self, email):
        return self.user_repo.get_by_attribute('email', email)

    def get_all_users(self):
        return self.user_repo.get_all()

    def update_user(self, user_id, user_data):
        user = self.user_repo.get(user_id)
        password = user_data.pop('password', None)
        if user and password:
            user.hash_password(password)
        self.user_repo.update(user_id, user_data)
        return self.user_repo.get(user_id)

    # --- Amenity methods ---
    def create_amenity(self, amenity_data):
        amenity = Amenity(**amenity_data)
        self.amenity_repo.add(amenity)
        return amenity

    def get_amenity(self, amenity_id):
        return self.amenity_repo.get(amenity_id)

    def get_all_amenities(self):
        return self.amenity_repo.get_all()

    def update_amenity(self, amenity_id, amenity_data):
        self.amenity_repo.update(amenity_id, amenity_data)
        return self.amenity_repo.get(amenity_id)

    # --- Place methods ---
    def create_place(self, place_data):
        amenity_ids = place_data.pop('amenities', [])
        place = Place(**place_data)
        for amenity_id in amenity_ids:
            amenity = self.amenity_repo.get(amenity_id)
            if amenity:
                place.add_amenity(amenity)
        self.place_repo.add(place)
        return place

    def get_place(self, place_id):
        return self.place_repo.get(place_id)

    def get_all_places(self):
        return self.place_repo.get_all()

    def update_place(self, place_id, place_data):
        place_data.pop('amenities', None)
        self.place_repo.update(place_id, place_data)
        return self.place_repo.get(place_id)

    # --- Review methods ---
    def create_review(self, review_data):
        review = Review(**review_data)
        self.review_repo.add(review)
        return review

    def get_review(self, review_id):
        return self.review_repo.get(review_id)

    def get_all_reviews(self):
        return self.review_repo.get_all()

    def get_reviews_by_place(self, place_id):
        return [r for r in self.review_repo.get_all()
                if r.place_id == place_id]

    def update_review(self, review_id, review_data):
        self.review_repo.update(review_id, review_data)
        return self.review_repo.get(review_id)

    def delete_review(self, review_id):
        self.review_repo.delete(review_id)


facade = HBnBFacade()
