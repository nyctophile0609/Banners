from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY =os.environ.get("SECRET_KEY")
#'django-insecure-w0sw7d3qy^slfz$9jr4bjo-*=+l320y5s1ttf37p03^sc_34$)'
DEBUG = os.environ.get("DEBUG")


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'corsheaders',

    'api.apps.ApiConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.common.CommonMiddleware',
]



ROOT_URLCONF = 'banners.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'banners.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'api.UserModel'
MEDIA_ROOT = os.path.join(BASE_DIR, 'banner_images')
MEDIA_URL = 'banner_images/'
# CORS_ORIGIN_ALLOW_ALL = True
# CORS_ALLOW_CREDENTIALS = True
# # CORS_ORIGIN_ALLOW_ALL = True
# # CORS_ALLOW_CREDENTIALS = True
# # CSRF_TRUSTED_ORIGINS = ['*']
# # SESSION_COOKIE_SAMESITE = 'None'
# # CSRF_COOKIE_SAMESITE = 'None'
# # SESSION_COOKIE_SECURE = True
# # CSRF_COOKIE_SECURE = True


ALLOWED_HOSTS = ["api.jsspm.uz", "jsspm.uz"]  # specify allowed hosts explicitly
CORS_ALLOWED_ORIGINS=["https://jsspm.uz/"]
# CORS_ORIGIN_WHITELIST = ["http://jsspm.uz", "https://jsspm.uz"]  # specify allowed origins explicitly
# CORS_ALLOW_CREDENTIALS = True

# CSRF_TRUSTED_ORIGINS = ["http://jsspm.uz", "https://jsspm.uz"]  # specify trusted origins for CSRF protection
# SESSION_COOKIE_SAMESITE = 'Lax'
# CSRF_COOKIE_SAMESITE = 'Lax'
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
