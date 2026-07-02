from app.models.base_model import BaseModel


class Amenity(BaseModel):
    def __init__(self, name):
        super().__init__()
        self.name = name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not value or not isinstance(value, str):
            raise ValueError("Amenity name is required")
        if len(value) > 50:
            raise ValueError("Amenity name must be 50 characters or fewer")
        self._name = value

    def to_dict(self):
        data = super().to_dict()
        data.update({
            'name': self.name
        })
        return data
