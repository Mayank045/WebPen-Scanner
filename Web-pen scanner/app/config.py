from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    SECRET_KEY = "dev-secret-change-me"
    DATABASE_PATH = BASE_DIR / "data" / "web_pen_scanner.db"
    JSON_SORT_KEYS = False
