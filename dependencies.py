import aiomysql

# Database Configuration
DATABASE_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "newuser",
    "password": "hitesh12",
    "db": "leaderboard",
    "autocommit": True,
}

async def create_db_connection():
    pool = await aiomysql.create_pool(**DATABASE_CONFIG)
    db = await pool.acquire()
    yield db
    await pool.release(db)
