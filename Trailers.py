import random

import psycopg


SEED_LIMIT = 1000
BATCH_SIZE = 1000

REEFER_UNITS = [
    "Carrier X4 7500", "Carrier X4 7300", "Carrier Vector 8600",
    "Carrier Vector 8500", "Thermo King Precedent", "Thermo King C-600",
]

DRY_VAN_ATTRS = [
    "swing doors", "roll door", "e-track interior", "logistics posts",
    "air ride suspension", "liftgate 3000 lb", "load bars x6",
    "spare tire mounted", "floor rated 20k lbs",
]

FLATBED_ATTRS = [
    "tarps onboard", "coil package", "conestoga rolling tarp",
    "chains and binders onboard", "headache rack installed",
    "edge protectors onboard", "lumber tarps", "steel hauling config",
]

CHASSIS_ATTRS = [
    "twist locks OK", "sliding tandem", "DOT sticker current",
    "tires at 60%", "tires at 45%",
]

NOTES = [
    "last DOT inspection", "annual inspection", "brake job due",
    "tires replaced", "door seal replaced", "kingpin inspected",
]


class Trailers:

    def __init__(self, args: dict):
        if "prefix" not in args:
            raise RuntimeError("args is missing required key: prefix")
        self.prefix = args["prefix"]
        self.init = args.get("init")

        self.global_numbers = []
        self.rbr_ids = []


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
                        params.extend([self.prefix, self.random_info()])
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
                "SELECT id FROM trailer_rbr WHERE region = %s LIMIT %s OFFSET %s",
                (self.region, SEED_LIMIT, offset),
            )
            self.rbr_ids.extend(row[0] for row in cur.fetchall())


    def loop(self):
        return [
                self.global_insert,
                self.global_update,
                self.global_select,
                self.rbr_insert,
                self.rbr_update,
                self.rbr_select
            ]


    def random_date(self):
        return f"2026-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"


    def random_info(self):
        trailer_type = random.choice([
            "53ft dry van", "48ft flatbed", "53ft reefer", "40ft container chassis"
        ])

        if trailer_type == "53ft reefer":
            parts = [
                trailer_type,
                random.choice(REEFER_UNITS),
                f"setpoint {random.randint(25, 40)}F",
                f"fuel {random.randint(30, 95)}%",
            ]
        elif trailer_type == "48ft flatbed":
            parts = [trailer_type] + random.sample(FLATBED_ATTRS, 2)
        elif trailer_type == "40ft container chassis":
            parts = [trailer_type] + random.sample(CHASSIS_ATTRS, 2)
        else:
            parts = [trailer_type] + random.sample(DRY_VAN_ATTRS, 2)

        if random.random() < 0.5:
            parts.append(f"{random.choice(NOTES)} {self.random_date()}")

        return ", ".join(parts)


    def global_insert(self, conn: psycopg.Connection):
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO trailer_global (trailer_number, info) VALUES (%s || unique_rowid()::STRING, %s)",
                (self.prefix, self.random_info()),
            )


    def global_update(self, conn: psycopg.Connection):
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE trailer_global SET info = %s WHERE trailer_number = %s",
                (self.random_info(), random.choice(self.global_numbers)),
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
