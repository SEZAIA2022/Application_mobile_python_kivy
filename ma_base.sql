-- MySQL dump 10.13  Distrib 8.0.40, for Win64 (x86_64)
--
-- Host: localhost    Database: projet_sezaia
-- ------------------------------------------------------
-- Server version	8.0.40

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `ask_repair`
--

DROP TABLE IF EXISTS `ask_repair`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ask_repair` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(100) NOT NULL,
  `date` date NOT NULL,
  `comment` text,
  `qr_code` varchar(100) NOT NULL,
  `hour_slot` time DEFAULT NULL,
  `status` enum('processing','repaired') NOT NULL DEFAULT 'processing',
  PRIMARY KEY (`id`),
  KEY `fk_username` (`username`),
  KEY `fk_qr_code` (`qr_code`),
  CONSTRAINT `fk_qr_code_ask_repair` FOREIGN KEY (`qr_code`) REFERENCES `qr_codes` (`qr_code`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_username_ask_repair` FOREIGN KEY (`username`) REFERENCES `users` (`username`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=281 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ask_repair`
--

LOCK TABLES `ask_repair` WRITE;
/*!40000 ALTER TABLE `ask_repair` DISABLE KEYS */;
INSERT INTO `ask_repair` VALUES (1,'vds','2025-06-16','yhehshs','https://larechercheparamedicalego.gogocarto.fr/','16:00:00','repaired'),(269,'vds','2025-06-23','hello','https://larechercheparamedicalego.gogocarto.fr/','08:00:00','processing'),(271,'vds','2025-06-17','bzbnzbbd','https://larechercheparamedicalego.gogocarto.fr/','08:00:00','processing'),(272,'vds','2025-06-26','bsbzb','https://larechercheparamedicalego.gogocarto.fr/','10:00:00','processing'),(273,'vds','2025-07-02','helo','https://larechercheparamedicalego.gogocarto.fr/','08:00:00','processing'),(274,'vds','2025-06-13','bdbdbsb','https://larechercheparamedicalego.gogocarto.fr/','14:00:00','processing'),(275,'vds','2025-06-18','hrllo','https://larechercheparamedicalego.gogocarto.fr/','08:00:00','processing'),(276,'vds','2025-06-18','bshsh','https://larechercheparamedicalego.gogocarto.fr/','10:00:00','processing'),(277,'vds','2025-06-18','hehs','https://larechercheparamedicalego.gogocarto.fr/','18:00:00','processing'),(278,'vds','2025-06-18','behshs','https://larechercheparamedicalego.gogocarto.fr/','18:00:00','processing'),(279,'vds','2025-06-18','hdhdh','https://larechercheparamedicalego.gogocarto.fr/','10:00:00','processing'),(280,'vds','2025-07-02','hemaa','https://larechercheparamedicalego.gogocarto.fr/','08:00:00','processing');
/*!40000 ALTER TABLE `ask_repair` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `qr_codes`
--

DROP TABLE IF EXISTS `qr_codes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `qr_codes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `locations` text,
  `user` varchar(100) DEFAULT NULL,
  `qr_code` varchar(100) NOT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `idx_qr_code` (`qr_code`),
  KEY `fk_user` (`user`),
  CONSTRAINT `fk_user` FOREIGN KEY (`user`) REFERENCES `users` (`username`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `qr_codes`
--

LOCK TABLES `qr_codes` WRITE;
/*!40000 ALTER TABLE `qr_codes` DISABLE KEYS */;
INSERT INTO `qr_codes` VALUES (8,'block A etage 1 porte 50','vds','https://larechercheparamedicalego.gogocarto.fr/',1),(9,NULL,NULL,'https://larechercheparamedicale.fr/a-propos/',0);
/*!40000 ALTER TABLE `qr_codes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `questions`
--

DROP TABLE IF EXISTS `questions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `questions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `text` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `questions`
--

LOCK TABLES `questions` WRITE;
/*!40000 ALTER TABLE `questions` DISABLE KEYS */;
INSERT INTO `questions` VALUES (1,'Aimez-vous la programmation ?'),(2,'Connaissez-vous Kivy ?'),(3,'Souhaitez-vous cr├®er des applications Android ?');
/*!40000 ALTER TABLE `questions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `registred_users`
--

DROP TABLE IF EXISTS `registred_users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `registred_users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(100) NOT NULL,
  `email` varchar(100) DEFAULT NULL,
  `role` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `registred_users`
--

LOCK TABLES `registred_users` WRITE;
/*!40000 ALTER TABLE `registred_users` DISABLE KEYS */;
INSERT INTO `registred_users` VALUES (37,'vds','housseinghannoum1@gmail.com','user'),(38,'vdsa','housseinghannoum803@gmail.com','user');
/*!40000 ALTER TABLE `registred_users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `responses`
--

DROP TABLE IF EXISTS `responses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `responses` (
  `id` int NOT NULL AUTO_INCREMENT,
  `question_id` int NOT NULL,
  `response` varchar(10) NOT NULL,
  `username` varchar(100) NOT NULL,
  `qr_code` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `question_id` (`question_id`),
  KEY `fk_username` (`username`),
  KEY `fk_qr_code_response` (`qr_code`),
  CONSTRAINT `fk_qr_code_response` FOREIGN KEY (`qr_code`) REFERENCES `qr_codes` (`qr_code`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_username` FOREIGN KEY (`username`) REFERENCES `users` (`username`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `responses_ibfk_1` FOREIGN KEY (`question_id`) REFERENCES `questions` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=476 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `responses`
--

LOCK TABLES `responses` WRITE;
/*!40000 ALTER TABLE `responses` DISABLE KEYS */;
INSERT INTO `responses` VALUES (440,1,'No','vds','https://larechercheparamedicalego.gogocarto.fr/'),(441,2,'Yes','vds','https://larechercheparamedicalego.gogocarto.fr/'),(442,3,'No','vds','https://larechercheparamedicalego.gogocarto.fr/'),(443,2,'No','vds','https://larechercheparamedicalego.gogocarto.fr/'),(444,1,'No','vds','https://larechercheparamedicalego.gogocarto.fr/'),(445,3,'Yes','vds','https://larechercheparamedicalego.gogocarto.fr/'),(446,1,'No','vds','https://larechercheparamedicalego.gogocarto.fr/'),(447,2,'Yes','vds','https://larechercheparamedicalego.gogocarto.fr/'),(448,3,'Yes','vds','https://larechercheparamedicalego.gogocarto.fr/'),(449,2,'No','vds','https://larechercheparamedicalego.gogocarto.fr/'),(450,1,'No','vds','https://larechercheparamedicalego.gogocarto.fr/'),(451,3,'No','vds','https://larechercheparamedicalego.gogocarto.fr/'),(452,2,'No','vds','https://larechercheparamedicalego.gogocarto.fr/'),(453,3,'No','vds','https://larechercheparamedicalego.gogocarto.fr/'),(454,1,'No','vds','https://larechercheparamedicalego.gogocarto.fr/'),(455,1,'No','vds','https://larechercheparamedicalego.gogocarto.fr/'),(456,3,'No','vds','https://larechercheparamedicalego.gogocarto.fr/'),(457,2,'No','vds','https://larechercheparamedicalego.gogocarto.fr/'),(458,3,'No','vds','https://larechercheparamedicalego.gogocarto.fr/'),(459,2,'No','vds','https://larechercheparamedicalego.gogocarto.fr/'),(460,1,'No','vds','https://larechercheparamedicalego.gogocarto.fr/'),(461,1,'Yes','vds','https://larechercheparamedicalego.gogocarto.fr/'),(462,2,'Yes','vds','https://larechercheparamedicalego.gogocarto.fr/'),(463,3,'Yes','vds','https://larechercheparamedicalego.gogocarto.fr/'),(464,2,'No','vds','https://larechercheparamedicalego.gogocarto.fr/'),(465,3,'No','vds','https://larechercheparamedicalego.gogocarto.fr/'),(466,1,'No','vds','https://larechercheparamedicalego.gogocarto.fr/'),(467,3,'Yes','vds','https://larechercheparamedicalego.gogocarto.fr/'),(468,1,'No','vds','https://larechercheparamedicalego.gogocarto.fr/'),(469,2,'No','vds','https://larechercheparamedicalego.gogocarto.fr/'),(470,1,'No','vds','https://larechercheparamedicalego.gogocarto.fr/'),(471,2,'Yes','vds','https://larechercheparamedicalego.gogocarto.fr/'),(472,3,'No','vds','https://larechercheparamedicalego.gogocarto.fr/'),(473,1,'No','vds','https://larechercheparamedicalego.gogocarto.fr/'),(474,3,'No','vds','https://larechercheparamedicalego.gogocarto.fr/'),(475,2,'Yes','vds','https://larechercheparamedicalego.gogocarto.fr/');
/*!40000 ALTER TABLE `responses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `email` varchar(100) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `phone_number` varchar(20) DEFAULT NULL,
  `address` varchar(255) NOT NULL,
  `role` varchar(50) DEFAULT NULL,
  `ville` varchar(100) NOT NULL,
  `code_postal` char(5) NOT NULL,
  `indicatif_telephonique` varchar(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `phone_number` (`phone_number`)
) ENGINE=InnoDB AUTO_INCREMENT=42 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (19,'Sezaia2024','$2b$12$1cVjFhER3K3ZkEoe7ClVouj5S6rxYj52iLMZiDIQ5U2b3yvu3flgi','hseinghannoum@gmail.com','2024-12-19 09:33:48','0786836539','*5 rue Pierre Maximin Audemar, 29200 Brest','admin','Brest','29200','+33'),(41,'vds','$2b$12$X55DVwNrWEExZFHJTcgEqeGzc3Uc3dULIk6gwooi9q.303MQ02JP2','housseinghannoum1@gmail.com','2025-06-11 09:58:24','0602204732','53 rue joseph le frapper','user','Brest','29200','+33');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-06-13 16:43:10

-- Pour extraire le base de donnee: mysqldump -u root -p projet_sezaia > ma_base.sql
