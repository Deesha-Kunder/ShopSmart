import os
from pathlib import Path
from dotenv import load_dotenv
import os
from datetime import timedelta
import dj_database_url
import platform
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-)t81nk()_*lbwil6o$#l&fu=-y1a4tacf6uud3jv+97kuc*uce")
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()

AUTH_USER_MODEL = "mainapp.User"

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")
FIREBASE_STORAGE_BUCKET = os.getenv('FIREBASE_STORAGE_BUCKET', 'shopsmartgmx.firebasestorage.app')
FIREBASE_CREDENTIALS_JSON = os.getenv('FIREBASE_CREDENTIALS_JSON')


# Image Upload Configuration
SHOP_IMAGE_LIMIT = int(os.getenv('SHOP_IMAGE_LIMIT', 3))
PRODUCT_IMAGE_LIMIT = int(os.getenv('PRODUCT_IMAGE_LIMIT', 5))
DOCUMENT_IMAGE_LIMIT = int(os.getenv('DOCUMENT_IMAGE_LIMIT', 5))
MAX_IMAGE_SIZE_MB = int(os.getenv('MAX_IMAGE_SIZE_MB', 5))


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'corsheaders',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'rest_framework',
    'rest_framework_gis',
    'rest_framework_simplejwt.token_blacklist',
    'mainapp.apps.MainappConfig', # Use full path to ensure ready() is called
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # WhiteNoise middleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ShopSmart.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ShopSmart.wsgi.application'

# Database & GIS Config
if ENVIRONMENT == "development":
    DATABASES = {
        'default': {
            'ENGINE': 'django.contrib.gis.db.backends.postgis',
            'NAME': os.getenv('DB_NAME', 'dev_db'),
            'USER': os.getenv('DB_USER', 'postgres'),
            'PASSWORD': os.getenv('DB_PASSWORD', 'password'),
            'HOST': os.getenv('DB_HOST', '127.0.0.1'),
            'PORT': os.getenv('DB_PORT', '5432'),
        }
    }

else:
    db_config = dj_database_url.parse(os.getenv('DATABASE_URL'))
    db_config['ENGINE'] = 'django.contrib.gis.db.backends.postgis'
    DATABASES = {
        'default': db_config
    }

system = platform.system()

if system == "Windows":
    GDAL_LIBRARY_PATH = os.getenv("GDAL_LIBRARY_PATH", "C:/OSGeo4W/bin/gdal311.dll")
    GEOS_LIBRARY_PATH = os.getenv("GEOS_LIBRARY_PATH", "C:/OSGeo4W/bin/geos_c.dll")
    PROJ_LIBRARY_PATH = os.getenv("PROJ_LIBRARY_PATH", "C:/OSGeo4W/bin/proj.dll")
else:
    GDAL_LIBRARY_PATH = os.getenv("GDAL_LIBRARY_PATH", "/lib/x86_64-linux-gnu/libgdal.so")
    GEOS_LIBRARY_PATH = os.getenv("GEOS_LIBRARY_PATH", "/lib/x86_64-linux-gnu/libgeos_c.so")
    PROJ_LIBRARY_PATH = os.getenv("PROJ_LIBRARY_PATH", "/lib/x86_64-linux-gnu/libproj.so")
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files (for user profile images)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    },
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=100),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,        
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
]
