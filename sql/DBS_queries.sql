-- ---making an appointment---

-- INSERT: (Example below)
INSERT INTO appointment (appointment_id, date, time, status, notes, patient_id, doctor_id, hospital_id)
VALUES (17, '2025-05-15', '10:00:00', 'scheduled', 'Follow-up consultation', 1, 1, 1);

-- DELETE:
DELETE FROM appointment WHERE appointment_id = 17;

-- UPDATE:
UPDATE appointment
SET status = 'completed', notes = 'Follow-up consultation completed successfully'
WHERE appointment_id = 14;

-- SELECT:
SELECT * FROM appointment WHERE appointment_id = 14;
SELECT * FROM appointment WHERE date = '2025-05-08' AND doctor_id = 1 ORDER BY time;
SELECT * FROM appointment WHERE status = 'scheduled' AND hospital_id = 1;

-- ---paying bill---

-- UPDATE (basic payment):
UPDATE billing_cost bc
JOIN patient_billing pb ON bc.billing_cost_id = pb.billing_cost_id
SET bc.total_amount = 300, bc.payment_status = 'paid'
WHERE bc.billing_cost_id = 24 AND pb.patient_id = 1;

-- UPDATE (zero out payment):
UPDATE billing_cost bc
JOIN patient_billing pb ON bc.billing_cost_id = pb.billing_cost_id
SET bc.total_amount = 0, bc.payment_status = 'paid'
WHERE bc.billing_cost_id = 23 AND pb.patient_id = 2;

-- UPDATE (insurance pays some):
UPDATE billing_cost bc
JOIN patient_billing pb ON bc.billing_cost_id = pb.billing_cost_id
SET bc.payment_status = 'paid', bc.insurance_claimed = 1, bc.insurance_covered = 200.00
WHERE bc.billing_cost_id = 22 AND pb.patient_id = 1;

-- ---insurance claim---

-- UPDATE (insurance claim submitted):
UPDATE billing_cost bc
JOIN patient_billing pb ON bc.billing_cost_id = pb.billing_cost_id
SET bc.insurance_claimed = 1, bc.insurance_covered = 150.00
WHERE bc.billing_cost_id = 21 AND pb.patient_id = 12;

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
WHERE a.doctor_id = 3 AND a.date = '2025-05-10'
ORDER BY a.time;

-- UPDATE (cancel appointment):
UPDATE appointment
SET status = 'cancelled', notes = 'Patient rescheduled'
WHERE appointment_id = 16 AND doctor_id = 3 AND date = '2025-05-10';

-- UPDATE (reschedule appointment):
UPDATE appointment
SET date = '2025-05-12', time = '11:00:00', status = 'scheduled', notes = 'Rescheduled appointment'
WHERE appointment_id = 16 AND doctor_id = 3 AND date = '2025-05-10';

-- ---Adding a new patient---

INSERT INTO patient (patient_id, first_name, last_name, phone, email, address)
VALUES (13, 'Chris', 'Evans', '555-987-6543', 'cevans@example.com', '789 Elm St');

-- ---Adding a new doctor---

INSERT INTO doctor (doctor_id, first_name, last_name, speciality, phone, email)
VALUES (4, 'Anna', 'Taylor', 3, '555-444-5555', 'ataylor@medcity.com');

-- ---Adding a new hospital---

INSERT INTO hospital (hospital_id, name, location, operating_hours, care_type)
VALUES (6, 'HealthFirst Clinic', 'Chicago, IL', '9:00 AM - 5:00 PM', 3);

-- ---Add doctor to hospital via hospital_doctors table---

INSERT INTO hospital_doctors (hospital_id, doctor_id)
VALUES (6, 4);

-- ---add a bill---

INSERT INTO billing_cost (billing_cost_id, total_amount, payment_status, insurance_claimed, insurance_covered)
VALUES (25, 200.00, 'unpaid', 0, 0);

INSERT INTO patient_billing (bill_id, billing_cost_id, appointment_id, patient_id, insurance_provider_id)
VALUES (25, 25, 14, 1, 1);

-- ---add new profession---

INSERT INTO professions (professions_id, type)
VALUES (21, 'Chiropractor');

-- Select ALL Doctors in a specific hospital:
SELECT * FROM doctor WHERE doctor_id IN (SELECT doctor_id FROM hospital_doctors WHERE hospital_id = 1);

-- Select ALL Doctors in a specific profession:
SELECT * FROM doctor 
WHERE speciality = 3;

