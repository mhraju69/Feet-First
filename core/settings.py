import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, ".env"))

SECRET_KEY = os.environ.get("SECRET_KEY")

DEBUG = True



# Application definition

INSTALLED_APPS = [
    'unfold',
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'Accounts',
    'Products',
    'django_filters',
    'Surveys',
    'Contact',
    "cloudinary",
    "cloudinary_storage",
    'rest_framework_simplejwt.token_blacklist',
    'Others',
    'tailwind',
    'dal',
    'dal_select2',
    'Brands',
    ]

TAILWIND_APP_NAME = 'Accounts   '  # Replace with your app name
TAILWIND_MODE = 'jit'

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',    
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.FixAuthorizationHeaderMiddleware',
]
CORS_ALLOW_ALL_ORIGINS = True

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'core.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}   

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': os.environ.get('DB_NAME'),
#         'USER': os.environ.get('DB_USER'),
#         'PASSWORD': os.environ.get('DB_PASSWORD'),
#         'HOST': os.environ.get('DB_HOST'),
#         'PORT': os.environ.get('DB_PORT'),
#     }
# }  


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

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True



STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",  
]
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")


MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


AUTH_USER_MODEL = 'Accounts.User'  


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        ),
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        'rest_framework.filters.OrderingFilter',
        ],
        'DEFAULT_PAGINATION_CLASS': None,  # No default pagination
        'PAGE_SIZE': None,
    }

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30)
}


UNFOLD = {
    "MODE": "dark",
    "SITE_TITLE": "Feet F1rst Admin",   
    "SITE_HEADER": "Admin Dashboard",
    "SHOW_ICON": True,  
    "CUSTOM_CSS": "/static/css/custom.css",
    "SITE_LOGO": "/static/images/logo.png",
    "COLORS": {
        "primary": {
            "50": "#62a07b",
            "100": "#62a07b",
            "200": "#62a07b",
            "300": "#62a07b",
            "400": "#62a07b",
            "500": "#62a07b",  # Your custom color
            "600": "#62a07b",
            "700": "#62a07b",
            "800": "#62a07b",
            "900": "#62a07b",
        },
    },
     "EXTENSIONS": {
        "colors": {
            "primary": "#62a07b",  # Ensure this matches
        },
    },
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")
CONTACT_EMAIL = os.getenv("CONTACT_EMAIL")

CORS_ALLOW_CREDENTIALS = True
ALLOWED_HOSTS = ['localhost','10.10.13.59','ape-in-eft.ngrok-free.app']
CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1:8000', 'https://yourdomain.com','https://ape-in-eft.ngrok-free.app',"http://127.0.0.1:5500",
    "http://localhost:5500","http://localhost:8000"]


# CORS_ALLOW_ALL_ORIGINS = True
GOOGLE_OAUTH_CALLBACK_URL = os.getenv("GOOGLE_OAUTH_CALLBACK_URL")
GOOGLE_OAUTH_CLIENT_ID = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
GOOGLE_OAUTH_CLIENT_SECRET = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": os.environ.get("CLOUDINARY_CLOUD_NAME"),
    "API_KEY": os.environ.get("CLOUDINARY_API_KEY"),
    "API_SECRET": os.environ.get("CLOUDINARY_API_SECRET"),
    'SECURE': True,  # HTTPS URL এর জন্য
    'MEDIA_TAG': 'media',
    'INVALID_VIDEO_ERROR_MESSAGE': 'Please upload a valid video file.',
    'EXCLUDED_FORMATS': ['svg', 'webp'],
}

DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"


JAZZMIN_SETTINGS = {
    "site_title": "Feet F1rst Admin", 
    "site_header": "Feet F1rst Admin",
    "welcome_sign": "Welcome to My Admin",
    "copyright": "© 2025 My Company",
    
        "site_logo": "images/logo.png",        
    "site_logo_classes": "img-circle",
    "login_logo": "images/logo.png",       
    "login_logo_dark": None,      

    "custom_css": "css/custom_admin.css",
    "custom_js": None,
}