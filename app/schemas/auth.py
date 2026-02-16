# Pydantic schemas for authentication flows.

from pydantic import BaseModel


class Token(BaseModel):
	access_token: str
	token_type: str = "bearer"
	refresh_token: str | None = None


class TokenPayload(BaseModel):
	sub: str


class LoginRequest(BaseModel):
	email: str
	password: str


class RefreshRequest(BaseModel):
	refresh_token: str
