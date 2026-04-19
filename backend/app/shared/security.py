"""
Shared Security Components

Provides reusable security dependencies for API authentication.
Part of the shared kernel - can be imported by any module.

Includes:
- JWT OAuth2 authentication (for user login)
- M2M API Key authentication (for Ronin integration)
- Password hashing utilities
- Token management and revocation
"""

import logging
import os
import time
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from pydantic import BaseModel

from ..config.settings import get_settings

logger = logging.getLogger(__name__)

# OAuth2 scheme for Bearer token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# API Key header scheme for M2M authentication
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)


# ============================================================================
# Data Models
# ============================================================================


class Token(BaseModel):
    """OAuth2 token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Data extracted from JWT token."""

    user_id: str  # UUID as string
    username: str
    scopes: list[str] = []
    tier: str = "free"  # free, premium, admin


# ============================================================================
# Password Hashing Functions (using bcrypt directly)
# ============================================================================


def get_password_hash(password: str) -> str:
    """Hash password using bcrypt.

    Args:
        password: Plain text password to hash

    Returns:
        Hashed password string
    """
    # Truncate password to 72 bytes (bcrypt limit)
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against

    Returns:
        True if password matches hash, False otherwise
    """
    try:
        # Truncate password to 72 bytes (bcrypt limit)
        password_bytes = plain_password.encode('utf-8')[:72]
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False


# ============================================================================
# JWT Token Functions
# ============================================================================


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token.

    Args:
        data: Token payload (user_id, username, scopes, tier)
        expires_delta: Token expiration time (optional)

    Returns:
        Encoded JWT token
    """
    settings = get_settings()
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY.get_secret_value(),
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token.

    Args:
        data: Token payload (user_id, username)

    Returns:
        Encoded JWT refresh token
    """
    settings = get_settings()
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY.get_secret_value(),
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def decode_token(token: str) -> dict:
    """Decode and validate JWT token.

    Args:
        token: JWT token to decode

    Returns:
        Decoded token payload

    Raises:
        JWTError: If token is invalid or expired
    """
    settings = get_settings()

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY.get_secret_value(),
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError as e:
        logger.warning(f"JWT validation error: {e}")
        raise


def validate_token_type(payload: dict, expected_type: str) -> bool:
    """Validate token type (access vs refresh).

    Args:
        payload: Decoded token payload
        expected_type: Expected token type ("access" or "refresh")

    Returns:
        True if token type matches, False otherwise
    """
    token_type = payload.get("type")
    return token_type == expected_type


def validate_redirect_url(url: str) -> bool:
    """Validate OAuth2 redirect URL for security.

    Args:
        url: Redirect URL to validate

    Returns:
        True if URL is valid, False otherwise
    """
    # Simple validation - can be enhanced based on requirements
    if not url:
        return False
    # Add more validation as needed (e.g., whitelist of domains)
    return url.startswith(("http://localhost", "https://"))


# ============================================================================
# Token Revocation Functions
# ============================================================================


async def is_token_revoked(token: str) -> bool:
    """Check if token is in revocation list.

    Args:
        token: JWT token to check

    Returns:
        True if token is revoked, False otherwise
    """
    try:
        from .cache import cache

        revoked = cache.get(f"revoked_token:{token}")
        return revoked is not None
    except Exception as e:
        logger.error(f"Error checking token revocation: {e}")
        # Fail open - if we can't check revocation, allow the token
        return False


async def revoke_token(token: str, ttl: int = 86400) -> None:
    """Add token to revocation list.

    Args:
        token: JWT token to revoke
        ttl: Time-to-live for revocation entry in seconds (default: 24 hours)
    """
    try:
        from .cache import cache

        cache.set(f"revoked_token:{token}", "revoked", ttl=ttl)
        logger.info(f"Token revoked: {token[:20]}...")
    except Exception as e:
        logger.error(f"Error revoking token: {e}")
        # Log error but don't raise - revocation is best-effort


# ============================================================================
# FastAPI OAuth2 Authentication Dependency
# ============================================================================

# Token cache to avoid repeated validation (in-memory cache with 60s TTL)
_token_cache: dict[str, tuple[TokenData, float]] = {}
_TOKEN_CACHE_TTL = 60  # seconds


async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    """Validate JWT token and extract user data.

    This is a FastAPI dependency that validates the Bearer token from the
    Authorization header and returns the user data from the token.
    
    Supports:
    - JWT tokens (OAuth2 user authentication)
    - Admin token (PHAROS_ADMIN_TOKEN for admin access)
    
    Performance: Tokens are cached for 60 seconds to avoid repeated validation.

    Args:
        token: JWT token from Authorization header

    Returns:
        TokenData with user information

    Raises:
        HTTPException: 401 if token is invalid, expired, or revoked
    """
    # Check for admin token first
    admin_token = os.getenv("PHAROS_ADMIN_TOKEN")
    if admin_token and token == admin_token:
        logger.info("Admin token authentication successful")
        return TokenData(
            user_id="admin",
            username="admin",
            scopes=["admin"],
            tier="admin",
        )
    
    # Check cache first (significant performance improvement)
    current_time = time.time()
    if token in _token_cache:
        cached_data, cache_time = _token_cache[token]
        if current_time - cache_time < _TOKEN_CACHE_TTL:
            # Cache hit - return cached user data
            return cached_data
        else:
            # Cache expired - remove from cache
            del _token_cache[token]
    
    settings = get_settings()

    # Bypass authentication in test mode
    if settings.is_test_mode or settings.TEST_MODE:
        logger.info("TEST_MODE enabled - bypassing authentication")
        # In test mode, still decode the token to get actual user data
        try:
            payload = decode_token(token)
            user_id = payload.get("user_id")
            username = payload.get("username")
            tier = payload.get("tier", "free")
            return TokenData(user_id=user_id, username=username, scopes=[], tier=tier)
        except Exception:
            # Fallback for invalid tokens in test mode
            return TokenData(user_id="1", username="test_user", scopes=[], tier="free")

    # Structured error response for invalid/expired tokens (HTTP 401)
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Check if token is revoked (only if not in cache)
        if await is_token_revoked(token):
            logger.warning(
                f"Authentication failure: Revoked token used - {token[:20]}..."
            )
            raise credentials_exception

        # Decode and validate token
        payload = decode_token(token)

        # Extract user data
        user_id: Optional[str] = payload.get("user_id")
        username: Optional[str] = payload.get("username")
        token_type: Optional[str] = payload.get("type")

        # Validate required fields
        if user_id is None or username is None:
            logger.warning(
                "Authentication failure: Token missing required fields (user_id or username)"
            )
            raise credentials_exception

        # Validate token type
        if token_type != "access":
            logger.warning(
                f"Authentication failure: Invalid token type '{token_type}' (expected: access)"
            )
            raise credentials_exception

        # Create TokenData
        token_data = TokenData(
            user_id=user_id,
            username=username,
            scopes=payload.get("scopes", []),
            tier=payload.get("tier", "free"),
        )
        
        # Cache the validated token data
        _token_cache[token] = (token_data, current_time)
        
        # Clean up old cache entries (simple cleanup every 100 validations)
        if len(_token_cache) > 1000:
            # Remove expired entries
            expired_tokens = [
                t for t, (_, cache_time) in _token_cache.items()
                if current_time - cache_time >= _TOKEN_CACHE_TTL
            ]
            for t in expired_tokens:
                del _token_cache[t]

        return token_data

    except JWTError as e:
        logger.warning(f"Authentication failure: JWT validation error - {e}")
        raise credentials_exception
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Authentication failure: Unexpected error - {e}")
        raise credentials_exception


# ============================================================================
# M2M API Key Authentication (for Ronin Integration)
# ============================================================================


def get_pharos_api_key() -> str:
    """
    Get the Pharos API key from environment variable.

    Returns:
        str: The API key

    Raises:
        RuntimeError: If PHAROS_API_KEY is not set
    """
    api_key = os.environ.get("PHAROS_API_KEY")
    if not api_key:
        raise RuntimeError(
            "PHAROS_API_KEY environment variable is not set. "
            "This is required for M2M authentication."
        )
    return api_key


def _constant_time_compare(a: str, b: str) -> bool:
    """
    Compare two strings in constant time to prevent timing attacks.

    Args:
        a: First string
        b: Second string

    Returns:
        bool: True if strings are equal, False otherwise
    """
    import secrets
    return secrets.compare_digest(a, b)


async def verify_api_key(
    authorization: Optional[str] = Security(api_key_header),
) -> str:
    """
    Verify API key for M2M (Machine-to-Machine) authentication.

    This dependency validates the API key from the Authorization header.
    Supports both raw keys and Bearer token format.

    Args:
        authorization: Authorization header value (injected by FastAPI)

    Returns:
        str: The validated API key

    Raises:
        HTTPException: 403 Forbidden if key is missing or invalid
    """
    # Check if authorization header is present
    if not authorization:
        logger.warning(
            "API key authentication failed: Missing Authorization header"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing API key. Include 'Authorization: Bearer <key>' header.",
        )

    # Strip "Bearer " prefix if present (case-insensitive)
    api_key = authorization
    if authorization.lower().startswith("bearer "):
        api_key = authorization[7:].strip()

    # Validate against environment variable
    try:
        expected_key = get_pharos_api_key()
    except RuntimeError as e:
        logger.error(f"API key validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server configuration error. Contact administrator.",
        )

    # Constant-time comparison to prevent timing attacks
    if not _constant_time_compare(api_key, expected_key):
        logger.warning(
            f"API key authentication failed: Invalid key provided "
            f"(length: {len(api_key)}, expected: {len(expected_key)})"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key. Access denied.",
        )

    logger.info(
        f"API key authentication successful (key length: {len(api_key)})"
    )

    return api_key


def is_valid_api_key(api_key: str) -> bool:
    """
    Check if an API key is valid (for testing purposes).

    Args:
        api_key: API key to validate

    Returns:
        bool: True if valid, False otherwise
    """
    try:
        expected_key = get_pharos_api_key()
        return _constant_time_compare(api_key, expected_key)
    except RuntimeError:
        return False


async def verify_api_key_optional(
    authorization: Optional[str] = Security(api_key_header),
) -> Optional[str]:
    """
    Optional API key verification for development/testing.

    Args:
        authorization: Authorization header value (injected by FastAPI)

    Returns:
        Optional[str]: The validated API key, or None if not provided

    Raises:
        HTTPException: 403 Forbidden if key is provided but invalid
    """
    if not authorization:
        logger.debug("API key not provided (optional mode)")
        return None

    return await verify_api_key(authorization)
