from db import get_db_pool
import aiomysql

class UserService:
    async def get_users(self):
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute("""
                    SELECT u.user_id, u.ko_name, u.email, 
                           d.height, d.weight, d.preferred_food, d.preferred_tags
                    FROM user u
                    LEFT JOIN user_detail d ON u.user_id = d.user_id
                """)
                return await cur.fetchall()

    async def get_one_user(self, user_id: str):
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute("""
                    SELECT u.user_id, u.ko_name, u.email, d.height, d.weight, 
                           d.preferred_food, d.preferred_tags, d.birth_date
                    FROM user u
                    LEFT JOIN user_detail d ON u.user_id = d.user_id
                    WHERE u.user_id = %s
                """, (user_id,))
                return await cur.fetchone()

    async def sign_in(self, user_info):
        user_id = user_info.get("user_id")
        pw = user_info.get("pw")
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute("SELECT * FROM user WHERE user_id=%s", (user_id,))
                user = await cur.fetchone()
                if not user:
                    raise Exception("Invalid User ID")
                if user["pw"] != pw:  # TODO: 실제 서비스에서는 암호화 처리
                    raise Exception("Wrong Password")
                return {
                    "user_id": user["user_id"],
                    "ko_name": user["ko_name"],
                    "email": user["email"]
                }

    async def sign_up(self, user_info):
        user_id = user_info.get("user_id")
        pw = user_info.get("pw")
        ko_name = user_info.get("ko_name")
        email = user_info.get("email")
        birth_date = user_info.get("birth_date")
        height = user_info.get("height")
        weight = user_info.get("weight")
        preferred_food = user_info.get("preferred_food")
        preferred_tags = user_info.get("preferred_tags")

        pool = await get_db_pool()
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute("SELECT * FROM user WHERE user_id=%s", (user_id,))
                user = await cur.fetchone()
                if user:
                    raise Exception("User ID already exists")

                await cur.execute("""
                    INSERT INTO user (user_id, pw, ko_name, email)
                    VALUES (%s, %s, %s, %s)
                """, (user_id, pw, ko_name, email))
                await conn.commit()

                if any([height, weight, birth_date, preferred_food, preferred_tags]):
                    await cur.execute("""
                        INSERT INTO user_detail(user_id, height, weight, birth_date, preferred_food, preferred_tags)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (user_id, height, weight, birth_date, preferred_food, preferred_tags))
                    await conn.commit()

                return {
                    "user_id": user_id,
                    "ko_name": ko_name,
                    "email": email,
                    "detail": {
                        "height": height,
                        "weight": weight,
                        "birth_date": birth_date,
                        "preferred_food": preferred_food,
                        "preferred_tags": preferred_tags,
                    }
                }

    async def update_user(self, user_id: str, update_info):
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute("""
                    UPDATE user 
                    SET ko_name=%s, email=%s
                    WHERE user_id=%s
                """, (
                    update_info.get("ko_name"),
                    update_info.get("email"),
                    user_id,
                ))

                await cur.execute("""
                    UPDATE user_detail 
                    SET height=%s, weight=%s, birth_date=%s, preferred_food=%s, preferred_tags=%s
                    WHERE user_id=%s
                """, (
                    update_info.get("height"),
                    update_info.get("weight"),
                    update_info.get("birth_date"),
                    update_info.get("preferred_food"),
                    update_info.get("preferred_tags"),
                    user_id,
                ))

                await conn.commit()
                return {"msg": "회원 정보 수정 완료"}
