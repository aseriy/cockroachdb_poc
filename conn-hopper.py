import json
import random
import string
import sys
import time
import uuid
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

import yaml
from psycopg_pool import ConnectionPool

FIRST_NAMES = [
    "James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael",
    "Linda", "David", "Elizabeth", "William", "Barbara", "Richard", "Susan",
    "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
    "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
]

EMAIL_DOMAINS = ["example.com", "mail.test", "fleetmail.net", "carrier.io"]


def _rand_digits(n):
    """Random n-digit integer with no leading zero."""
    return int(str(random.randint(1, 9)) + "".join(random.choices(string.digits, k=n - 1)))


def _rand_date(start_year, end_year):
    start = date(start_year, 1, 1).toordinal()
    end = date(end_year, 12, 31).toordinal()
    return date.fromordinal(random.randint(start, end))


def _rand_ts(days_back=1825):
    return datetime(2020, 1, 1) + timedelta(
        days=random.randint(0, days_back),
        seconds=random.randint(0, 86399),
        microseconds=random.randint(0, 999999),
    )


def generate_driver_row(as_json=False):
    """
    Generate one random row for public.driver.

    Returns a dict (JSON object) keyed by column name, with values already
    coerced to JSON-serializable types:
      - numeric  -> int / float
      - date     -> 'YYYY-MM-DD'
      - timestamp-> 'YYYY-MM-DD HH:MM:SS.ffffff'
      - nullable columns may be None

    Set as_json=True to get a JSON string instead of a dict.
    """
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)

    create_ts = _rand_ts()
    update_ts = create_ts + timedelta(seconds=random.randint(0, 60 * 60 * 24 * 365))

    create_user = f"usr{_rand_digits(5)}"

    row = {
        # numeric(10) NOT NULL PRIMARY KEY
        "driver_number": _rand_digits(10),

        # varchar(20)
        "driver_id": f"DRV-{uuid.uuid4().hex[:12].upper()}",

        # varchar(100)
        "driver_first_name": first,
        "driver_last_name": last,

        # STRING — 10-digit phone
        "driver_contct_number": str(_rand_digits(10)),

        # varchar(230)
        "driver_label": f"{last}, {first} - Unit {random.randint(100, 9999)}",

        # date
        "birth_date": _rand_date(1955, 2005).isoformat(),

        # char(1)
        "issue_flag": random.choice(["Y", "N"]),

        # varchar(256), nullable
        "cmnt_text": random.choice([
            None,
            "Auto-generated test record.",
            "Pending license verification.",
            "Endorsement renewal on file.",
            "No comments.",
        ]),

        # varchar(20)
        "trctr_licence": "".join(random.choices(string.ascii_uppercase, k=2))
                         + str(_rand_digits(8)),

        # numeric
        "status_sysid": random.choice([1, 2, 3, 4, 9]),

        # varchar(100)
        "email_addr": f"{first.lower()}.{last.lower()}{random.randint(1, 999)}"
                      f"@{random.choice(EMAIL_DOMAINS)}",

        # timestamp NOT NULL
        "create_ts": create_ts.isoformat(sep=" "),
        # varchar(30) NOT NULL
        "create_userid": create_user,
        # timestamp NOT NULL
        "update_ts": update_ts.isoformat(sep=" "),
        # varchar(30) NOT NULL
        "update_userid": random.choice([create_user, f"usr{_rand_digits(5)}"]),

        # numeric
        "ver_number": random.randint(1, 25),

        # varchar(36) — UUID string is exactly 36 chars
        "vector_driver_id": str(uuid.uuid4()),

        # text NOT NULL UNIQUE
        "phenix_id": f"PHX-{uuid.uuid4()}",
    }

    return json.dumps(row) if as_json else row


