from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_NAME = os.getenv("DATABASE_NAME", "../test.db")
PER_PAGE = 50
SUPERUSER_TOKEN = os.getenv("SUPERUSER_TOKEN", "admin")