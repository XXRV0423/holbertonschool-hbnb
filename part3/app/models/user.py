import re
from sqlalchemy.orm import validates
from app import db, bcrypt
from app.models.base_model import BaseModel


class User(BaseModel):
    __tablename__ = 'users'

    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    # One-to-many: a User can own many Places and write many Reviews.
    # backref creates the reverse accessor (place.owner / review.user)
    # automatically, so Place/Review don't need their own relationship().
    places = db.relationship('Place', backref='owner', lazy=True)
    reviews = db.relationship('Review', backref='user', lazy=True)

    def __init__(self, first_name, last_name, email, password=None, is_admin=False):
        super().__init__()
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.is_admin = is_admin
        if password:
            self.hash_password(password)

    @validates('first_name')
    def validate_first_name(self, key, value):
        if not value or not isinstance(value, str):
            raise ValueError("First name is required")
        if len(value) > 50:
            raise ValueError("First name must be 50 characters or fewer")
        return value

    @validates('last_name')
    def validate_last_name(self, key, value):
        if not value or not isinstance(value, str):
            raise ValueError("Last name is required")
        if len(value) > 50:
            raise ValueError("Last name must be 50 characters or fewer")
        return value

    @validates('email')
    def validate_email(self, key, value):
        if not value or not isinstance(value, str):
            raise ValueError("Email is required")
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(pattern, value):
            raise ValueError("Invalid email format")
        return value

    @validates('password')
    def validate_password(self, key, value):
        if value is not None and not isinstance(value, str):
            raise ValueError("Password must be a string")
        return value

    def hash_password(self, password):
        """Hash the password before storing it."""
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def verify_password(self, password):
        """Verify the provided password against the stored hash."""
        if not self.password:
            return False
        return bcrypt.check_password_hash(self.password, password)

    def to_dict(self):
        data = super().to_dict()
        data.update({
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'is_admin': self.is_admin
        })
        return data
