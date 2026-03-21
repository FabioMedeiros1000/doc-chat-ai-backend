from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker

from config.env_settings import get_settings


def _build_mysql_url() -> URL:
    settings = get_settings()
    return URL.create(
        "mysql+pymysql",
        username=settings.MYSQL_USER,
        password=settings.MYSQL_PASSWORD,
        host=settings.MYSQL_HOST,
        port=settings.MYSQL_PORT,
        database=settings.MYSQL_DATABASE,
        query={"charset": "utf8mb4"},
    )


engine = create_engine(
    _build_mysql_url(),
    pool_pre_ping=True,
    pool_recycle=3600,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_session():
    return SessionLocal()
