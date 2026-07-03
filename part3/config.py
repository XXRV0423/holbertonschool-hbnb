import os


class DevelopmentConfig:
    DEBUG = True
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    JWT_SECRET_KEY = SECRET_KEY


config = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig
}
