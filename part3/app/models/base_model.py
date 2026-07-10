import uuid
from datetime import datetime
from app import db


class BaseModel(db.Model):
    __abstract__ = True  # SQLAlchemy will not create a table for this class

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Column defaults only apply once a row is flushed to the database.
        # Entities that aren't persisted yet (Amenity/Place/Review still use
        # the in-memory repository) need a real id/timestamps right away, so
        # we set them explicitly here too.
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.created_at:
            self.created_at = datetime.utcnow()
        if not self.updated_at:
            self.updated_at = datetime.utcnow()

    def save(self):
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()

    def update(self, data):
        """Update instance attributes from a dictionary."""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.save()

    def delete(self):
        """Placeholder for deletion logic (handled by repository)."""
        pass

    def to_dict(self):
        """Return a dictionary representation of the instance."""
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
