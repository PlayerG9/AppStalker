--
-- File generated with SQLiteStudio v3.3.3 on Fr Okt 1 19:57:44 2021
--
-- Text encoding used: UTF-8
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: executables
CREATE IF NOT EXISTS TABLE executables (
    name        STRING NOT NULL,
    exe         STRING NOT NULL,
    cmdline     STRING NOT NULL,
    create_time REAL   NOT NULL
                       UNIQUE,
    username    STRING NOT NULL
);


-- Table: measurements
CREATE IF NOT EXISTS TABLE measurements (
    exe_id INTEGER NOT NULL,
    ts     REAL    NOT NULL
                   DEFAULT (CURRENT_TIMESTAMP) 
);


COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
