# production/database/db.py

import os
import asyncpg
from dotenv import load_dotenv

load_dotenv()

async def get_pool():
    """Get database connection pool"""
    db_url = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://nur_scents_user:nur_scents_pass@localhost:5432/nur_scents_db"
    )

    # Convert to asyncpg format
    db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")

    return await asyncpg.create_pool(
        db_url,
        min_size=5,
        max_size=20,
        command_timeout=60
    )
