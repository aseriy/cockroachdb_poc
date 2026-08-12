CREATE TABLE trailer (
  id             UUID NOT NULL DEFAULT gen_random_uuid(),
  region         crdb_internal_region NOT NULL AS (
                   CASE
                     WHEN trailer_number LIKE 'TRL-EAST-1%' THEN 'aws-us-east-1'
                     WHEN trailer_number LIKE 'TRL-EAST-2%' THEN 'aws-us-east-2'
                     WHEN trailer_number LIKE 'TRL-WEST-2%' THEN 'aws-us-west-2'
                   END
                 ) STORED,
  trailer_number STRING NOT NULL,
  CONSTRAINT pk_trailer PRIMARY KEY (id),
  UNIQUE INDEX uq_trailer_number (trailer_number)
) LOCALITY REGIONAL BY ROW;

CREATE TABLE trailer (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  region         crdb_internal_region NOT NULL AS (
                   CASE
                     WHEN trailer_number LIKE 'TRL-EAST-1%' THEN 'aws-us-east-1'
                     WHEN trailer_number LIKE 'TRL-EAST-2%' THEN 'aws-us-east-2'
                     WHEN trailer_number LIKE 'TRL-WEST-2%' THEN 'aws-us-west-2'
                   END
                 ) STORED,
  trailer_number STRING NOT NULL
) LOCALITY REGIONAL BY ROW AS region;


INSERT INTO trailer (trailer_number) VALUES
  ('TRL-EAST-1-4827'),
  ('TRL-EAST-1-9153'),
  ('TRL-EAST-1-2064'),
  ('TRL-EAST-1-7391'),
  ('TRL-EAST-1-5628'),
  ('TRL-EAST-1-1470'),
  ('TRL-EAST-1-8305'),
  ('TRL-EAST-2-6742'),
  ('TRL-EAST-2-3918'),
  ('TRL-EAST-2-5273'),
  ('TRL-EAST-2-8046'),
  ('TRL-EAST-2-1659'),
  ('TRL-EAST-2-9384'),
  ('TRL-EAST-2-2517'),
  ('TRL-WEST-2-7830'),
  ('TRL-WEST-2-4265'),
  ('TRL-WEST-2-9012'),
  ('TRL-WEST-2-3574'),
  ('TRL-WEST-2-6198'),
  ('TRL-WEST-2-8421');

SELECT region, count(*) FROM trailer GROUP BY region ORDER BY region;

SELECT id, region, trailer_number FROM trailer WHERE trailer_number LIKE 'TRL-WEST%';




INSERT INTO trailer (trailer_number) VALUES
  ('TRL-EAST-1-3047'),('TRL-EAST-1-8215'),('TRL-EAST-1-6390'),('TRL-EAST-1-1728'),
  ('TRL-EAST-1-9564'),('TRL-EAST-1-4102'),('TRL-EAST-1-7836'),('TRL-EAST-1-2459'),
  ('TRL-EAST-1-5981'),('TRL-EAST-1-3623'),('TRL-EAST-1-8074'),('TRL-EAST-1-1395'),
  ('TRL-EAST-1-6748'),('TRL-EAST-1-9027'),('TRL-EAST-1-4581'),('TRL-EAST-1-2136'),
  ('TRL-EAST-1-7492'),('TRL-EAST-1-5308'),('TRL-EAST-1-8659'),('TRL-EAST-1-3874'),
  ('TRL-EAST-1-1063'),('TRL-EAST-1-9418'),('TRL-EAST-1-6725'),('TRL-EAST-1-2807'),
  ('TRL-EAST-1-4936'),('TRL-EAST-1-7150'),('TRL-EAST-1-5472'),('TRL-EAST-1-8903'),
  ('TRL-EAST-1-3261'),('TRL-EAST-1-6584'),('TRL-EAST-1-1849'),('TRL-EAST-1-9736'),
  ('TRL-EAST-1-2093'),('TRL-EAST-1-5617'),
  ('TRL-EAST-2-4728'),('TRL-EAST-2-9051'),('TRL-EAST-2-3396'),('TRL-EAST-2-6842'),
  ('TRL-EAST-2-1574'),('TRL-EAST-2-8209'),('TRL-EAST-2-5063'),('TRL-EAST-2-2735'),
  ('TRL-EAST-2-7481'),('TRL-EAST-2-9628'),('TRL-EAST-2-3157'),('TRL-EAST-2-6014'),
  ('TRL-EAST-2-4892'),('TRL-EAST-2-1360'),('TRL-EAST-2-8546'),('TRL-EAST-2-5729'),
  ('TRL-EAST-2-2483'),('TRL-EAST-2-7095'),('TRL-EAST-2-9312'),('TRL-EAST-2-4607'),
  ('TRL-EAST-2-1938'),('TRL-EAST-2-6251'),('TRL-EAST-2-8764'),('TRL-EAST-2-3520'),
  ('TRL-EAST-2-5186'),('TRL-EAST-2-2947'),('TRL-EAST-2-7803'),('TRL-EAST-2-9475'),
  ('TRL-EAST-2-1092'),('TRL-EAST-2-4318'),('TRL-EAST-2-6679'),('TRL-EAST-2-8231'),
  ('TRL-EAST-2-3865'),
  ('TRL-WEST-2-5240'),('TRL-WEST-2-9683'),('TRL-WEST-2-1417'),('TRL-WEST-2-6052'),
  ('TRL-WEST-2-3798'),('TRL-WEST-2-8365'),('TRL-WEST-2-2609'),('TRL-WEST-2-7124'),
  ('TRL-WEST-2-4571'),('TRL-WEST-2-9836'),('TRL-WEST-2-1250'),('TRL-WEST-2-6493'),
  ('TRL-WEST-2-3017'),('TRL-WEST-2-8742'),('TRL-WEST-2-5169'),('TRL-WEST-2-2384'),
  ('TRL-WEST-2-7906'),('TRL-WEST-2-4638'),('TRL-WEST-2-9051'),('TRL-WEST-2-1573'),
  ('TRL-WEST-2-6820'),('TRL-WEST-2-3495'),('TRL-WEST-2-8107'),('TRL-WEST-2-5762'),
  ('TRL-WEST-2-2938'),('TRL-WEST-2-7451'),('TRL-WEST-2-9284'),('TRL-WEST-2-4016'),
  ('TRL-WEST-2-1839'),('TRL-WEST-2-6527'),('TRL-WEST-2-3160'),('TRL-WEST-2-8473'),
  ('TRL-WEST-2-5698');

  EXPLAIN ANALYZE SELECT id, region, trailer_number FROM trailer WHERE trailer_number LIKE 'TRL-WEST%';

