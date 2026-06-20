from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_NAME = os.getenv("DATABASE_NAME")
PER_PAGE = int(os.getenv("PER_PAGE", "50"))
SUPERUSER_TOKEN = os.getenv("SUPERUSER_TOKEN")