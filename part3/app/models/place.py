from sqlalchemy.orm import validates
from app import db
from app.models.base_model import BaseModel


class Place(BaseModel):
    # NOTE: owner_id/amenities/reviews stay plain (unmapped) attributes for
    # now — relationships between entities are added in a later task. Only
    # the core scalar attributes below are real SQLAlchemy columns.
    __tablename__ = 'places'

    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String, nullable=True)
    price = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)

    def __init__(self, title, description, price, latitude, longitude, owner_id):
        super().__init__()
        self.title = title
        self.description = description
        self.price = price
        self.latitude = latitude
        self.longitude = longitude
        self.owner_id = owner_id
        self.amenities = []
        self.reviews = []

    @validates('title')
    def validate_title(self, key, value):
        if not value or not isinstance(value, str):
            raise ValueError("Title is required")
        if len(value) > 100:
            raise ValueError("Title must be 100 characters or fewer")
        return value

    @validates('price')
    def validate_price(self, key, value):
        if not isinstance(value, (int, float)) or value < 0:
            raise ValueError("Price must be a non-negative number")
        return float(value)

    @validates('latitude')
    def validate_latitude(self, key, value):
        if not isinstance(value, (int, float)) or not (-90.0 <= value <= 90.0):
            raise ValueError("Latitude must be between -90 and 90")
        return float(value)

    @validates('longitude')
    def validate_longitude(self, key, value):
        if not isinstance(value, (int, float)) or not (-180.0 <= value <= 180.0):
            raise ValueError("Longitude must be between -180 and 180")
        return float(value)

    def add_amenity(self, amenity):
        if amenity not in self.amenities:
            self.amenities.append(amenity)

    def remove_amenity(self, amenity):
        if amenity in self.amenities:
            self.amenities.remove(amenity)

    def add_review(self, review):
        if review not in self.reviews:
            self.reviews.append(review)

    def to_dict(self):
        data = super().to_dict()
        data.update({
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'owner_id': self.owner_id,
            'amenities': [a.id for a in self.amenities]
        })
        return data
