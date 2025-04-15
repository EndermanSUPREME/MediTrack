-- Create the `users` table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('Patient', 'Doctor', 'Billing Staff', 'Insurance') NOT NULL
);

-- Insert sample data into the `users` table
INSERT INTO users (username, password, role) VALUES
('patient1', '$2b$12$i9Chg7XN5B3K/JBaBKQIFubO9hFuMEMGDT/omj4.VWkRpIWDxu5bu', 'Patient'), -- password: 1234
('doctor1', '$2b$12$i9Chg7XN5B3K/JBaBKQIFubO9hFuMEMGDT/omj4.VWkRpIWDxu5bu', 'Doctor'),   -- password: 1234
('billing1', '$2b$12$i9Chg7XN5B3K/JBaBKQIFubO9hFuMEMGDT/omj4.VWkRpIWDxu5bu', 'Billing Staff'), -- password: 1234
('insurance1', '$2b$12$i9Chg7XN5B3K/JBaBKQIFubO9hFuMEMGDT/omj4.VWkRpIWDxu5bu', 'Insurance'); -- password: 1234
