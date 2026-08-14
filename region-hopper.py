import random
import sys
import time
from pathlib import Path

import yaml
from psycopg_pool import ConnectionPool

sys.path.append(str(Path(__file__).parent))
import datagen


def load_config() -> dict:
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)

    if "urls" not in config:
        raise RuntimeError("config.yaml is missing required key: urls")

    if not isinstance(config["urls"], dict) or len(config["urls"]) < 2:
        raise RuntimeError("config.yaml 'urls' must map at least 2 tags to connection URLs")

    return config


def main() -> None:
    config = load_config()

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
            prefix = random.choice(datagen.PREFIXES)

            info = datagen.random_info()
            param1 = random.randint(0, 100)
            param2 = round(random.uniform(0, 75), 2)

            try:
                with pools[insert_tag].connection() as conn:
                    cur = conn.execute(
                        "INSERT INTO trailer_global (trailer_number, info) "
                        "VALUES (%s || unique_rowid()::STRING, %s) "
                        "RETURNING trailer_number",
                        (prefix, info),
                    )
                    global_number = cur.fetchone()[0]

                    cur = conn.execute(
                        "INSERT INTO trailer_rbr (trailer_number, param1, param2) "
                        "VALUES (%s || unique_rowid()::STRING, %s, %s) "
                        "RETURNING trailer_number",
                        (prefix, param1, param2),
                    )
                    rbr_number = cur.fetchone()[0]
            except Exception as exc:
                print(f"INSERT via '{insert_tag}' failed: {exc}")
                print("Skipping verification, moving to next iteration.")
                continue

            print(f"INSERT via '{insert_tag}' with prefix '{prefix}'...  OK")
            print(f"trailer_global: {global_number}")
            print(f"trailer_rbr:    {rbr_number}")

            read_start = time.perf_counter()
            with pools[insert_tag].connection() as conn:
                cur = conn.execute(
                    "SELECT crdb_internal_mvcc_timestamp FROM trailer_global "
                    "WHERE trailer_number = %s",
                    (global_number,),
                )
                global_mvcc_ts = cur.fetchone()[0]

                cur = conn.execute(
                    "SELECT crdb_internal_mvcc_timestamp FROM trailer_rbr "
                    "WHERE trailer_number = %s",
                    (rbr_number,),
                )
                rbr_mvcc_ts = cur.fetchone()[0]
            read_ms = (time.perf_counter() - read_start) * 1000

            print(f"Read back via '{insert_tag}': "
                  f"global mvcc_timestamp={global_mvcc_ts}, "
                  f"rbr mvcc_timestamp={rbr_mvcc_ts} ({read_ms:.1f} ms)")

            for tag, pool in pools.items():
                if tag == insert_tag:
                    continue

                verify_start = time.perf_counter()
                with pool.connection() as conn:
                    cur = conn.execute(
                        "SELECT info, crdb_internal_mvcc_timestamp "
                        "FROM trailer_global WHERE trailer_number = %s",
                        (global_number,),
                    )
                    global_record = cur.fetchone()

                    cur = conn.execute(
                        "SELECT param1, param2, crdb_internal_mvcc_timestamp "
                        "FROM trailer_rbr WHERE trailer_number = %s",
                        (rbr_number,),
                    )
                    rbr_record = cur.fetchone()
                verify_ms = (time.perf_counter() - verify_start) * 1000

                if global_record is None:
                    print(f"VERIFICATION FAILED via '{tag}': "
                          f"trailer_global row {global_number} not found")
                    sys.exit(1)

                if global_record[1] != global_mvcc_ts:
                    print(f"VERIFICATION FAILED via '{tag}': trailer_global "
                          f"mvcc_timestamp mismatch: inserted={global_mvcc_ts}, "
                          f"read={global_record[1]}")
                    sys.exit(1)

                if global_record[0] != info:
                    print(f"VERIFICATION FAILED via '{tag}': trailer_global "
                          f"info mismatch: inserted={info!r}, read={global_record[0]!r}")
                    sys.exit(1)

                if rbr_record is None:
                    print(f"VERIFICATION FAILED via '{tag}': "
                          f"trailer_rbr row {rbr_number} not found")
                    sys.exit(1)

                if rbr_record[2] != rbr_mvcc_ts:
                    print(f"VERIFICATION FAILED via '{tag}': trailer_rbr "
                          f"mvcc_timestamp mismatch: inserted={rbr_mvcc_ts}, "
                          f"read={rbr_record[2]}")
                    sys.exit(1)

                if rbr_record[0] != param1 or rbr_record[1] != param2:
                    print(f"VERIFICATION FAILED via '{tag}': trailer_rbr "
                          f"param mismatch: inserted=({param1}, {param2}), "
                          f"read=({rbr_record[0]}, {rbr_record[1]})")
                    sys.exit(1)

                print(f"Verified via '{tag}': mvcc_timestamps and spot columns match "
                      f"({verify_ms:.1f} ms)")

    except KeyboardInterrupt:
        print("Interrupted, closing pools.")
    finally:
        for pool in pools.values():
            pool.close()


if __name__ == "__main__":
    main()
