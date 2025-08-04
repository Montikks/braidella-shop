from .base import *

DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = os.getenv("SHOP_FROM_EMAIL", "web@example.com")
GOPAY_GOID          = int(os.getenv("GOPAY_GOID",    "8123456789"))
GOPAY_CLIENT_ID     =     os.getenv("GOPAY_CLIENT_ID",     "")
GOPAY_CLIENT_SECRET =     os.getenv("GOPAY_CLIENT_SECRET", "")
GOPAY_SANDBOX       = True