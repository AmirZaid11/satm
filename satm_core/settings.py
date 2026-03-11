import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-change-this-later-for-production'  # generate secure one later

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']


# CSRF and Security Settings for Local Development

INSTALLED_APPS = [
    'unfold',                     # ← must be first
    'unfold.contrib.filters',     # optional but recommended
    'unfold.contrib.inlines',     # optional for better inlines
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users.apps.UsersConfig',
    'timetabling.apps.TimetablingConfig',
    'analytics.apps.AnalyticsConfig',
]

MIDDLEWARE = [  # default is fine, no change needed now
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'satm_core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # ← this line must exist
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.csrf',
            ],
        },
    },
]

WSGI_APPLICATION = 'satm_core.wsgi.application'

# Database - SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [  # default ok
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']   # for custom CSS/JS later
STATIC_ROOT = BASE_DIR / 'staticfiles'     # path where collectstatic will store files

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

LOGOUT_REDIRECT_URL = 'home'
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = 'home'
CSRF_USE_SESSIONS = False
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8000',
    'http://localhost:8000',
]



DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom user model (must be set before first migrate!)
AUTH_USER_MODEL = 'users.User'

# Brand the admin panel (Done in urls.py)



# Unfold configuration
UNFOLD = {
    "SITE_TITLE": "SATM Administration",
    "SITE_HEADER": "SATM Admin",
    "SITE_LOGO": None,
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "STYLES": [
        lambda request: "/static/css/custom_admin.css",
    ],
    "COLORS": {
        "primary": {
            "50": "#f0f9ff",
            "100": "#e0f2fe",
            "200": "#bae6fd",
            "300": "#7dd3fc",
            "400": "#38bdf8",
            "500": "#0ea5e9",
            "600": "#0284c7",
            "700": "#0369a1",
            "800": "#075985",
            "900": "#0c4a6e",
            "950": "#082f49",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Main",
                "items": [
                    {
                        "title": "Dashboard",
                        "icon": "dashboard",
                        "link": "/satm-admin/",
                    },
                    {
                        "title": "Generate Timetable",
                        "icon": "auto_awesome",
                        "link": "http://127.0.0.1:8000/dashboard/admin/",
                    },
                ],
            },
            {
                "title": "Authentication",
                "items": [
                    {"title": "Users", "link": "/satm-admin/users/user/", "icon": "person"},
                    {"title": "Groups", "link": "/satm-admin/auth/group/", "icon": "group"},
                    {"title": "Bulk Password Reset", "link": "/satm-admin/users/user/bulk-password-reset/", "icon": "key"},
                ],
            },
            {
                "title": "Timetabling",
                "items": [
                    {"title": "Courses", "link": "/satm-admin/timetabling/course/", "icon": "school"},
                    {"title": "Units", "link": "/satm-admin/timetabling/unit/", "icon": "book"},
                    {"title": "Rooms", "link": "/satm-admin/timetabling/room/", "icon": "meeting_room"},
                    {"title": "Time slots", "link": "/satm-admin/timetabling/timeslot/", "icon": "schedule"},
                ],
            },
        ],
    },
}