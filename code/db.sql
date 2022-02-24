DROP TABLE IF EXISTS stockLimits;

CREATE TABLE stockLimits (
    limitType TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    renewTime INTEGER NOT NULL
);
