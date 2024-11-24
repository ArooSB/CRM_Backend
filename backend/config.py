import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'aroo')
    #SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/crm_backend')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL',
                                             'postgresql://aroo:7Axx8cWyMQTxWj3TE642pLnVo8VZlKOO@dpg-csuvp223esus73cogp10-a.oregon-postgres.render.com/crm_db_yz92')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/crm_backend_test')

class ProductionConfig(Config):
    #SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/crm_backend')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'postgresql://aroo:7Axx8cWyMQTxWj3TE642pLnVo8VZlKOO@dpg-csuvp223esus73cogp10-a.oregon-postgres.render.com/crm_db_yz92'
    )


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

current_config = config[os.getenv('FLASK_ENV', 'default')]
# postgresql://aroo:7Axx8cWyMQTxWj3TE642pLnVo8VZlKOO@dpg-csuvp223esus73cogp10-a.oregon-postgres.render.com/crm_db_yz92