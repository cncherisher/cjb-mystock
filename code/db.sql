DROP TABLE IF EXISTS stockLimits;

CREATE TABLE stockLimits (
    limitType TEXT PRIMARY KEY,
    limitContent TEXT NOT NULL,
    renewTime INTEGER NOT NULL
);