def db_value_to_json(value):
    """Coerce a DB-returned value to the same JSON-serializable form
    generate_driver_row() produces."""
    if isinstance(value, Decimal):
        return int(value)
    if isinstance(value, datetime):
        if value.tzinfo is not None:
            value = value.astimezone(timezone.utc).replace(tzinfo=None)
        return value.isoformat(sep=" ")
    if isinstance(value, date):
        return value.isoformat()
    return value


def load_config() -> dict:
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)

    for key in ("table", "pk_column", "urls"):
        if key not in config:
            raise RuntimeError(f"config.yaml is missing required key: {key}")

    if not isinstance(config["urls"], dict) or len(config["urls"]) < 2:
        raise RuntimeError("config.yaml 'urls' must map at least 2 tags to connection URLs")

    return config


def main() -> None:
    config = load_config()
    table = config["table"]
    pk_column = config["pk_column"]

    pools = {
        tag: ConnectionPool(url, min_size=1, open=True)
        for tag, url in config["urls"].items()
    }

    iteration = 0
    try:
        while True:
            iteration += 1
            print()
            print(f"=== Iteration {iteration} ===")

            insert_tag = random.choice(list(pools))
            row = generate_driver_row()
            columns = list(row.keys())
            pk_value = row[pk_column]

            print("Generated row:")
            print(json.dumps(row, indent=2))

            insert_sql = (
                f"INSERT INTO {table} ({', '.join(columns)}) "
                f"VALUES ({', '.join(['%s'] * len(columns))})"
            )
            try:
                with pools[insert_tag].connection() as conn:
                    conn.execute(insert_sql, tuple(row[c] for c in columns))
            except Exception as exc:
                print(f"INSERT via '{insert_tag}' failed: {exc}")
                print("Skipping verification, moving to next iteration.")
                continue

            print(f"INSERT via '{insert_tag}'...  OK")

            read_start = time.perf_counter()
            with pools[insert_tag].connection() as conn:
                cur = conn.execute(
                    f"SELECT crdb_internal_mvcc_timestamp FROM {table} "
                    f"WHERE {pk_column} = %s",
                    (pk_value,),
                )
                mvcc_ts = cur.fetchone()[0]
            read_ms = (time.perf_counter() - read_start) * 1000

            print(f"Read back via '{insert_tag}': mvcc_timestamp={mvcc_ts} ({read_ms:.1f} ms)")

            spot_column = random.choice([c for c in columns if c != pk_column])
            print(f"Spot check column '{spot_column}' = {row[spot_column]!r}")

            for tag, pool in pools.items():
                if tag == insert_tag:
                    continue

                verify_start = time.perf_counter()
                with pool.connection() as conn:
                    cur = conn.execute(
                        f"SELECT {spot_column}, crdb_internal_mvcc_timestamp "
                        f"FROM {table} WHERE {pk_column} = %s",
                        (pk_value,),
                    )
                    record = cur.fetchone()
                verify_ms = (time.perf_counter() - verify_start) * 1000

                if record is None:
                    print(f"VERIFICATION FAILED via '{tag}': "
                          f"row {pk_column}={pk_value} not found")
                    sys.exit(1)

                spot_value, verify_mvcc_ts = record

                if verify_mvcc_ts != mvcc_ts:
                    print(f"VERIFICATION FAILED via '{tag}': mvcc_timestamp mismatch: "
                          f"inserted={mvcc_ts}, read={verify_mvcc_ts}")
                    sys.exit(1)

                if db_value_to_json(spot_value) != row[spot_column]:
                    print(f"VERIFICATION FAILED via '{tag}': column '{spot_column}' mismatch: "
                          f"inserted={row[spot_column]!r}, read={spot_value!r}")
                    sys.exit(1)

                print(f"Verified via '{tag}': mvcc_timestamp and '{spot_column}' match "
                      f"({verify_ms:.1f} ms)")

    except KeyboardInterrupt:
        print("Interrupted, closing pools.")
    finally:
        for pool in pools.values():
            pool.close()


if __name__ == "__main__":
    main()
