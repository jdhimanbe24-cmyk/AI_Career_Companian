import os
from dotenv import load_dotenv

load_dotenv()

# Render's Postgres (and most managed Postgres providers) expose a single
# connection string rather than separate host/port/user/password fields.
DATABASE_URL = os.getenv("DATABASE_URL")

SECRET_KEY = os.getenv("SECRET_KEY")
