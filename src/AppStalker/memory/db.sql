--
-- File generated with SQLiteStudio v3.3.3 on Sa Okt 16 13:45:04 2021
--
-- Text encoding used: UTF-8
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: executables
CREATE TABLE IF NOT EXISTS executables (
    name        STRING NOT NULL,
    exe         STRING NOT NULL,
    cmdline     STRING NOT NULL,
    create_time REAL   NOT NULL
                       UNIQUE
                       PRIMARY KEY,
    username    STRING NOT NULL
);


-- Table: measurements
CREATE TABLE IF NOT EXISTS measurements (
    exe_id INTEGER NOT NULL,
    ts     REAL    NOT NULL
                   DEFAULT (strftime('%s', 'now') ) 
);


COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
