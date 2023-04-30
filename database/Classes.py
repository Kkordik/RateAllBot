from datetime import date
from config import DATABASE_FILE, BOT_TOKEN, DEFAULT_LANG, HOST, USER, PSWD, DB_NAME, FAKE_USER_ID, PORT
import aiomysql
import random
import asyncio


async def reg_db_pool(loop):
    pool = await aiomysql.create_pool(host=HOST, port=PORT,
                                      user=USER, password=PSWD,
                                      db=DB_NAME, autocommit=False)

    return pool

if __name__ == 'database.Classes':
    loop = asyncio.get_event_loop()
    pool = loop.run_until_complete(reg_db_pool(loop))


class UserDb:
    def __init__(self, userid):
        self.userid = userid
        self.lang = None
        self.new_user = True

    async def search_add_user(self):
        try:
            select_user = "SELECT * FROM users WHERE user_id = {}".format(self.userid)
            insert_user = "INSERT IGNORE INTO users (user_id, language) VALUES ({}, '{}')".format(
                self.userid, DEFAULT_LANG)

            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(select_user)
                    user_db = await cur.fetchone()
                    if user_db is None:
                        await cur.execute(insert_user)
                        self.lang = DEFAULT_LANG
                await conn.commit()

            if user_db is not None:
                self.lang = user_db[1]
                self.new_user = False

        except Exception as ex:
            print("Connection refused...")
            print(ex)

    async def insert_language(self, language):
        try:
            self.lang = language
            update_user = "UPDATE users SET language = '{}' WHERE user_id = {}".format(self.lang, self.userid)

            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(update_user)
                await conn.commit()

        except Exception as ex:
            print("Connection refused...")
            print(ex)


class ObjectDb:
    def __init__(self, objectid, obj_type=None):
        self.objectid = objectid
        self.obj_type = obj_type
        self.new_obj = True

    async def search_add_obj(self):
        try:
            select_object = "SELECT * FROM rate_objects WHERE object_id = {}".format(self.objectid)
            insert_object = "INSERT IGNORE INTO rate_objects (object_id, object_type) VALUES ({}, '{}')".format(
                self.objectid, self.obj_type)

            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(select_object)
                    object_db = await cur.fetchone()
                    if object_db is None:
                        await cur.execute(insert_object)
                await conn.commit()

            if object_db is not None:
                self.obj_type = object_db[1]
                self.new_obj = False

        except Exception as ex:
            print("Connection refused...")
            print(ex)

    async def insert_rate(self, user_id, rate):
        try:
            insert_rate = "INSERT INTO rates(user_id, object_id, rate, datetime) VALUES ({}, {}, {}, now())".format(
                user_id, self.objectid, rate)

            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(insert_rate)
                await conn.commit()

        except Exception as ex:
            print("Connection refused...")
            print(ex)

    async def create_fake_rates(self, subs_numb=None):
        print("fake rates ", self.objectid, " subs_numb = ", subs_numb, " obj_type = ", self.obj_type)
        if self.obj_type in ["group", "supergroup"] and subs_numb is not None:
            subs_numb = int(subs_numb)
            rates_numb = round((subs_numb / 1000) ** 0.5) + 1
        elif self.obj_type == "channel" and subs_numb is not None:
            subs_numb = int(subs_numb)
            rates_numb = round((subs_numb / 5000) ** 0.5)
        elif self.obj_type == "user":
            rates_numb = random.choice([0, 0, 0, 1])
        else:
            rates_numb = random.choice([0, random.randint(1, 3), random.randint(1, 5)])

        for i in range(rates_numb):
            rate = random.randint(3, 5)
            await self.insert_rate(FAKE_USER_ID, rate)

    async def get_rate(self, user_id):
        try:
            select_rates_numb = "SELECT COUNT(rate) FROM rates WHERE object_id = {}".format(self.objectid)
            select_rate = "SELECT AVG(rate) FROM rates WHERE object_id = {}".format(self.objectid)
            select_user_left_rate = "SELECT rate FROM rates WHERE user_id = {} AND object_id = {}".format(
                user_id, self.objectid)
            print(user_id, " get rate  ", self.objectid)
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(select_rates_numb)
                    rates_numb = await cur.fetchone()
                    await cur.execute(select_rate)
                    rate = await cur.fetchone()
                    await cur.execute(select_user_left_rate)
                    user_left_rate = await cur.fetchone()
                    await cur.close()
                await conn.commit()

            return rates_numb, rate, user_left_rate
        except Exception as ex:
            print("Connection refused...")
            print(ex)

    async def delete_rate(self, user_id):
        try:
            select_rates_numb = "DELETE FROM rates WHERE object_id = {} AND user_id = {}".format(self.objectid,
                                                                                                 user_id)

            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(select_rates_numb)
                await conn.commit()

        except Exception as ex:
            print("Connection refused...")
            print(ex)
