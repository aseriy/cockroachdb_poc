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


