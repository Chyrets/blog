from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash


SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")
optional_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token", auto_error=False)