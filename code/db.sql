DROP TABLE IF EXISTS stockLimits;

CREATE TABLE stockLimits (
    limitKey TEXT PRIMARY KEY,
    content TEXT NOT NULL
);
