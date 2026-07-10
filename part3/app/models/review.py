from app.models.base_model import BaseModel


class Review(BaseModel):
    # NOTE: see amenity.py — placeholder table so SQLAlchemy can map this
    # class now that BaseModel is a db.Model. Review still uses the
    # in-memory repository for now; full column mapping is a future task.
    __tablename__ = 'reviews'

    def __init__(self, text, rating, place_id, user_id):
        super().__init__()
        self.text = text
        self.rating = rating
        self.place_id = place_id
        self.user_id = user_id

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        if not value or not isinstance(value, str):
            raise ValueError("Review text is required")
        self._text = value

    @property
    def rating(self):
        return self._rating

    @rating.setter
    def rating(self, value):
        if not isinstance(value, int) or not (1 <= value <= 5):
            raise ValueError("Rating must be an integer between 1 and 5")
        self._rating = value

    def to_dict(self):
        data = super().to_dict()
        data.update({
            'text': self.text,
            'rating': self.rating,
            'place_id': self.place_id,
            'user_id': self.user_id
        })
        return data
