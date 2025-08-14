import aiomysql

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "snapcook1234!",
    "db": "airecipe",
}

async def get_db_pool():
    return await aiomysql.create_pool(**DB_CONFIG)
