-- create init table with one row
CREATE TABLE init_lock(lock boolean DEFAULT TRUE);
INSERT INTO init_lock(lock)
VALUES 
(TRUE);

DO
$$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'monsterverse') THEN
        CREATE DATABASE monsterverse;
    END IF;
END
$$;
DO
$$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'godzilla') THEN
        CREATE ROLE godzilla WITH LOGIN PASSWORD 'Mrawww';
    END IF;
END
$$;
GRANT ALL PRIVILEGES ON DATABASE monsterverse TO godzilla;