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
        if "prefix" not in args or not isinstance(args["prefix"], list) or len(args["prefix"]) != 2:
            raise RuntimeError("args key 'prefix' must be a list of two prefixes: [local, remote]")
        self.prefix = args["prefix"][0]
        self.prefix_remote = args["prefix"][1]
        self.rows = args.get("rows")

        self.global_numbers = []
        self.rbr_ids = []
        self.rbr_numbers = []


    def setup(self, conn: psycopg.Connection, id: int, total_thread_count: int):
        with conn.cursor() as cur:
            self.region = cur.execute("SELECT gateway_region()").fetchone()[0]

            cur.execute("SELECT region FROM [SHOW REGIONS FROM DATABASE]")
            self.regions = [row[0] for row in cur.fetchall()]

            if self.rows and total_thread_count == 1:
                target = round(self.rows / 2)

                for prefix in datagen.PREFIXES:
                    count = cur.execute(
                        "SELECT count(*) FROM trailer_global WHERE trailer_number LIKE %s",
                        (prefix + "%",),
                    ).fetchone()[0]

                    for start in range(0, target - count, BATCH_SIZE):
                        chunk = min(BATCH_SIZE, target - count - start)
                        values = ", ".join(["(%s || unique_rowid()::STRING, %s)"] * chunk)
                        params = []
                        for _ in range(chunk):
                            params.extend([prefix, datagen.random_info()])
                        cur.execute(
                            f"INSERT INTO trailer_global (trailer_number, info) VALUES {values}",
                            params,
                        )

                    for start in range(0, count - target, BATCH_SIZE):
                        chunk = min(BATCH_SIZE, count - target - start)
                        cur.execute(
                            "DELETE FROM trailer_global WHERE trailer_number LIKE %s LIMIT %s",
                            (prefix + "%", chunk),
                        )

                    count = cur.execute(
                        "SELECT count(*) FROM trailer_rbr WHERE trailer_number LIKE %s",
                        (prefix + "%",),
                    ).fetchone()[0]

                    for start in range(0, target - count, BATCH_SIZE):
                        chunk = min(BATCH_SIZE, target - count - start)
                        values = ", ".join(["(%s || unique_rowid()::STRING, %s, %s)"] * chunk)
                        params = []
                        for _ in range(chunk):
                            params.extend([
                                prefix,
                                random.randint(0, 100),
                                round(random.uniform(0, 75), 2),
                            ])
                        cur.execute(
                            f"INSERT INTO trailer_rbr (trailer_number, param1, param2) VALUES {values}",
                            params,
                        )

                    for start in range(0, count - target, BATCH_SIZE):
                        chunk = min(BATCH_SIZE, count - target - start)
                        cur.execute(
                            "DELETE FROM trailer_rbr WHERE trailer_number LIKE %s LIMIT %s",
                            (prefix + "%", chunk),
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
                self.global_select_info,
                self.rbr_insert,
                self.rbr_update,
                self.rbr_select,
                self.rbr_select_number,
                self.rbr_select_prefix,
                self.rbr_select_prefix_in_region,
                self.rbr_select_prefix_aost,
                self.rbr_select_prefix_remote,
                self.rbr_select_prefix_remote_aost,
                self.rbr_select_param,
                self.rbr_select_param_aost
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


    def global_select_info(self, conn: psycopg.Connection):
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, trailer_number, info FROM trailer_global WHERE info LIKE %s LIMIT 1000",
                ("53ft reefer%",),
            )
            cur.fetchall()


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
                "UPDATE trailer_rbr SET param1 = %s, param2 = %s WHERE id = %s",
                (
                    random.randint(0, 100),
                    round(random.uniform(0, 75), 2),
                    random.choice(self.rbr_ids),
                ),
            )


    def rbr_select(self, conn: psycopg.Connection):
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, trailer_number, param1, param2 FROM trailer_rbr WHERE id = %s",
                (random.choice(self.rbr_ids),),
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


    def rbr_select_prefix_in_region(self, conn: psycopg.Connection):
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, trailer_number, param1, param2 FROM trailer_rbr "
                "WHERE region = %s AND trailer_number LIKE %s LIMIT 1000",
                (self.region, self.prefix + "%")
            )
            cur.fetchall()


    def rbr_select_prefix_aost(self, conn: psycopg.Connection):
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, trailer_number, param1, param2 FROM trailer_rbr "
                "AS OF SYSTEM TIME follower_read_timestamp() "
                "WHERE trailer_number LIKE %s LIMIT 1000",
                (self.prefix + "%",),
            )
            cur.fetchall()


    def rbr_select_prefix_remote(self, conn: psycopg.Connection):
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, trailer_number, param1, param2 FROM trailer_rbr WHERE trailer_number LIKE %s LIMIT 1000",
                (self.prefix_remote + "%",),
            )
            cur.fetchall()


    def rbr_select_prefix_remote_aost(self, conn: psycopg.Connection):
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, trailer_number, param1, param2 FROM trailer_rbr "
                "AS OF SYSTEM TIME follower_read_timestamp() "
                "WHERE trailer_number LIKE %s LIMIT 1000",
                (self.prefix_remote + "%",),
            )
            cur.fetchall()


    def rbr_select_param(self, conn: psycopg.Connection):
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, trailer_number, param1, param2 FROM trailer_rbr WHERE param1 > 5 LIMIT 100",
            )
            cur.fetchall()


    def rbr_select_param_aost(self, conn: psycopg.Connection):
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, trailer_number, param1, param2 FROM trailer_rbr "
                "AS OF SYSTEM TIME follower_read_timestamp() "
                "WHERE param1 > 5 LIMIT 100",
            )
            cur.fetchall()
