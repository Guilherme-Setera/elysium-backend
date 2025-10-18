from pydantic import BaseModel, Field, EmailStr

class TokenRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)
    totp_code: str | None = None

class UserOut(BaseModel):
    full_name: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut

class RegisterRequest(BaseModel):
    nome: str = Field(min_length=1)
    email: str = Field(min_length=1)
    senha: str = Field(min_length=6)
    role: str = Field(default="vendedor")

class ChangePasswordRequest(BaseModel):
    user_id: int
    senha_atual: str = Field(min_length=1)
    senha_nova: str = Field(min_length=6)
