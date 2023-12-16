import os

PROPAGATE_EXCEPTIONS = True
FLASK_DEBUG = True

# Database Configuration
SQLALCHEMY_DATABASE_URI = f"{os.environ['POSTGRES_NAME']}://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}@{os.environ['POSTGRES_HOST']}/{os.environ['POSTGRES_DB']}"
SQLALCHEMY_TRACK_MODIFICATIONS = False


# NO I DONT USE IT, НЕМА ЧАСУ
# OpenAPI Configuration
API_TITLE = "Finance REST API"
API_VERSION = "v1"
OPENAPI_VERSION = "3.0.3"
OPENAPI_URL_PREFIX = "/"
OPENAPI_SWAGGER_UI_PATH = "/swagger-ui"
OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
