from flask import Flask
from flask_restx import Api
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

bcrypt = Bcrypt()
jwt = JWTManager()
db = SQLAlchemy()

from app.api.v1.users import api as users_ns
from app.api.v1.amenities import api as amenities_ns
from app.api.v1.places import api as places_ns
from app.api.v1.reviews import api as reviews_ns
from app.api.v1.auth import api as auth_ns, protected_api as protected_ns

def create_app(config_class="config.DevelopmentConfig"):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Allow the static front-end (part4) to call this API from the browser.
    # allow_headers is explicit so the "Authorization" header used for JWT
    # requests isn't stripped out of the CORS preflight response.
    CORS(app, resources={r"/api/*": {"origins": "*"}},
         allow_headers=["Content-Type", "Authorization"])

    bcrypt.init_app(app)
    jwt.init_app(app)
    db.init_app(app)
    api = Api(app, version='1.0', title='HBnB API',
            description='HBnB Application API', doc='/api/v1/')

    api.add_namespace(users_ns, path='/api/v1/users')
    api.add_namespace(amenities_ns, path='/api/v1/amenities')
    api.add_namespace(places_ns, path='/api/v1/places')
    api.add_namespace(reviews_ns, path='/api/v1/reviews')
    api.add_namespace(auth_ns, path='/api/v1/auth')
    api.add_namespace(protected_ns, path='/api/v1/protected')

    with app.app_context():
        db.create_all()
        from app.services.facade import facade
        facade._seed_admin()

    return app
