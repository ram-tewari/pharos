#!/usr/bin/env python3
"""
Fix authentication issues in production.
"""

# 1. Add token refresh endpoint to backend/app/modules/auth/router.py
TOKEN_REFRESH_ENDPOINT = '''
@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str = Body(..., embed=True),
    db: Session = Depends(get_sync_db)
):
    """Refresh access token using refresh token."""
    try:
        # Validate refresh token
        payload = jwt.decode(
            refresh_token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Get user from database
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Generate new access token
        access_token = create_access_token(
            data={
                "user_id": str(user.id),
                "username": user.username,
                "tier": user.tier,
                "scopes": []
            }
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
'''

# 2. Update token creation to include refresh tokens
UPDATED_TOKEN_CREATION = '''
def create_tokens(user_data: dict) -> dict:
    """Create both access and refresh tokens."""
    access_token = create_access_token(data=user_data)
    
    # Create refresh token with longer expiry
    refresh_data = {
        "user_id": user_data["user_id"],
        "type": "refresh"
    }
    refresh_token = jwt.encode(
        {
            **refresh_data,
            "exp": datetime.utcnow() + timedelta(days=30)  # 30 days
        },
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }
'''

print("1. Add token refresh endpoint to auth router")
print("2. Update frontend to handle token refresh automatically")
print("3. Consider shorter access token expiry (15-30 minutes) with refresh tokens")
