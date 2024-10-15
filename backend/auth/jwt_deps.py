import jwt
import base64
import requests
from fastapi import Depends, HTTPException, Request, status
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import json
from jwt import InvalidTokenError, ExpiredSignatureError
from api.config import V_AZURE_CLIENT_ID, V_AZURE_TENANT_ID
from .memory_cache import cache_set, cache_get, cache_delete


JWKS_URL = f"https://login.microsoftonline.com/{V_AZURE_TENANT_ID}/discovery/v2.0/keys"
CACHE_EXPIRY = 240
security = HTTPBearer()


async def get_signing_keys(kid):
    print(cache_set)
    cache_key = await cache_get(f"JWKS_{kid}")
    print("cache_key", cache_key)
    if cache_key:
        return json.loads(cache_key)
    jwks = requests.get(JWKS_URL).json()
    matching_key = None
    for key in jwks["keys"]:
        if kid == key["kid"]:
            matching_key = key
            await cache_set(f"JWKS_{kid}", json.dumps(key), CACHE_EXPIRY)
            break
    return matching_key


def get_unverified_header(token):
    header_data = token.split(".")[0]
    header_data += "=" * (-len(header_data) % 4)
    header = base64.urlsafe_b64decode(header_data).decode("utf-8")
    return json.loads(header)


async def verify_token(authorization: HTTPAuthorizationCredentials = Depends(security)):
    kid_key = None 
    try:
        token = authorization.credentials
        headers = jwt.get_unverified_header(token)
        kid_key = headers["kid"]
        key = await get_signing_keys(kid_key)
        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
        
        if not public_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token header"
            )
        
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience=V_AZURE_CLIENT_ID,
            issuer=f"https://login.microsoftonline.com/{V_AZURE_TENANT_ID}/v2.0",
        )
        return payload

    except ExpiredSignatureError as ex:
        await cache_delete(f"JWKS_{kid_key}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired!"
        )
    except InvalidTokenError as e:
        await cache_delete(f"JWKS_{kid_key}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token claims"
        )
    except Exception as e:
        await cache_delete(f"JWKS_{kid_key}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to validate token"
        )