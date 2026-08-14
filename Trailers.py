import random
import sys
from pathlib import Path

import psycopg

sys.path.append(str(Path(__file__).parent))
import datagen


SEED_LIMIT = 1000
BATCH_SIZE = 1000


class Trailers:

    def __init__(self, args: dict):
        if "prefix" not in args:
            raise RuntimeError("args is missing required key: prefix")
        self.prefix = args["prefix"]
        self.init = args.get("init")

        self.global_numbers = []
        self.rbr_ids = []
        self.rbr_numbers = []


    def setup(self, conn: psycopg.Connection, id: int, total_thread_count: int):
        with conn.cursor() as cur:
            self.region = cur.execute("SELECT gateway_region()").fetchone()[0]

            cur.execute("SELECT region FROM [SHOW REGIONS FROM DATABASE]")
            self.regions = [row[0] for row in cur.fetchall()]

            if self.init:
                share = round(self.init / total_thread_count)

                for start in range(0, share, BATCH_SIZE):
                    chunk = min(BATCH_SIZE, share - start)

                    values = ", ".join(["(%s || unique_rowid()::STRING, %s)"] * chunk)
                    params = []
                    for _ in range(chunk):
                        params.extend([self.prefix, datagen.random_info()])
                    cur.execute(
                        f"INSERT INTO trailer_global (trailer_number, info) VALUES {values}",
                        params,
                    )

                    values = ", ".join(["(%s || unique_rowid()::STRING, %s, %s)"] * chunk)
                    params = []
                    for _ in range(chunk):
                        params.extend([
                            self.prefix,
                            random.randint(0, 100),
                            round(random.uniform(0, 75), 2),
                        ])
                    cur.execute(
                        f"INSERT INTO trailer_rbr (trailer_number, param1, param2) VALUES {values}",
                        params,
                    )

            count = cur.execute("SELECT count(*) FROM trailer_global").fetchone()[0]
            offset = random.randint(0, max(0, count - SEED_LIMIT))
            cur.execute(
                "SELECT trailer_number FROM trailer_global LIMIT %s OFFSET %s",
                (SEED_LIMIT, offset),
            )
            self.global_numbers.extend(row[0] for row in cur.fetchall())

            count = cur.execute(
                "SELECT count(*) FROM trailer_rbr WHERE region = %s",
                (self.region,),
            ).fetchone()[0]
            offset = random.randint(0, max(0, count - SEED_LIMIT))
            cur.execute(
                "SELECT id, trailer_number FROM trailer_rbr WHERE region = %s LIMIT %s OFFSET %s",
                (self.region, SEED_LIMIT, offset),
            )
            for row in cur.fetchall():
                self.rbr_ids.append(row[0])
                self.rbr_numbers.append(row[1])


    def loop(self):
        return [
                self.global_insert,
                self.global_update,
                self.global_select,
                self.rbr_insert,
                self.rbr_update,
                self.rbr_select,
                self.rbr_select_number,
                self.rbr_select_prefix
            ]


    def global_insert(self, conn: psycopg.Connection):
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO trailer_global (trailer_number, info) VALUES (%s || unique_rowid()::STRING, %s)",
                (self.prefix, datagen.random_info()),
            )


    def global_update(self, conn: psycopg.Connection):
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE trailer_global SET info = %s WHERE trailer_number = %s",
                (datagen.random_info(), random.choice(self.global_numbers)),
            )


    def global_select(self, conn: psycopg.Connection):
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, trailer_number, info FROM trailer_global WHERE trailer_number = %s",
                (random.choice(self.global_numbers),),
            )
            cur.fetchone()


    def rbr_insert(self, conn: psycopg.Connection):
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO trailer_rbr (trailer_number, param1, param2) VALUES (%s || unique_rowid()::STRING, %s, %s)",
                (
                    self.prefix,
                    random.randint(0, 100),
                    round(random.uniform(0, 75), 2),
                ),
            )


    def rbr_update(self, conn: psycopg.Connection):
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE trailer_rbr SET param1 = %s, param2 = %s WHERE region = %s AND id = %s",
                (
                    random.randint(0, 100),
                    round(random.uniform(0, 75), 2),
                    self.region,
                    random.choice(self.rbr_ids),
                ),
            )


    def rbr_select(self, conn: psycopg.Connection):
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, trailer_number, param1, param2 FROM trailer_rbr WHERE region = %s AND id = %s",
                (self.region, random.choice(self.rbr_ids)),
            )
            cur.fetchone()


    def rbr_select_number(self, conn: psycopg.Connection):
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, trailer_number, param1, param2 FROM trailer_rbr WHERE trailer_number = %s",
                (random.choice(self.rbr_numbers),),
            )
            cur.fetchone()


    def rbr_select_prefix(self, conn: psycopg.Connection):
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, trailer_number, param1, param2 FROM trailer_rbr WHERE trailer_number LIKE %s LIMIT 1000",
                (self.prefix + "%",),
            )
            cur.fetchall()
