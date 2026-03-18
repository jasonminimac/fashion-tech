"""DB connection stub — reads DATABASE_URL from environment."""
import os

DATABASE_URL: str = os.environ.get("DATABASE_URL", "postgresql://localhost/fashiontech")

# TODO: replace with async SQLAlchemy engine in Sprint 2
# from sqlalchemy.ext.asyncio import create_async_engine
# engine = create_async_engine(DATABASE_URL)
