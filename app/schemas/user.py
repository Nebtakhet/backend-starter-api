# Pydantic schemas for user data exchange.

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


def validate_password_policy(value: str) -> str:
    if len(value) < 12:
        raise ValueError("Password must be at least 12 characters long")
    if not any(char.islower() for char in value):
        raise ValueError("Password must include at least one lowercase letter")
    if not any(char.isupper() for char in value):
        raise ValueError("Password must include at least one uppercase letter")
    if not any(char.isdigit() for char in value):
        raise ValueError("Password must include at least one number")
    if not any(not char.isalnum() for char in value):
        raise ValueError("Password must include at least one special character")
    if any(char.isspace() for char in value):
        raise ValueError("Password must not contain spaces")
    return value


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return validate_password_policy(value)


class UserPasswordChange(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, value: str) -> str:
        return validate_password_policy(value)


class UserOut(UserBase):
    id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
