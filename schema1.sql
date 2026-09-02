CREATE TABLE warehouse (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    region              STRING NOT NULL,
    location            STRING
) LOCALITY GLOBAL;


INSERT INTO warehouse (region, location) VALUES
    ('west', 'Bakersfield, CA 93313'),
    ('west', 'Fresno, CA 93725'),
    ('west', 'McClellan Park, CA 95652'),
    ('west', 'Tracy, CA 95376'),
    ('west', 'Tulare, CA 93274'),
    ('west', 'Turlock, CA 95380'),
    ('west', 'Union City, CA 94587'),
    ('west', 'Syracuse, UT 84075'),
    ('west', 'La Vista, NE 68138'),
    ('west', 'Omaha, NE 68107'),
    ('west', 'Arlington, TX 76010'),
    ('west', 'Dallas, TX 75247'),
    ('west', 'Dallas, TX 75212'),
    ('west', 'Denton, TX 76207'),
    ('west', 'Fort Worth, TX 76106'),
    ('west', 'Laredo, TX 78045'),
    ('west', 'Laredo, TX 78041'),
    ('east', 'Milford, DE 19963'),
    ('east', 'Lake City, FL 32055'),
    ('east', 'Medley, FL 33178'),
    ('east', 'Orlando, FL 32808'),
    ('east', 'McDonough, GA 30253'),
    ('east', 'Minooka, IL 60447'),
    ('east', 'Wilmington, IL 60481'),
    ('east', 'Hebron, IN 46341'),
    ('east', 'Lebanon, IN 46052'),
    ('east', 'Camden, NJ 08103'),
    ('east', 'Voorhees, NJ 08043'),
    ('east', 'Lumberton, NC 28358'),
    ('east', 'Marshville, NC 28103'),
    ('east', 'Warsaw, NC 28398'),
    ('east', 'Bethlehem, PA 18015'),
    ('east', 'Bethlehem, PA 18020'),
    ('east', 'Hazleton, PA 18202'),
    ('east', 'Quakertown, PA 18951'),
    ('east', 'Covington, TN 38019'),
    ('east', 'La Vergne, TN 37086'),
    ('east', 'Nashville, TN 37210'),
    ('east', 'Smyrna, TN 37167'),
    ('east', 'Harrisonburg, VA 22801');


CREATE TABLE gate_arrival (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    warehouse_id        UUID,
    trailer_id          UUID,
    crdb_region         crdb_internal_region NOT VISIBLE NOT NULL DEFAULT default_to_database_primary_region(gateway_region())::crdb_internal_region,
    CONSTRAINT gate_arrival_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES warehouse(id),
    CONSTRAINT gate_arrival_trailer_id_fkey FOREIGN KEY (trailer_id) REFERENCES trailer_global(id)
) LOCALITY REGIONAL BY ROW;

CREATE INDEX ON gate_arrival (warehouse_id);


INSERT INTO gate_arrival (warehouse_id, trailer_id, crdb_region)
SELECT w.id, t.id, CASE w.region WHEN 'east' THEN 'tx1' WHEN 'west' THEN 'tx3' END::crdb_internal_region
FROM warehouse w
CROSS JOIN (SELECT id FROM trailer_global LIMIT 25 OFFSET 0) t;

INSERT INTO gate_arrival (warehouse_id, trailer_id, crdb_region)
SELECT w.id, t.id, CASE w.region WHEN 'east' THEN 'tx1' WHEN 'west' THEN 'tx3' END::crdb_internal_region
FROM warehouse w
CROSS JOIN (SELECT id FROM trailer_global LIMIT 25 OFFSET 25) t;

INSERT INTO gate_arrival (warehouse_id, trailer_id, crdb_region)
SELECT w.id, t.id, CASE w.region WHEN 'east' THEN 'tx1' WHEN 'west' THEN 'tx3' END::crdb_internal_region
FROM warehouse w
CROSS JOIN (SELECT id FROM trailer_global LIMIT 25 OFFSET 50) t;

INSERT INTO gate_arrival (warehouse_id, trailer_id, crdb_region)
SELECT w.id, t.id, CASE w.region WHEN 'east' THEN 'tx1' WHEN 'west' THEN 'tx3' END::crdb_internal_region
FROM warehouse w
CROSS JOIN (SELECT id FROM trailer_global LIMIT 25 OFFSET 75) t;

INSERT INTO gate_arrival (warehouse_id, trailer_id, crdb_region)
SELECT w.id, t.id, CASE w.region WHEN 'east' THEN 'tx1' WHEN 'west' THEN 'tx3' END::crdb_internal_region
FROM warehouse w
CROSS JOIN (SELECT id FROM trailer_global LIMIT 25 OFFSET 100) t;

INSERT INTO gate_arrival (warehouse_id, trailer_id, crdb_region)
SELECT w.id, t.id, CASE w.region WHEN 'east' THEN 'tx1' WHEN 'west' THEN 'tx3' END::crdb_internal_region
FROM warehouse w
CROSS JOIN (SELECT id FROM trailer_global LIMIT 25 OFFSET 125) t;

INSERT INTO gate_arrival (warehouse_id, trailer_id, crdb_region)
SELECT w.id, t.id, CASE w.region WHEN 'east' THEN 'tx1' WHEN 'west' THEN 'tx3' END::crdb_internal_region
FROM warehouse w
CROSS JOIN (SELECT id FROM trailer_global LIMIT 25 OFFSET 150) t;

INSERT INTO gate_arrival (warehouse_id, trailer_id, crdb_region)
SELECT w.id, t.id, CASE w.region WHEN 'east' THEN 'tx1' WHEN 'west' THEN 'tx3' END::crdb_internal_region
FROM warehouse w
CROSS JOIN (SELECT id FROM trailer_global LIMIT 25 OFFSET 175) t;

INSERT INTO gate_arrival (warehouse_id, trailer_id, crdb_region)
SELECT w.id, t.id, CASE w.region WHEN 'east' THEN 'tx1' WHEN 'west' THEN 'tx3' END::crdb_internal_region
FROM warehouse w
CROSS JOIN (SELECT id FROM trailer_global LIMIT 25 OFFSET 200) t;

INSERT INTO gate_arrival (warehouse_id, trailer_id, crdb_region)
SELECT w.id, t.id, CASE w.region WHEN 'east' THEN 'tx1' WHEN 'west' THEN 'tx3' END::crdb_internal_region
FROM warehouse w
CROSS JOIN (SELECT id FROM trailer_global LIMIT 25 OFFSET 225) t;
