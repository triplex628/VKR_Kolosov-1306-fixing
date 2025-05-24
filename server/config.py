# server/config.py

from datetime import timedelta
import os
# Секретный ключ — поменяйте на что-то длинное и случайное
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 300  # время жизни токена в минутах
