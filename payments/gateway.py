import gopay
from django.conf import settings

# Bezpečný fallback – pro každý SDK
try:
    from gopay.enums import Scope
    SCOPE_ALL = Scope.ALL          # starší SDK
except (ImportError, AttributeError):
    SCOPE_ALL = "payment-all"      # novější SDK

def gopay_client():
    return gopay.payments(
        {
            "goid":         settings.GOPAY_GOID,
            "clientId":     settings.GOPAY_CLIENT_ID,
            "clientSecret": settings.GOPAY_CLIENT_SECRET,
            "scope":        SCOPE_ALL,
            "gatewayUrl": (
                "https://gw.sandbox.gopay.com"
                if settings.GOPAY_SANDBOX
                else "https://gate.gopay.cz"
            ),
        }
    )
