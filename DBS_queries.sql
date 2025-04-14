-- ---making an appointment---

-- INSERT: (Example below)
-- INSERT INTO appointment (...) VALUES (112, '2025-04-22', '13:00:00', 'scheduled', 'Routine check-up', 12, 3, 2);
INSERT INTO appointment (appointment_id, date, time, status, notes, patient_id, doctor_id, hospital_id)
VALUES (113, '2025-04-22', '13:00:00', 'scheduled', 'Routine check-up', 12, 3, 2);

-- DELETE:
DELETE FROM appointment WHERE appointment_id = 113;

-- UPDATE:
UPDATE appointment
SET status = 'completed', notes = 'Routine check-up completed successfully'
WHERE appointment_id = 112;

-- SELECT:
SELECT * FROM appointment WHERE appointment_id = 112;
SELECT * FROM appointment WHERE date = '2025-04-22' AND doctor_id = 3 ORDER BY time;
SELECT * FROM appointment WHERE status = 'scheduled' AND hospital_id = 2;

-- ---paying bill---

-- UPDATE (basic payment):
UPDATE billing_cost bc
JOIN patient_billing pb ON bc.billing_cost_id = pb.billing_cost_id
SET bc.total_amount = 250, bc.payment_status = 'paid'
WHERE bc.billing_cost_id = 152 AND pb.patient_id = 12;

-- UPDATE (zero out payment):
UPDATE billing_cost bc
JOIN patient_billing pb ON bc.billing_cost_id = pb.billing_cost_id
SET bc.total_amount = 0, bc.payment_status = 'paid'
WHERE bc.billing_cost_id = 112 AND pb.patient_id = 12;

-- UPDATE (insurance pays some):
UPDATE billing_cost bc
JOIN patient_billing pb ON bc.billing_cost_id = pb.billing_cost_id
SET bc.payment_status = 'paid', bc.insurance_claimed = 1, bc.insurance_covered = 300.00
WHERE bc.billing_cost_id = 112 AND pb.patient_id = 12;

-- ---insurance claim---

-- UPDATE (insurance claim submitted):
UPDATE billing_cost bc
JOIN patient_billing pb ON bc.billing_cost_id = pb.billing_cost_id
SET bc.insurance_claimed = 1, bc.insurance_covered = 300.00
WHERE bc.billing_cost_id = 112 AND pb.patient_id = 12;

-- SELECT (view claimed insurance info):
SELECT bc.billing_cost_id, bc.total_amount, bc.insurance_covered, bc.payment_status, pb.patient_id, pb.insurance_provider_id
FROM billing_cost bc
JOIN patient_billing pb ON bc.billing_cost_id = pb.billing_cost_id
WHERE bc.insurance_claimed = 1;

-- ---see schedule of appointments---

-- SELECT (for specific doctor):
SELECT a.date, p.first_name AS patient_first_name, p.last_name AS patient_last_name, a.status
FROM appointment a
JOIN patient p ON a.patient_id = p.patient_id
WHERE a.doctor_id = 3 AND a.date = '2025-04-30'
ORDER BY a.time;

-- UPDATE (cancel appointment):
UPDATE appointment
SET status = 'cancelled', notes = 'Patient rescheduled'
WHERE appointment_id = 112 AND doctor_id = 3 AND date = '2025-04-30';

-- UPDATE (reschedule appointment):
UPDATE appointment
SET date = '2025-05-01', time = '14:00:00', status = 'scheduled', notes = 'Rescheduled appointment'
WHERE appointment_id = 112 AND doctor_id = 3 AND date = '2025-04-30';

-- ---Adding a new patient---

-- Example:
-- INSERT INTO `patient`(...) VALUES (...);
INSERT INTO patient (patient_id, first_name, last_name, phone, email, address)
VALUES (21, 'Alex', 'Johnson', '555-123-4567', 'alex.j@example.com', '123 Main St');

-- ---Adding a new doctor---

-- Example:
-- INSERT INTO doctor (...) VALUES (...);
INSERT INTO doctor (doctor_id, first_name, last_name, speciality, phone, email)
VALUES (10, 'Austin', 'Sternberg', '2', '111-111-1111', 'asternb1@kent.edu');

-- ---Adding a new hospital---

-- Example:
-- INSERT INTO hospital (...) VALUES (...);
INSERT INTO hospital (hospital_id, name, location, operating_hours, care_type)
VALUES (3, 'DeWeese Health', 'Kent, Ohio', '8:00 AM - 8:00 PM', '2');

-- ---Add doctor to hospital via hospital_doctors table---

-- Example:
-- INSERT INTO hospital_doctors (...) VALUES (...);
INSERT INTO hospital_doctors (hospital_id, doctor_id)
VALUES (3, 10);

-- ---add a bill---

-- Example:
-- INSERT INTO billing_cost (...) VALUES (...);
INSERT INTO billing_cost (billing_cost_id, total_amount, payment_status, insurance_claimed, insurance_covered)
VALUES (115, 150.00, 'unpaid', 0, 0);

-- INSERT INTO patient_billing (...) VALUES (...);
INSERT INTO patient_billing (bill_id, billing_cost_id, appointment_id, patient_id, insurance_provider_id)
VALUES (115, 115, 112, 12, 1);

-- ---add new profession---

-- Example:
-- INSERT INTO professions (...) VALUES (...);
INSERT INTO professions (professions_id, type)
VALUES (50, 'therapist');

-- Select ALL Doctors in a specific hospital:
-- Example:
SELECT * FROM doctor WHERE doctor_id IN (SELECT doctor_id FROM hospital_doctors WHERE hospital_id = 1);

-- Select ALL Doctors in a specific profession:
-- Example:
SELECT * FROM doctor 
WHERE speciality = 2;

