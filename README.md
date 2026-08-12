# Data Locality

```sql
ALTER DATABASE uscs SET PRIMARY REGION tx1;
ALTER DATABASE uscs ADD REGION tx2;
ALTER DATABASE uscs ADD REGION tx3;
ALTER DATABASE uscs SURVIVE REGION FAILURE;
```

## Global Tables

Choose this option for a table if

1. it needs to be optimized for fast reading in all regions
2. `INSERT`s, `UPDATE`s and `DELETE`s happen infrequently or even ocassionally
3. slightly increased write latency can be tolerated


Create a table:

```sql
CREATE TABLE trailer_global (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trailer_number      STRING NOT NULL,
    info                STRING DEFAULT NULL
) LOCALITY GLOBAL;
```

and populate it:

```sql
INSERT INTO trailer_global (trailer_number, info) VALUES
  ('TRL-EAST-1-3047','53ft dry van, reefer unit N/A, last DOT inspection 2026-01-14'),
  ('TRL-EAST-1-8215','48ft flatbed, tarps onboard, tandem slider serviced 2026-03-02'),
  ('TRL-EAST-1-6390','53ft reefer, Carrier X4 7500, setpoint 34F, fuel 78%'),
  ('TRL-EAST-1-1728','53ft dry van, swing doors, air leak repaired 2026-02-11'),
  ('TRL-EAST-1-9564','53ft reefer, Thermo King Precedent, setpoint 28F, fuel 45%'),
  ('TRL-EAST-1-4102','53ft dry van, roll door, liftgate equipped'),
  ('TRL-EAST-1-7836','48ft flatbed, coil package, chains and binders onboard'),
  ('TRL-EAST-1-2459','53ft dry van, e-track interior, brake job due 2026-09-01'),
  ('TRL-EAST-1-5981','53ft reefer, setpoint 36F, multi-temp bulkhead installed'),
  ('TRL-EAST-1-3623','53ft dry van, tires replaced 2026-04-22, ABS fault cleared'),
  ('TRL-EAST-1-8074','40ft container chassis, twist locks OK, DOT sticker current'),
  ('TRL-EAST-1-1395','53ft dry van, logistics posts, floor rated 20k lbs'),
  ('TRL-EAST-1-6748','53ft reefer, Carrier Vector 8600, setpoint 32F, fuel 91%'),
  ('TRL-EAST-1-9027','48ft flatbed, conestoga rolling tarp, deck boards replaced'),
  ('TRL-EAST-1-4581','53ft dry van, swing doors, GPS tracker unit 4581-A'),
  ('TRL-EAST-1-2136','53ft dry van, out of service pending kingpin inspection'),
  ('TRL-EAST-1-7492','53ft reefer, setpoint 38F, defrost cycle intermittent'),
  ('TRL-EAST-1-5308','53ft dry van, spare tire mounted, mudflaps replaced'),
  ('TRL-EAST-1-8659','53ft dry van, air ride suspension, annual due 2026-11-30'),
  ('TRL-EAST-1-3874','48ft flatbed, lumber tarps, edge protectors onboard'),
  ('TRL-EAST-1-1063','53ft reefer, Thermo King C-600, setpoint 30F, fuel 62%'),
  ('TRL-EAST-1-9418','53ft dry van, roll door, rear bumper repaired 2026-05-08'),
  ('TRL-EAST-1-6725','53ft dry van, load bars x6, interior lights operational'),
  ('TRL-EAST-1-2807','40ft container chassis, sliding tandem, tires at 60%'),
  ('TRL-EAST-1-4936','53ft reefer, setpoint 34F, door seal replaced 2026-06-19'),
  ('TRL-EAST-1-7150','53ft dry van, swing doors, dock bumpers worn'),
  ('TRL-EAST-1-5472','48ft flatbed, steel hauling config, 12 straps onboard'),
  ('TRL-EAST-1-8903','53ft dry van, in yard, awaiting outbound assignment'),
  ('TRL-EAST-1-3261','53ft reefer, Carrier X4 7300, setpoint 26F, frozen goods'),
  ('TRL-EAST-1-6584','53ft dry van, e-track, wall damage noted panel 7'),
  ('TRL-EAST-1-1849','53ft dry van, liftgate 3000 lb, hydraulic serviced'),
  ('TRL-EAST-1-9736','48ft flatbed, tarps onboard, headache rack installed'),
  ('TRL-EAST-1-2093','53ft reefer, setpoint 40F, produce config, fuel 55%'),
  ('TRL-EAST-1-5617','53ft dry van, roll door, annual inspection 2026-07-03'),
  ('TRL-EAST-2-4728','53ft dry van, swing doors, tandem slider seized'),
  ('TRL-EAST-2-9051','53ft reefer, Thermo King Precedent, setpoint 33F, fuel 82%'),
  ('TRL-EAST-2-3396','48ft flatbed, coil racks installed, chains onboard'),
  ('TRL-EAST-2-6842','53ft dry van, air ride, brake chambers replaced 2026-03-27'),
  ('TRL-EAST-2-1574','53ft dry van, e-track interior, GPS tracker unit 1574-B'),
  ('TRL-EAST-2-8209','53ft reefer, setpoint 29F, multi-temp, bulkhead damaged'),
  ('TRL-EAST-2-5063','40ft container chassis, twist locks OK, tires at 45%'),
  ('TRL-EAST-2-2735','53ft dry van, roll door, floor rated 22k lbs'),
  ('TRL-EAST-2-7481','53ft reefer, Carrier Vector 8500, setpoint 35F, fuel 70%'),
  ('TRL-EAST-2-9628','48ft flatbed, conestoga, rolling tarp track sticking'),
  ('TRL-EAST-2-3157','53ft dry van, swing doors, in yard, loaded outbound'),
  ('TRL-EAST-2-6014','53ft dry van, liftgate equipped, hydraulic leak reported'),
  ('TRL-EAST-2-4892','53ft reefer, setpoint 31F, defrost operational, fuel 88%'),
  ('TRL-EAST-2-1360','53ft dry van, logistics posts, spare tire missing'),
  ('TRL-EAST-2-8546','48ft flatbed, lumber config, edge protectors x20'),
  ('TRL-EAST-2-5729','53ft dry van, roll door, ABS module replaced 2026-02-05'),
  ('TRL-EAST-2-2483','53ft reefer, Thermo King C-600, setpoint 37F, produce'),
  ('TRL-EAST-2-7095','53ft dry van, out of service, kingpin wear exceeds spec'),
  ('TRL-EAST-2-9312','40ft container chassis, sliding tandem, DOT current'),
  ('TRL-EAST-2-4607','53ft dry van, e-track, load bars x8, interior clean'),
  ('TRL-EAST-2-1938','53ft reefer, setpoint 34F, door seal intact, fuel 39%'),
  ('TRL-EAST-2-6251','48ft flatbed, steel config, tarps and binders onboard'),
  ('TRL-EAST-2-8764','53ft dry van, swing doors, rear frame rail repaired'),
  ('TRL-EAST-2-3520','53ft dry van, air ride, annual due 2026-10-15'),
  ('TRL-EAST-2-5186','53ft reefer, Carrier X4 7500, setpoint 27F, frozen'),
  ('TRL-EAST-2-2947','53ft dry van, roll door, mudflaps and lights OK'),
  ('TRL-EAST-2-7803','53ft dry van, in transit, ETA yard 2026-08-12'),
  ('TRL-EAST-2-9475','48ft flatbed, headache rack, deck boards worn'),
  ('TRL-EAST-2-1092','53ft reefer, setpoint 32F, multi-temp bulkhead installed'),
  ('TRL-EAST-2-4318','53ft dry van, liftgate 2500 lb, tires replaced 2026-05-30'),
  ('TRL-EAST-2-6679','40ft container chassis, twist locks worn, inspection due'),
  ('TRL-EAST-2-8231','53ft dry van, e-track, wall panel 3 punctured'),
  ('TRL-EAST-2-3865','53ft reefer, Thermo King, setpoint 36F, fuel 74%'),
  ('TRL-WEST-2-5240','53ft dry van, swing doors, DOT inspection 2026-01-28'),
  ('TRL-WEST-2-9683','53ft reefer, Carrier X4 7300, setpoint 30F, fuel 66%'),
  ('TRL-WEST-2-1417','48ft flatbed, tarps onboard, chains x10, binders x6'),
  ('TRL-WEST-2-6052','53ft dry van, roll door, air ride suspension serviced'),
  ('TRL-WEST-2-3798','53ft reefer, setpoint 25F, frozen config, fuel 93%'),
  ('TRL-WEST-2-8365','53ft dry van, e-track interior, GPS tracker unit 8365-C'),
  ('TRL-WEST-2-2609','40ft container chassis, sliding tandem, tires at 70%'),
  ('TRL-WEST-2-7124','53ft dry van, liftgate 3000 lb, hydraulic serviced'),
  ('TRL-WEST-2-4571','53ft reefer, Thermo King Precedent, setpoint 38F, produce'),
  ('TRL-WEST-2-9836','48ft flatbed, conestoga rolling tarp, track lubricated'),
  ('TRL-WEST-2-1250','53ft dry van, swing doors, floor rated 20k lbs'),
  ('TRL-WEST-2-6493','53ft dry van, out of service, brake job scheduled'),
  ('TRL-WEST-2-3017','53ft reefer, setpoint 33F, defrost cycle normal, fuel 51%'),
  ('TRL-WEST-2-8742','53ft dry van, roll door, in yard, empty'),
  ('TRL-WEST-2-5169','48ft flatbed, coil package, steel hauling config'),
  ('TRL-WEST-2-2384','53ft dry van, logistics posts, load bars x6'),
  ('TRL-WEST-2-7906','53ft reefer, Carrier Vector 8600, setpoint 28F, fuel 84%'),
  ('TRL-WEST-2-4638','53ft dry van, e-track, annual inspection 2026-12-09'),
  ('TRL-WEST-2-9051','53ft dry van, swing doors, tandem slider serviced'),
  ('TRL-WEST-2-1573','40ft container chassis, twist locks OK, DOT current'),
  ('TRL-WEST-2-6820','53ft reefer, setpoint 35F, door seal replaced 2026-04-17'),
  ('TRL-WEST-2-3495','48ft flatbed, lumber tarps, edge protectors onboard'),
  ('TRL-WEST-2-8107','53ft dry van, roll door, rear bumper damaged'),
  ('TRL-WEST-2-5762','53ft dry van, air ride, tires at 55%, ABS fault active'),
  ('TRL-WEST-2-2938','53ft reefer, Thermo King C-600, setpoint 31F, fuel 47%'),
  ('TRL-WEST-2-7451','53ft dry van, in transit, ETA yard 2026-08-13'),
  ('TRL-WEST-2-9284','48ft flatbed, headache rack, deck boards replaced'),
  ('TRL-WEST-2-4016','53ft reefer, setpoint 39F, produce config, fuel 60%'),
  ('TRL-WEST-2-1839','53ft dry van, liftgate equipped, interior lights out'),
  ('TRL-WEST-2-6527','53ft dry van, swing doors, kingpin inspected 2026-06-02'),
  ('TRL-WEST-2-3160','40ft container chassis, sliding tandem, tires at 35%'),
  ('TRL-WEST-2-8473','53ft reefer, Carrier X4 7500, setpoint 26F, frozen goods'),
  ('TRL-WEST-2-5698','53ft dry van, e-track, spare tire mounted, clean');
```

