import logging
import google.auth
import google.oauth2.id_token
from google.auth.transport.requests import Request
from app.config.settings import settings

logger = logging.getLogger(__name__)

def get_google_auth_headers() -> dict[str, str]:
    if not settings.ENABLE_GOOGLE_AUTH:
        return {}

    try:
        audience = settings.RETRIEVAL_SERVICE_HOST
        auth_req = Request()
        token = google.oauth2.id_token.fetch_id_token(auth_req, audience)
        
        return {"Authorization": f"Bearer {token}"}
    except Exception as e:
        logger.warning(f"Failed to fetch Google ID token: {e}. Proceeding without auth headers.")
        return {}
