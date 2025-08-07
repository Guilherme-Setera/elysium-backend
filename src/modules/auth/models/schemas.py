from pydantic import BaseModel

class TokenRequest(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    full_name: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut
