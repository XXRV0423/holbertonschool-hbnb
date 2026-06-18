import os


class DevelopmentConfig:
    DEBUG = True
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')


config = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig
}
