CREATE TABLE trailer_global (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trailer_number      STRING NOT NULL,
    info                STRING DEFAULT NULL
) LOCALITY GLOBAL;

CREATE UNIQUE INDEX ON trailer_global(trailer_number);


CREATE TABLE trailer_rbr (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  region              crdb_internal_region NOT VISIBLE NOT NULL AS (
                          CASE
                              WHEN trailer_number LIKE 'TRL-EAST-%' THEN 'us-east'
                              WHEN trailer_number LIKE 'TRL-WEST-%' THEN 'us-west'
                              ELSE 'us-central'
                          END
                      ) STORED,
  trailer_number      STRING NOT NULL,
  param1              INTEGER DEFAULT 0,
  param2              FLOAT DEFAULT 0.0
) LOCALITY REGIONAL BY ROW AS region;

CREATE UNIQUE INDEX ON trailer_rbr (trailer_number);
CREATE INDEX ON trailer_rbr (param2 DESC);
CREATE INDEX ON trailer_rbr (param2 DESC, trailer_number);


CREATE TABLE public.t_driver (
      id UUID NOT NULL DEFAULT gen_random_uuid(),
      name STRING NOT NULL,
      info STRING NULL,
      CONSTRAINT t_driver_pkey PRIMARY KEY (id ASC)
  ) WITH (schema_locked = true) LOCALITY GLOBAL;


  CREATE TABLE public.t_gate_arr (
      id UUID NOT NULL DEFAULT gen_random_uuid(),
      trailer_id UUID NULL,
      driver_id UUID NULL,
      update_ts TIMESTAMP NULL,
      crdb_region public.crdb_internal_region NOT VISIBLE NOT NULL DEFAULT default_to_database_primary_region(gateway_region())::public.crdb_internal_region,
      CONSTRAINT t_gate_arr_pkey PRIMARY KEY (id ASC),
      CONSTRAINT t_gate_arr_trailer_id_fkey FOREIGN KEY (trailer_id) REFERENCES public.trailer_global(id),
      CONSTRAINT t_gate_arr_driver_id_fkey FOREIGN KEY (driver_id) REFERENCES public.t_driver(id),
      INDEX t_gate_arr_driver_id_update_ts_idx (driver_id ASC, update_ts ASC)
  ) WITH (schema_locked = true) LOCALITY REGIONAL BY ROW;

  CREATE TABLE public.t_appt (
      id UUID NOT NULL DEFAULT gen_random_uuid(),
      trailer_id UUID NULL,
      driver_id UUID NULL,
      update_ts TIMESTAMP NULL,
      crdb_region public.crdb_internal_region NOT VISIBLE NOT NULL DEFAULT default_to_database_primary_region(gateway_region())::public.crdb_internal_region,
      CONSTRAINT t_appt_pkey PRIMARY KEY (id ASC),
      CONSTRAINT t_appt_trailer_id_fkey FOREIGN KEY (trailer_id) REFERENCES public.trailer_global(id),
      CONSTRAINT t_appt_driver_id_fkey FOREIGN KEY (driver_id) REFERENCES public.t_driver(id)
  ) WITH (schema_locked = true) LOCALITY REGIONAL BY ROW;


-- INSERT INTO t_trailer (id) VALUES
--                             ('11111111-1111-1111-1111-111111111111'),
--                             ('22222222-2222-2222-2222-222222222222');

-- INSERT INTO t_driver (id) VALUES
--                             ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'),
--                             ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb');

-- INSERT INTO t_gate_arr (trailer_id, driver_id, update_ts) VALUES
--                                                            ('11111111-1111-1111-1111-111111111111', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '2026-01-01 08:00:00'),
--                                                            ('22222222-2222-2222-2222-222222222222', NULL,                                    '2026-01-02 08:00:00');

-- INSERT INTO t_appt (trailer_id, driver_id, update_ts) VALUES
--                                                        ('11111111-1111-1111-1111-111111111111', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', '2026-01-01 09:00:00'),
--                                                        ('22222222-2222-2222-2222-222222222222', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '2026-01-02 07:00:00');


-- INSERT INTO t_driver (id) SELECT gen_random_uuid() FROM generate_series(1, 500000);
-- INSERT INTO t_trailer (id) SELECT gen_random_uuid() FROM generate_series(1, 100);


-- -- SLOW QUERY
-- EXPLAIN ANALYZE
-- SELECT *
-- FROM t_trailer tr
-- LEFT JOIN t_gate_arr ga ON ga.trailer_id = tr.id
-- LEFT JOIN t_appt ON t_appt.trailer_id = tr.id
-- LEFT JOIN t_driver ON (t_driver.id = t_appt.driver_id AND ga.update_ts < t_appt.update_ts) OR t_driver.id = ga.driver_id;

-- -- REWRITTEN JOIN CONDITION TO SPEED IT UP
-- EXPLAIN ANALYZE
-- SELECT *
-- FROM t_trailer tr
--          LEFT JOIN t_gate_arr ga ON ga.trailer_id = tr.id
--          LEFT JOIN t_appt      ON t_appt.trailer_id = tr.id
--          LEFT JOIN t_driver ON t_driver.id = CASE WHEN ga.update_ts < t_appt.update_ts THEN t_appt.driver_id ELSE ga.driver_id END
