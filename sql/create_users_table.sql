-- Create the `users` table with foreign key references
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('Patient', 'Doctor', 'Billing Staff', 'Insurance', 'Admin') NOT NULL,
    doctor_id INT DEFAULT NULL,
    patient_id INT DEFAULT NULL,
    insurance_provider_id INT DEFAULT NULL,
    FOREIGN KEY (doctor_id) REFERENCES doctor(doctor_id) ON DELETE CASCADE,
    FOREIGN KEY (patient_id) REFERENCES patient(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (insurance_provider_id) REFERENCES insurance_provider(insurance_id) ON DELETE CASCADE
);

-- Insert sample data into the `users` table
INSERT INTO users (username, password, role, doctor_id) VALUES
('doctor1', '$2b$12$i9Chg7XN5B3K/JBaBKQIFubO9hFuMEMGDT/omj4.VWkRpIWDxu5bu', 'Doctor', 3); -- password: 1234

INSERT INTO users (username, password, role, patient_id) VALUES
('patient1', '$2b$12$i9Chg7XN5B3K/JBaBKQIFubO9hFuMEMGDT/omj4.VWkRpIWDxu5bu', 'Patient', 12); -- password: 1234

INSERT INTO users (username, password, role) VALUES
('billing1', '$2b$12$i9Chg7XN5B3K/JBaBKQIFubO9hFuMEMGDT/omj4.VWkRpIWDxu5bu', 'Billing Staff'); -- password: 1234

INSERT INTO users (username, password, role, insurance_provider_id) VALUES
('insurance1', '$2b$12$i9Chg7XN5B3K/JBaBKQIFubO9hFuMEMGDT/omj4.VWkRpIWDxu5bu', 'Insurance', 1); -- password: 1234
