from auth.jwt_deps import verify_token
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from api.dependencies.model_utils import get_db


def get_current_user(token: str = Depends(verify_token), db: Session = Depends(get_db)):
    try:
        user_name = token.get("name")
        user_email = token.get("email")
        if user_email:
            username, domain_name = user_email.split('@')
        else:
            raise HTTPException(status_code=400, detail="Invalid access token: Email not found in token")

        return {"user_name":user_name , "user_email": user_email}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: JWT decode token failed" + str(e))
