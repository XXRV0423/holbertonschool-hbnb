-- HBnB initial data
-- Run after schema.sql. Target: MySQL 8.x

USE hbnb_dev_db;

-- Administrator user.
-- Password is 'admin1234' hashed with bcrypt (cost factor 12, same
-- algorithm/format Flask-Bcrypt uses at runtime):
--   >>> import bcrypt
--   >>> bcrypt.hashpw(b'admin1234', bcrypt.gensalt(rounds=12))
INSERT INTO User (id, first_name, last_name, email, password, is_admin)
VALUES (
    '36c9050e-ddd3-4c3b-9731-9f487208bbc1',
    'Admin',
    'HBnB',
    'admin@hbnb.io',
    '$2b$12$cbVQpgH8e6vJ3ViXp0y53eecee9vqIHy4RM.AgFLc0wrO228qffCG',
    TRUE
);

-- Initial amenities (UUID4 generated with Python's uuid.uuid4()).
INSERT INTO Amenity (id, name) VALUES
    ('ed5311d5-e5c8-40be-94d9-6932366b584d', 'WiFi'),
    ('7553a5c6-fb3a-48c7-9985-ef2ea2254959', 'Swimming Pool'),
    ('03658698-5636-40be-bc52-c5bf7986b8b0', 'Air Conditioning');
