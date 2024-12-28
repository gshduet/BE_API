from pydantic import BaseModel, EmailStr


class GoogleSignupRequest(BaseModel):
    email: EmailStr
    name: str
    google_id: str