Confirm that all 100 rows are the same range

```bash
$ python3 show-ranges.py --url <url> --table trailer_global

┌───┬──────────┬──────┬─────────────┬─────────────────────────────────────────────┐
│   │ range_id │ rows │ leaseholder │ replicas                                    │
╞───╪──────────╪──────╪─────────────╪─────────────────────────────────────────────╡
│ 1 │ 3806     │ 100  │ tx1 (3)     │ tx1 (1), tx1 (3), tx1 (6), tx2 (5), tx3 (8) │
├───┼──────────┼──────┼─────────────┼─────────────────────────────────────────────┤
│   │ TOTAL    │ 100  │             │                                             │
└───┴──────────┴──────┴─────────────┴─────────────────────────────────────────────┘
```

and then confirm that each region has at least one replica of the range

```sql
> SHOW ZONE CONFIGURATION FROM TABLE trailer_global;                     
         target        |                            raw_config_sql
-----------------------+------------------------------------------------------------------------
  TABLE trailer_global | ALTER TABLE trailer_global CONFIGURE ZONE USING
                       |     range_min_bytes = 134217728,
                       |     range_max_bytes = 536870912,
                       |     gc.ttlseconds = 31536000,
                       |     global_reads = true,
                       |     num_replicas = 5,
                       |     num_voters = 3,
                       |     constraints = '{+region=tx1: 1, +region=tx2: 1, +region=tx3: 1}',
                       |     voter_constraints = '[+region=tx1]',
                       |     lease_preferences = '[[+region=tx1]]'
```


```sql
SELECT id, trailer_number, info FROM trailer_global WHERE trailer_number = 'TRL-EAST-1-6390';
SELECT id, trailer_number, info FROM trailer_global WHERE trailer_number = 'TRL-WEST-2-4571';
SELECT id, trailer_number, info FROM trailer_global WHERE trailer_number LIKE 'TRL-WEST-2%';
SELECT id, trailer_number, info FROM trailer_global WHERE trailer_number LIKE 'TRL-EAST-1%';
SELECT id, trailer_number, info FROM trailer_global WHERE trailer_number IN ('TRL-EAST-1-3047','TRL-EAST-2-9051','TRL-WEST-2-5240');
```


```sql
> EXPLAIN ANALYZE SELECT id, trailer_number, info FROM trailer_global WHERE       
                                                                 -> trailer_number = 'TRL-EAST-1-6390';                                             
                        info
----------------------------------------------------
  planning time: 353µs
  execution time: 2ms
  distribution: full
  plan type: custom
  rows decoded from KV: 100 (12 KiB, 1 gRPC calls)
  DistSQL network usage: 400 B (3 messages)
  regions: tx1, tx3

  • filter
  │ sql nodes: n3
  │ regions: tx1
  │ execution time: 21µs
  │ sql cpu time: 21µs
  │ actual row count: 1
  │ filter: trailer_number = 'TRL-EAST-1-6390'
  │
  └── • scan
        sql nodes: n3
        kv nodes: n3
        regions: tx1
        KV time: 621µs
        KV rows decoded: 100
        sql cpu time: 176µs
        actual row count: 100
        missing stats
        table: trailer_global@trailer_global_pkey
        spans: FULL SCAN



                                         info
--------------------------------------------------------------------------------------
  planning time: 4ms
  execution time: 3ms
  distribution: local
  plan type: custom
  rows decoded from KV: 100 (12 KiB, 1 gRPC calls)
  regions: tx1
  used follower read

  • filter
  │ sql nodes: n6
  │ regions: tx1
  │ execution time: 10µs
  │ sql cpu time: 10µs
  │ actual row count: 1
  │ estimated row count: 1
  │ filter: trailer_number = 'TRL-EAST-1-6390'
  │
  └── • scan
        sql nodes: n6
        kv nodes: n6
        regions: tx1
        used follower read
        KV time: 3ms
        KV rows decoded: 100
        sql cpu time: 124µs
        actual row count: 100
        estimated row count: 100 (100% of the table; stats collected 15 seconds ago)
        table: trailer_global@trailer_global_pkey
        spans: FULL SCAN



                                         info
--------------------------------------------------------------------------------------
  planning time: 4ms
  execution time: 2ms
  distribution: local
  plan type: custom
  rows decoded from KV: 100 (12 KiB, 1 gRPC calls)
  regions: tx2
  used follower read

  • filter
  │ sql nodes: n9
  │ regions: tx2
  │ execution time: 11µs
  │ sql cpu time: 10µs
  │ actual row count: 1
  │ estimated row count: 1
  │ filter: trailer_number = 'TRL-EAST-1-6390'
  │
  └── • scan
        sql nodes: n9
        kv nodes: n5
        regions: tx2
        used follower read
        KV time: 2ms
        KV rows decoded: 100
        sql cpu time: 117µs
        actual row count: 100
        estimated row count: 100 (100% of the table; stats collected 28 seconds ago)
        table: trailer_global@trailer_global_pkey
        spans: FULL SCAN
```




```sql
UPDATE trailer_global SET info = '53ft reefer, Carrier X4 7500, setpoint 34F, fuel 92%, PM completed 2026-08-11'
WHERE trailer_number = 'TRL-EAST-1-6390';

UPDATE trailer_global SET info = '53ft dry van, roll door, returned to service, brake job completed 2026-08-11'
WHERE trailer_number = 'TRL-EAST-2-7095';

UPDATE trailer_global SET info = '53ft reefer, Thermo King Precedent, setpoint 27F, frozen config, fuel 88%'
WHERE trailer_number = 'TRL-WEST-2-4571';

UPDATE trailer_global SET info = '48ft flatbed, conestoga, tarp track repaired, deck boards replaced 2026-08-11'
WHERE trailer_number = 'TRL-EAST-2-9628';

UPDATE trailer_global SET info = '53ft dry van, air ride, ABS fault cleared, tires replaced 2026-08-11'
WHERE trailer_number = 'TRL-WEST-2-5762';
```


## Regional by Row (RBR) Tables

Choose this option for a table if

1. it needs to be optimized for fast `INSERT`s, `UPDATE`s and `DELETE`s in multiple regions
2. `SELECT`s are typically predicated on specific values, e.g. `id='12345'`


Create a table:

```sql
CREATE TABLE trailer_rbr (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    region              crdb_internal_region NOT NULL AS (
                            CASE
                                WHEN trailer_number LIKE 'TRL-EAST-1%' THEN 'tx1'
                                WHEN trailer_number LIKE 'TRL-EAST-2%' THEN 'tx2'
                                WHEN trailer_number LIKE 'TRL-WEST-2%' THEN 'tx3'
                            END
                        ) STORED,
    trailer_number      STRING NOT NULL,
    param1              INTEGER DEFAULT 0,
    param2              FLOAT DEFAULT 0.0
) LOCALITY REGIONAL BY ROW AS region;
```

and populate it:

```sql
INSERT INTO trailer_rbr (trailer_number, param1, param2) VALUES
 ('TRL-EAST-1-3047',12,4.75),('TRL-EAST-1-8215',48,19.20),
 ('TRL-EAST-1-6390',7,33.10),('TRL-EAST-1-1728',91,2.45),
 ('TRL-EAST-1-9564',23,58.60),('TRL-EAST-1-4102',65,11.05),
 ('TRL-EAST-1-7836',3,47.90),('TRL-EAST-1-2459',80,6.35),
 ('TRL-EAST-1-5981',37,25.80),('TRL-EAST-1-3623',54,72.15),
 ('TRL-EAST-1-8074',19,8.50),('TRL-EAST-1-1395',72,39.95),
 ('TRL-EAST-1-6748',41,14.70),('TRL-EAST-1-9027',88,61.30),
 ('TRL-EAST-1-4581',15,27.45),('TRL-EAST-1-2136',60,3.80),
 ('TRL-EAST-1-7492',29,52.25),('TRL-EAST-1-5308',96,17.65),
 ('TRL-EAST-1-8659',44,44.40),('TRL-EAST-1-3874',8,9.15),
 ('TRL-EAST-1-1063',77,66.85),('TRL-EAST-1-9418',33,21.00),
 ('TRL-EAST-1-6725',51,35.55),('TRL-EAST-1-2807',26,5.90),
 ('TRL-EAST-1-4936',69,49.75),('TRL-EAST-1-7150',11,13.30),
 ('TRL-EAST-1-5472',84,70.20),('TRL-EAST-1-8903',39,1.65),
 ('TRL-EAST-1-3261',57,29.85),('TRL-EAST-1-6584',22,56.40),
 ('TRL-EAST-1-1849',94,10.75),('TRL-EAST-1-9736',46,42.10),
 ('TRL-EAST-1-2093',17,23.55),('TRL-EAST-1-5617',63,63.95),
 ('TRL-EAST-2-4728',31,7.20),('TRL-EAST-2-9051',86,38.65),
 ('TRL-EAST-2-3396',5,16.40),('TRL-EAST-2-6842',59,54.05),
 ('TRL-EAST-2-1574',74,2.90),('TRL-EAST-2-8209',20,31.50),
 ('TRL-EAST-2-5063',67,68.75),('TRL-EAST-2-2735',42,12.15),
 ('TRL-EAST-2-7481',9,45.60),('TRL-EAST-2-9628',82,24.30),
 ('TRL-EAST-2-3157',35,59.85),('TRL-EAST-2-6014',53,4.05),
 ('TRL-EAST-2-4892',28,36.70),('TRL-EAST-2-1360',71,73.25),
 ('TRL-EAST-2-8546',14,18.90),('TRL-EAST-2-5729',90,50.35),
 ('TRL-EAST-2-2483',47,26.60),('TRL-EAST-2-7095',2,64.15),
 ('TRL-EAST-2-9312',62,9.80),('TRL-EAST-2-4607',25,41.45),
 ('TRL-EAST-2-1938',79,15.00),('TRL-EAST-2-6251',38,57.55),
 ('TRL-EAST-2-8764',6,32.20),('TRL-EAST-2-3520',93,71.85),
 ('TRL-EAST-2-5186',50,6.50),('TRL-EAST-2-2947',16,48.95),
 ('TRL-EAST-2-7803',75,22.40),('TRL-EAST-2-9475',43,60.05),
 ('TRL-EAST-2-1092',30,13.70),('TRL-EAST-2-4318',87,37.35),
 ('TRL-EAST-2-6679',10,53.90),('TRL-EAST-2-8231',56,28.15),
 ('TRL-EAST-2-3865',21,67.60),
 ('TRL-WEST-2-5240',68,3.25),('TRL-WEST-2-9683',34,40.80),
 ('TRL-WEST-2-1417',97,20.35),('TRL-WEST-2-6052',13,55.70),
 ('TRL-WEST-2-3798',61,8.95),('TRL-WEST-2-8365',27,46.50),
 ('TRL-WEST-2-2609',85,74.05),('TRL-WEST-2-7124',49,11.60),
 ('TRL-WEST-2-4571',4,34.25),('TRL-WEST-2-9836',76,62.70),
 ('TRL-WEST-2-1250',40,17.15),('TRL-WEST-2-6493',18,51.80),
 ('TRL-WEST-2-3017',89,5.45),('TRL-WEST-2-8742',55,43.00),
 ('TRL-WEST-2-5169',24,69.65),('TRL-WEST-2-2384',70,30.10),
 ('TRL-WEST-2-7906',36,7.75),('TRL-WEST-2-4638',92,58.40),
 ('TRL-WEST-2-9051',45,14.95),('TRL-WEST-2-1573',1,65.50),
 ('TRL-WEST-2-6820',64,25.05),('TRL-WEST-2-3495',32,47.60),
 ('TRL-WEST-2-8107',78,10.20),('TRL-WEST-2-5762',52,72.75),
 ('TRL-WEST-2-2938',7,39.30),('TRL-WEST-2-7451',83,19.85),
 ('TRL-WEST-2-9284',47,56.40),('TRL-WEST-2-4016',12,2.05),
 ('TRL-WEST-2-1839',66,44.60),('TRL-WEST-2-6527',29,29.25),
 ('TRL-WEST-2-3160',81,63.80),('TRL-WEST-2-8473',58,16.35),
 ('TRL-WEST-2-5698',95,52.90);
```

```sql
UPDATE trailer_rbr SET param1 = 17 WHERE id = '92302113-6962-4552-aa92-a56571c68b6c';
UPDATE trailer_rbr SET param2 = 58.20 WHERE id = '92302113-6962-4552-aa92-a56571c68b6c';
UPDATE trailer_rbr SET param1 = 63, param2 = 12.85 WHERE id = '92302113-6962-4552-aa92-a56571c68b6c';
UPDATE trailer_rbr SET param1 = 8 WHERE id = '92302113-6962-4552-aa92-a56571c68b6c';
UPDATE trailer_rbr SET param2 = 91.40 WHERE id = '92302113-6962-4552-aa92-a56571c68b6c';
UPDATE trailer_rbr SET param1 = 45, param2 = 27.05 WHERE id = '92302113-6962-4552-aa92-a56571c68b6c';
UPDATE trailer_rbr SET param2 = 3.75 WHERE id = '92302113-6962-4552-aa92-a56571c68b6c';
UPDATE trailer_rbr SET param1 = 79 WHERE id = '92302113-6962-4552-aa92-a56571c68b6c';
UPDATE trailer_rbr SET param1 = 22, param2 = 66.30 WHERE id = '92302113-6962-4552-aa92-a56571c68b6c';
UPDATE trailer_rbr SET param2 = 40.95 WHERE id = '92302113-6962-4552-aa92-a56571c68b6c';
```


```sql
EXPLAIN ANALYZE SELECT * FROM trailer_rbr WHERE region='tx1';
```
