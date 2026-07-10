from sqlalchemy.orm import validates
from app import db
from app.models.base_model import BaseModel


class Amenity(BaseModel):
    __tablename__ = 'amenities'

    name = db.Column(db.String(50), nullable=False)

    def __init__(self, name):
        super().__init__()
        self.name = name

    @validates('name')
    def validate_name(self, key, value):
        if not value or not isinstance(value, str):
            raise ValueError("Amenity name is required")
        if len(value) > 50:
            raise ValueError("Amenity name must be 50 characters or fewer")
        return value

    def to_dict(self):
        data = super().to_dict()
        data.update({
            'name': self.name
        })
        return data
