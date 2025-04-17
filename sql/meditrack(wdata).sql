-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Apr 14, 2025 at 09:53 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `meditrack`
--

-- --------------------------------------------------------

--
-- Table structure for table `appointment`
--

CREATE TABLE `appointment` (
  `appointment_id` int(11) NOT NULL AUTO_INCREMENT,
  `date` date DEFAULT NULL,
  `time` time DEFAULT NULL,
  `status` varchar(100) DEFAULT NULL,
  `notes` varchar(100) DEFAULT NULL,
  `patient_id` int(11) DEFAULT NULL,
  `doctor_id` int(11) DEFAULT NULL,
  `hospital_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`appointment_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `appointment`
--

INSERT INTO `appointment` (`appointment_id`, `date`, `time`, `status`, `notes`, `patient_id`, `doctor_id`, `hospital_id`) VALUES
(1, '2025-05-01', '09:00:00', 'Scheduled', 'Regular checkup', 1, 1, 1),
(2, '2025-05-02', '14:00:00', 'Scheduled', 'Routine dental checkup', 2, 2, 2),
(3, '2025-05-03', '10:00:00', 'Scheduled', 'Follow-up visit', 1, 1, 1),
(4, '2025-05-04', '11:00:00', 'Scheduled', 'Consultation for teeth cleaning', 2, 2, 2),
(5, '2025-05-05', '13:00:00', 'Scheduled', 'Routine eye exam', 1, 3, 1),
(6, '2025-05-06', '15:00:00', 'Scheduled', 'Follow-up for eye exam', 1, 3, 1),
(7, '2025-05-07', '09:30:00', 'Scheduled', 'Dental checkup', 2, 2, 2),
(112, '2025-04-22', '13:00:00', 'completed', 'Routine check-up completed successfully', 12, 3, 2),
(122, '2025-04-30', '13:00:00', 'scheduled', 'Cancer Screening', 12, 3, 2);

-- --------------------------------------------------------

--
-- Table structure for table `billing_cost`
--

CREATE TABLE `billing_cost` (
  `billing_cost_id` int(11) NOT NULL AUTO_INCREMENT,
  `total_amount` double DEFAULT NULL,
  `payment_status` varchar(100) DEFAULT NULL,
  `insurance_claimed` tinyint(1) DEFAULT NULL,
  `insurance_covered` double DEFAULT NULL,
  PRIMARY KEY (`billing_cost_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `billing_cost`
--

INSERT INTO `billing_cost` (`billing_cost_id`, `total_amount`, `payment_status`, `insurance_claimed`, `insurance_covered`) VALUES
(1, 200, 'Paid', 1, 150),
(2, 300, 'Pending', 1, 250),
(3, 500, 'Paid', 1, 400),
(4, 150, 'Pending', 1, 100),
(5, 250, 'Paid', 0, 0),
(6, 450, 'Pending', 1, 350),
(7, 300, 'Paid', 1, 250),
(8, 150, 'Pending', 1, 100),
(9, 250, 'Paid', 0, 0),
(10, 450, 'Pending', 1, 350),
(11, 200, 'Paid', 1, 150);

-- --------------------------------------------------------

--
-- Table structure for table `doctor`
--

CREATE TABLE `doctor` (
  `doctor_id` int(11) NOT NULL AUTO_INCREMENT,
  `first_name` varchar(100) DEFAULT NULL,
  `last_name` varchar(100) DEFAULT NULL,
  `speciality` int(11) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`doctor_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `doctor`
--

INSERT INTO `doctor` (`doctor_id`, `first_name`, `last_name`, `speciality`, `phone`, `email`) VALUES
(1, 'John', 'Doe', 1, '555-1234', 'jdoe@medcity.com'),
(2, 'Jane', 'Smith', 2, '555-5678', 'jsmith@carewell.com'),
(3, 'Emily', 'Jones', 3, '555-8765', 'ejones@medcity.com');

-- --------------------------------------------------------

--
-- Table structure for table `health_demographics`
--

CREATE TABLE `health_demographics` (
  `patient_id` int(11) NOT NULL,
  `date_recorded` date DEFAULT NULL,
  `date_of_birth` date DEFAULT NULL,
  `weight` double DEFAULT NULL,
  `height` double DEFAULT NULL,
  `health_status` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `health_demographics`
--

INSERT INTO `health_demographics` (`patient_id`, `date_recorded`, `date_of_birth`, `weight`, `height`, `health_status`) VALUES
(1, '2025-04-01', '1990-06-15', 75, 180, 'Healthy'),
(2, '2025-04-02', '1985-09-10', 65, 165, 'Healthy');

-- --------------------------------------------------------

--
-- Table structure for table `hospital`
--

CREATE TABLE `hospital` (
  `hospital_id` int(11) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `location` varchar(100) DEFAULT NULL,
  `operating_hours` varchar(100) DEFAULT NULL,
  `care_type` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `hospital`
--

INSERT INTO `hospital` (`hospital_id`, `name`, `location`, `operating_hours`, `care_type`) VALUES
(1, 'MedCity Hospital', 'New York, NY', '24/7', 1),
(2, 'CareWell Medical Center', 'Los Angeles, CA', '9:00 AM - 6:00 PM', 2);

-- --------------------------------------------------------

--
-- Table structure for table `hospital_doctors`
--

CREATE TABLE `hospital_doctors` (
  `doctor_id` int(11) NOT NULL,
  `hospital_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `hospital_doctors`
--

INSERT INTO `hospital_doctors` (`doctor_id`, `hospital_id`) VALUES
(1, 1),
(2, 2),
(3, 1);

-- --------------------------------------------------------

--
-- Table structure for table `insurance_provider`
--

CREATE TABLE `insurance_provider` (
  `insurance_id` int(11) NOT NULL AUTO_INCREMENT,
  `insurance_name` varchar(100) DEFAULT NULL,
  `contact_number` varchar(20) DEFAULT NULL,
  `insurance_type` int(11) DEFAULT NULL,
  PRIMARY KEY (`insurance_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `insurance_provider`
--

INSERT INTO `insurance_provider` (`insurance_id`, `insurance_name`, `contact_number`, `insurance_type`) VALUES
(1, 'HealthPlus', '555-8888', 1),
(2, 'CareFirst', '555-9999', 2),
(3, 'SecureCare', '555-1234', 1),
(4, 'OptiHealth', '555-5678', 3);

-- --------------------------------------------------------

--
-- Table structure for table `patient`
--

CREATE TABLE `patient` (
  `patient_id` int(11) NOT NULL AUTO_INCREMENT,
  `first_name` varchar(100) DEFAULT NULL,
  `last_name` varchar(100) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `address` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`patient_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `patient`
--

INSERT INTO `patient` (`patient_id`, `first_name`, `last_name`, `phone`, `email`, `address`) VALUES
(1, 'Michael', 'Johnson', '555-1111', 'mjohnson@email.com', '123 Oak St, New York, NY'),
(2, 'Sarah', 'Williams', '555-2222', 'swilliams@email.com', '456 Pine St, Los Angeles, CA'),
(12, 'Paige', 'Ogden', '1234567890', 'podgen@kent.edu', 'a place');

-- --------------------------------------------------------

--
-- Table structure for table `patient_billing`
--

CREATE TABLE `patient_billing` (
  `bill_id` int(11) NOT NULL AUTO_INCREMENT,
  `billing_cost_id` int(11) DEFAULT NULL,
  `appointment_id` int(11) DEFAULT NULL,
  `patient_id` int(11) DEFAULT NULL,
  `insurance_provider_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`bill_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `patient_billing`
--

INSERT INTO `patient_billing` (`bill_id`, `billing_cost_id`, `appointment_id`, `patient_id`, `insurance_provider_id`) VALUES
(1, 1, 1, 1, 1),
(2, 2, 2, 2, 1),
(3, 3, 1, 1, 1),
(4, 4, 2, 2, 2),
(5, 5, 1, 1, 2),
(6, 6, 2, 2, 1),
(7, 7, 3, 1, 1),
(8, 8, 4, 2, 2),
(9, 9, 5, 1, 2),
(10, 10, 6, 1, 3),
(11, 11, 7, 2, 1);

-- --------------------------------------------------------

--
-- Table structure for table `patient_insurance`
--

CREATE TABLE `patient_insurance` (
  `patient_id` int(11) NOT NULL,
  `insurance_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `patient_insurance`
--

INSERT INTO `patient_insurance` (`patient_id`, `insurance_id`) VALUES
(1, 1),
(1, 3),
(2, 2),
(2, 4);

-- --------------------------------------------------------

--
-- Table structure for table `professions`
--

CREATE TABLE `professions` (
  `professions_id` int(11) NOT NULL AUTO_INCREMENT,
  `type` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`professions_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `professions`
--

INSERT INTO `professions` (`professions_id`, `type`) VALUES
(1, 'Doctor'),
(2, 'Dentist'),
(3, 'Optometrist'),
(4, 'Nurse'),
(5, 'Therapist');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `appointment`
--
ALTER TABLE `appointment`
  ADD KEY `patient_id` (`patient_id`),
  ADD KEY `doctor_id` (`doctor_id`),
  ADD KEY `hospital_id` (`hospital_id`);

--
-- Indexes for table `billing_cost`
--
-- No changes needed as primary key is already defined in table structure.

--
-- Indexes for table `doctor`
--
ALTER TABLE `doctor`
  ADD KEY `speciality` (`speciality`);

--
-- Indexes for table `health_demographics`
--
ALTER TABLE `health_demographics`
  ADD PRIMARY KEY (`patient_id`);

--
-- Indexes for table `hospital`
--
ALTER TABLE `hospital`
  ADD PRIMARY KEY (`hospital_id`),
  ADD KEY `care_type` (`care_type`);

--
-- Indexes for table `hospital_doctors`
--
ALTER TABLE `hospital_doctors`
  ADD PRIMARY KEY (`doctor_id`,`hospital_id`),
  ADD KEY `hospital_id` (`hospital_id`);

--
-- Indexes for table `insurance_provider`
--
ALTER TABLE `insurance_provider`
  ADD KEY `insurance_type` (`insurance_type`);

--
-- Indexes for table `patient`
--
-- No changes needed as primary key is already defined in table structure.

--
-- Indexes for table `patient_billing`
--
ALTER TABLE `patient_billing`
  ADD KEY `billing_cost_id` (`billing_cost_id`),
  ADD KEY `appointment_id` (`appointment_id`),
  ADD KEY `patient_id` (`patient_id`),
  ADD KEY `insurance_provider_id` (`insurance_provider_id`);

--
-- Indexes for table `patient_insurance`
--
ALTER TABLE `patient_insurance`
  ADD PRIMARY KEY (`patient_id`,`insurance_id`),
  ADD KEY `insurance_id` (`insurance_id`);

--
-- Indexes for table `professions`
--
-- No changes needed as primary key is already defined in table structure.

--
-- Constraints for dumped tables
--

--
-- Constraints for table `appointment`
--
ALTER TABLE `appointment`
  ADD CONSTRAINT `appointment_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patient` (`patient_id`),
  ADD CONSTRAINT `appointment_ibfk_2` FOREIGN KEY (`doctor_id`) REFERENCES `doctor` (`doctor_id`),
  ADD CONSTRAINT `appointment_ibfk_3` FOREIGN KEY (`hospital_id`) REFERENCES `hospital` (`hospital_id`);

--
-- Constraints for table `doctor`
--
ALTER TABLE `doctor`
  ADD CONSTRAINT `doctor_ibfk_1` FOREIGN KEY (`speciality`) REFERENCES `professions` (`professions_id`);

--
-- Constraints for table `health_demographics`
--
ALTER TABLE `health_demographics`
  ADD CONSTRAINT `health_demographics_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patient` (`patient_id`);

--
-- Constraints for table `hospital`
--
ALTER TABLE `hospital`
  ADD CONSTRAINT `hospital_ibfk_1` FOREIGN KEY (`care_type`) REFERENCES `professions` (`professions_id`);

--
-- Constraints for table `hospital_doctors`
--
ALTER TABLE `hospital_doctors`
  ADD CONSTRAINT `hospital_doctors_ibfk_1` FOREIGN KEY (`doctor_id`) REFERENCES `doctor` (`doctor_id`),
  ADD CONSTRAINT `hospital_doctors_ibfk_2` FOREIGN KEY (`hospital_id`) REFERENCES `hospital` (`hospital_id`);

--
-- Constraints for table `insurance_provider`
--
ALTER TABLE `insurance_provider`
  ADD CONSTRAINT `insurance_provider_ibfk_1` FOREIGN KEY (`insurance_type`) REFERENCES `professions` (`professions_id`);

--
-- Constraints for table `patient_billing`
--
ALTER TABLE `patient_billing`
  ADD CONSTRAINT `patient_billing_ibfk_1` FOREIGN KEY (`billing_cost_id`) REFERENCES `billing_cost` (`billing_cost_id`),
  ADD CONSTRAINT `patient_billing_ibfk_2` FOREIGN KEY (`appointment_id`) REFERENCES `appointment` (`appointment_id`),
  ADD CONSTRAINT `patient_billing_ibfk_3` FOREIGN KEY (`patient_id`) REFERENCES `patient` (`patient_id`),
  ADD CONSTRAINT `patient_billing_ibfk_4` FOREIGN KEY (`insurance_provider_id`) REFERENCES `insurance_provider` (`insurance_id`);

--
-- Constraints for table `patient_insurance`
--
ALTER TABLE `patient_insurance`
  ADD CONSTRAINT `patient_insurance_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patient` (`patient_id`),
  ADD CONSTRAINT `patient_insurance_ibfk_2` FOREIGN KEY (`insurance_id`) REFERENCES `insurance_provider` (`insurance_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
