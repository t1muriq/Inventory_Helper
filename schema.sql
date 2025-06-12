CREATE TABLE IF NOT EXISTS buildings (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS rooms (
    id SERIAL PRIMARY KEY,
    building_id INTEGER REFERENCES buildings(id) ON DELETE CASCADE,
    room_number TEXT NOT NULL,
    UNIQUE(building_id, room_number)
);

CREATE TABLE IF NOT EXISTS computers (
    id SERIAL PRIMARY KEY,
    room_id INTEGER REFERENCES rooms(id) ON DELETE CASCADE,
    assigned_it_number TEXT UNIQUE,
    department TEXT,
    responsible TEXT,
    phone TEXT,
    inventory_number TEXT,
    serial_number TEXT,
    ip_address TEXT,
    mac_address TEXT,
    kaspersky_attempted TEXT,
    kaspersky_network TEXT,
    comment TEXT
);

CREATE TABLE IF NOT EXISTS memory_modules (
    id SERIAL PRIMARY KEY,
    computer_id INTEGER REFERENCES computers(id) ON DELETE CASCADE,
    name TEXT,
    description TEXT
);

CREATE TABLE IF NOT EXISTS processors (
    id SERIAL PRIMARY KEY,
    computer_id INTEGER REFERENCES computers(id) ON DELETE CASCADE,
    type TEXT,
    frequency TEXT
);

CREATE TABLE IF NOT EXISTS motherboards (
    id SERIAL PRIMARY KEY,
    computer_id INTEGER REFERENCES computers(id) ON DELETE CASCADE,
    model TEXT
);

CREATE TABLE IF NOT EXISTS disks (
    id SERIAL PRIMARY KEY,
    computer_id INTEGER REFERENCES computers(id) ON DELETE CASCADE,
    name TEXT,
    capacity TEXT
);

CREATE TABLE IF NOT EXISTS video_adapters (
    id SERIAL PRIMARY KEY,
    computer_id INTEGER REFERENCES computers(id) ON DELETE CASCADE,
    name TEXT,
    memory TEXT
);

CREATE TABLE IF NOT EXISTS monitors (
    id SERIAL PRIMARY KEY,
    computer_id INTEGER REFERENCES computers(id) ON DELETE CASCADE,
    assigned_it_number TEXT,
    model TEXT,
    serial_number TEXT,
    resolution TEXT
);

CREATE TABLE IF NOT EXISTS upss (
    id SERIAL PRIMARY KEY,
    computer_id INTEGER REFERENCES computers(id) ON DELETE CASCADE,
    assigned_it_number TEXT
);