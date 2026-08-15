CREATE DATABASE  IF NOT EXISTS `printia` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `printia`;
-- MySQL dump 10.13  Distrib 8.0.43, for Win64 (x86_64)
--
-- Host: localhost    Database: printia
-- ------------------------------------------------------
-- Server version	8.0.43

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `facturas`
--

DROP TABLE IF EXISTS `facturas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `facturas` (
  `id_factura` int NOT NULL AUTO_INCREMENT,
  `id_usuario` int NOT NULL,
  `monto` decimal(10,2) NOT NULL,
  `fecha` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `detalle` varchar(255) NOT NULL,
  `transaction_id` varchar(255) NOT NULL,
  PRIMARY KEY (`id_factura`),
  UNIQUE KEY `transaction_id` (`transaction_id`),
  KEY `id_usuario` (`id_usuario`),
  CONSTRAINT `facturas_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `facturas`
--

LOCK TABLES `facturas` WRITE;
/*!40000 ALTER TABLE `facturas` DISABLE KEYS */;
INSERT INTO `facturas` VALUES (2,2,1000.00,'2026-08-08 20:28:21','PRO PrintIA (1 Mes)','fd2ade53-e9d0-42f3-9584-260250780be4'),(3,2,1000.00,'2026-08-08 20:34:11','PRO PrintIA (1 Mes)','9274aed8-44ab-44ed-8157-d280cc930b26'),(4,4,1000.00,'2026-08-08 21:40:20','PRO PrintIA (1 Mes)','608e27bf-35b5-4ba9-b5a7-d8ded8f76106'),(5,7,1000.00,'2026-08-08 21:46:28','PRO PrintIA (1 Mes)','b8c07e5a-e488-47e4-abad-3e0ed39f238e');
/*!40000 ALTER TABLE `facturas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `metricas`
--

DROP TABLE IF EXISTS `metricas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `metricas` (
  `id_metrica` int NOT NULL AUTO_INCREMENT,
  `id_modelo` int NOT NULL,
  `duracion` decimal(8,2) DEFAULT NULL,
  `detalle_error` varchar(255) DEFAULT NULL,
  `fecha_generacion` datetime DEFAULT CURRENT_TIMESTAMP,
  `recomendaciones` text,
  `total_descargas` int DEFAULT '0',
  `exitoso` tinyint DEFAULT NULL,
  PRIMARY KEY (`id_metrica`),
  KEY `fk_modelo_idx` (`id_modelo`),
  CONSTRAINT `fk_modelo2` FOREIGN KEY (`id_modelo`) REFERENCES `modelos` (`id_modelo`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `metricas`
--

LOCK TABLES `metricas` WRITE;
/*!40000 ALTER TABLE `metricas` DISABLE KEYS */;
INSERT INTO `metricas` VALUES (1,1,156.42,NULL,'2026-04-03 17:49:34',NULL,50,1),(2,2,127.85,NULL,'2026-04-07 17:56:27',NULL,24,1),(3,3,82.64,NULL,'2026-04-12 18:23:45',NULL,10,1),(4,4,128.37,NULL,'2026-04-16 21:23:07',NULL,33,1),(5,5,123.18,NULL,'2026-04-20 21:26:12',NULL,72,1),(6,6,76.52,NULL,'2026-04-24 21:33:14',NULL,41,1),(7,7,123.76,NULL,'2026-04-28 21:42:09',NULL,8,1),(8,8,158.94,NULL,'2026-05-02 13:05:06',NULL,77,1),(9,9,81.73,NULL,'2026-05-06 20:02:54',NULL,73,1),(10,10,185.67,NULL,'2026-05-11 11:38:24',NULL,73,1),(11,11,104.21,NULL,'2026-05-15 11:48:12',NULL,51,1),(12,12,58.43,NULL,'2026-05-19 12:38:11',NULL,23,1),(13,13,67.82,NULL,'2026-05-24 22:15:16',NULL,44,1),(14,14,36.94,NULL,'2026-05-29 23:20:00',NULL,51,1),(15,15,91.36,NULL,'2026-06-03 10:15:15',NULL,70,1),(16,16,168.47,NULL,'2026-06-07 22:28:35',NULL,40,1),(17,17,114.32,NULL,'2026-06-12 13:10:30',NULL,60,1),(18,18,143.18,NULL,'2026-06-16 20:58:36',NULL,44,1),(19,19,101.71,NULL,'2026-06-20 20:33:12',NULL,55,1),(20,20,55.40,NULL,'2026-06-24 20:49:49',NULL,19,1),(21,21,117.24,NULL,'2026-07-02 21:01:30',NULL,62,1),(22,22,80.27,NULL,'2026-07-06 21:05:34',NULL,55,1),(23,23,163.92,NULL,'2026-07-10 21:12:34',NULL,52,1),(24,24,108.71,NULL,'2026-07-14 21:16:01',NULL,21,1),(25,25,185.10,NULL,'2026-07-18 21:28:39',NULL,22,1),(26,26,154.68,NULL,'2026-07-22 21:33:10',NULL,29,1),(27,27,95.04,NULL,'2026-07-26 21:35:40',NULL,10,1),(28,28,199.97,NULL,'2026-07-30 21:46:27',NULL,2,1),(29,29,68.63,NULL,'2026-08-01 21:52:49',NULL,9,1),(30,30,62.91,NULL,'2026-08-03 21:56:17',NULL,1,1),(31,31,97.69,NULL,'2026-08-05 22:01:14',NULL,72,1),(32,32,107.34,NULL,'2026-08-07 22:04:40',NULL,1,1),(33,33,75.33,NULL,'2026-08-09 22:10:30',NULL,14,1),(34,34,63.43,NULL,'2026-08-11 22:18:10',NULL,2,1),(35,35,44.69,NULL,'2026-08-13 22:21:25',NULL,4,1),(36,36,103.19,NULL,'2026-08-15 22:23:33',NULL,5,1),(37,37,69.08,NULL,'2026-08-15 23:23:33',NULL,61,1);
/*!40000 ALTER TABLE `metricas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `modelos`
--

DROP TABLE IF EXISTS `modelos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `modelos` (
  `id_modelo` int NOT NULL AUTO_INCREMENT,
  `id_usuario` int NOT NULL,
  `prompt_texto` varchar(255) NOT NULL,
  `titulo` varchar(255) NOT NULL,
  `archivo_url` varchar(255) DEFAULT NULL,
  `imagen_url` varchar(255) DEFAULT NULL,
  `es_publico` tinyint NOT NULL DEFAULT '0',
  `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_actualizacion` datetime DEFAULT CURRENT_TIMESTAMP,
  `meshy_task_id` varchar(255) DEFAULT NULL,
  `feedback_ia` int DEFAULT '0',
  PRIMARY KEY (`id_modelo`),
  KEY `fk_usuario2_idx` (`id_usuario`),
  CONSTRAINT `fk_usuario2` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `modelos`
--

LOCK TABLES `modelos` WRITE;
/*!40000 ALTER TABLE `modelos` DISABLE KEYS */;
INSERT INTO `modelos` VALUES (1,2,'Soporte para celular','Soporte de celular simple','modelo_1_019dd535.stl','thumb_1_019dd535.png',1,'2026-04-03 17:49:34','2026-04-03 18:34:34',NULL,1),(2,5,'Auto con forma de calabaza','Auto con forma de calabaza sonriente','modelo_2_019dd53c.stl','thumb_2_019dd53c.png',1,'2026-04-07 17:56:27','2026-04-07 18:56:27',NULL,0),(3,5,'Guitarra stratocaster','Guitarra eléctrica stratocaster','modelo_3_019dd555.stl','thumb_3_019dd555.png',0,'2026-04-12 18:23:45','2026-04-12 19:38:45',NULL,0),(4,7,'Corazon con detalles','Corazón elegante','modelo_4_019dd5f9.stl','thumb_4_019dd5f9.png',1,'2026-04-16 21:23:07','2026-04-16 22:53:07',NULL,0),(5,10,'La pieza de ajedrez del rey','Rey ajedrez','modelo_5_019dd5fc.stl','thumb_5_019dd5fc.png',1,'2026-04-20 21:26:12','2026-04-20 21:56:12',NULL,1),(6,10,'Set de piezas de ajedrez, rey y peones','Peones y rey ajedrez','modelo_6_019dd602.stl','thumb_6_019dd602.png',1,'2026-04-24 21:33:14','2026-04-24 22:33:14',NULL,1),(7,5,'Un auto deportuvo con una flor','Auto con flor','modelo_7_019dd60a.stl','thumb_7_019dd60a.png',1,'2026-04-28 21:42:09','2026-04-28 23:12:09',NULL,0),(8,5,'Un gato sentado sobre sus patas traseras','Un gato sentado sobre sus patas traseras','modelo_8_019dd957.stl','thumb_8_019dd957.png',1,'2026-05-02 13:05:06','2026-05-02 13:50:06',NULL,1),(9,5,'Un perro sentado sobre sus patas traseras','Un perro amistoso','modelo_9_019df495.stl','thumb_9_019df495.png',1,'2026-05-06 20:02:54','2026-05-06 21:02:54','019df495-f8f1-753c-927e-bdd3558373ce',1),(10,7,'Llavero con forma de corazón, superficie plana, sin partes sueltas','Llavero de corazón','modelo_10_019df7ee.stl','thumb_10_019df7ee.png',1,'2026-05-11 11:38:24','2026-05-11 12:53:24','019df7ee-712c-799e-8ea5-7907bee11fd5',1),(11,3,'Calavera con base plana','Calavera decorativa','modelo_11_019df7f7.stl','thumb_11_019df7f7.png',1,'2026-05-15 11:48:12','2026-05-15 13:18:12','019df7f7-6773-7cc7-9880-e2fcc7e815c7',1),(12,6,'Helado de palito','Helado de palito','modelo_12_019e267e.stl','thumb_12_019e267e.png',1,'2026-05-19 12:38:11','2026-05-19 13:08:11','019e267e-5ed4-76fb-91ad-3e723ea5bd6b',0),(13,6,'Figura pokemon de charmander','Charmander','modelo_13_019e665a.stl','thumb_13_019e665a.png',1,'2026-05-24 22:15:16','2026-05-24 23:15:16','019e665a-b5b8-7f98-a87d-3071fc4dd799',1),(14,6,'Cocodrilo sentado sobre su cola','Cocodrilo gordo','modelo_14_019de854.stl','thumb_14_019de854.png',1,'2026-05-29 23:20:00','2026-05-30 00:50:00',NULL,1),(15,6,'Astronauta que sirva para decorar','Astronauta decorativo','modelo_15_019df901.stl','thumb_15_019df901.png',1,'2026-06-03 10:15:15','2026-06-03 11:00:15',NULL,1),(16,7,'Joyero pequeño','Joyero','modelo_16_019e6667.stl','thumb_16_019e6667.png',1,'2026-06-07 22:28:35','2026-06-07 23:28:35','019e6667-6a86-7776-9177-ea53d82d1a2c',0),(17,6,'Un portalápices de escritorio con forma de torre de un castillo medieval en ruinas','Un portalápices con forma de torre de un castillo medieval','modelo_17_019e4582.stl','thumb_17_019e4582.png',1,'2026-06-12 13:10:30','2026-06-12 14:25:30','019e4582-4fc9-7d27-8311-9cae64366100',0),(18,2,'Soporte para celular con forma de sillon','Soporte para celular con forma de sillon','modelo_18_019fd8de.stl','thumb_18_019fd8de.png',1,'2026-06-16 20:58:36','2026-06-16 22:28:36','019fd8de-8974-7c7b-9ab3-8a2027ba9ce0',0),(19,2,'Juguete de una gallina con forma redondeada','Juguete de una gallina con forma redondeada.','modelo_19_019fd8c7.stl','thumb_19_019fd8c7.png',1,'2026-06-20 20:33:12','2026-06-20 21:03:12','019fd8c7-a648-7806-90bb-61a4aa35b930',0),(20,7,'Llavero plano con garra de oso.','Llavero plano con garra de oso.','modelo_20_019fd8d6.stl','thumb_20_019fd8d6.png',1,'2026-06-24 20:49:49','2026-06-24 21:49:49','019fd8d6-e006-7b2f-bb35-796e511758d8',0),(21,7,'Bowl decorativo.','Bowl decorativo.','modelo_21_019fd8e1.stl','thumb_21_019fd8e1.png',1,'2026-07-02 21:01:30','2026-07-02 22:16:30','019fd8e1-8f7b-7328-a6f6-a2d2d4f29b1c',1),(22,2,'Juguete con forma de aguacate','Juguete con forma de aguacate','modelo_22_019fd8e5.stl','thumb_22_019fd8e5.png',1,'2026-07-06 21:05:34','2026-07-06 22:35:34','019fd8e5-4b32-7b02-9ce6-98e2844f0fef',1),(23,2,'Juegue de oso de peluche','Jueguete de oso de peluche','modelo_23_019fd8eb.stl','thumb_23_019fd8eb.png',1,'2026-07-10 21:12:34','2026-07-10 21:42:34','019fd8eb-b24c-740c-aebd-813b8cee3f6c',0),(24,6,'Una hamburguesa con doble carne, lechuga y tomate.','Una hamburguesa con doble carne, lechuga y tomate.','modelo_24_019fd8ee.stl','thumb_24_019fd8ee.png',1,'2026-07-14 21:16:01','2026-07-14 22:16:01','019fd8ee-d969-74b6-bbd3-48e522793be5',0),(25,8,'Portalapices','Portalapices','modelo_25_019fd8fa.stl','thumb_25_019fd8fa.png',1,'2026-07-18 21:28:39','2026-07-18 22:43:39','019fd8fa-6b1b-76c3-957b-3c6c0033fa83',1),(26,6,'Pelota de futbol','Pelota de futbol','modelo_26_019fd8fe.stl','thumb_26_019fd8fe.png',1,'2026-07-22 21:33:10','2026-07-22 23:03:10','019fd8fe-8ca5-72d6-a2b3-ba1794e5def3',0),(27,4,'Emoji sonriente con forma plana','Emoji sonriente con forma plana','modelo_27_019fd900.stl','thumb_27_019fd900.png',1,'2026-07-26 21:35:40','2026-07-26 22:05:40','019fd900-d5b3-77df-b5c2-aea052a5961c',0),(28,4,'Pulgar para arriba','Emoji de pulgar para arriba','modelo_28_019fd90a.stl','thumb_28_019fd90a.png',1,'2026-07-30 21:46:27','2026-07-30 22:46:27','019fd90a-b5a7-74e3-917d-2fcc9f7bc2ae',-1),(29,4,'Caja sin tapa de 20 cm de largo, 10 cm de profundidad y 8 cm de altura','Caja sin tapa de 20 cm de largo, 10 cm de profundidad y 8 cm de altura','modelo_29_019fd910.stl','thumb_29_019fd910.png',1,'2026-08-01 21:52:49','2026-08-01 23:07:49','019fd910-8b41-7a6c-9803-1c297eb77002',0),(30,4,'Una tuerca','Una tuerca','modelo_30_019fd913.stl','thumb_30_019fd913.png',0,'2026-08-03 21:56:17','2026-08-03 22:56:17','019fd913-b7c7-76be-b73e-6c9d85486454',-1),(31,2,'Soldado de juguete','Soldado de juguete','modelo_31_019fd918.stl','thumb_31_019fd918.png',1,'2026-08-05 22:01:14','2026-08-05 23:16:14','019fd918-3e9c-7bd4-a292-243e38eb1d20',1),(32,4,'Dinosaurio','Dinosaurio','modelo_32_019fd91b.stl','thumb_32_019fd91b.png',0,'2026-08-07 22:04:40','2026-08-07 23:34:40','019fd91b-65cb-7c0c-96ad-adb8558c6ee4',-1),(33,6,'Pata de pollo tipo animado para usar de llavero','Pata de pollo tipo animado para usar de llavero','modelo_33_019fd920.stl','thumb_33_019fd920.png',1,'2026-08-09 22:10:30','2026-08-09 22:40:30','019fd920-b305-74e0-9244-a51b4ff34f3f',-1),(34,4,'Tapa para botella','Tapa para botella','modelo_34_019fd927.stl','thumb_34_019fd927.png',0,'2026-08-11 22:18:10','2026-08-11 23:18:10','019fd927-c196-799a-b061-309451ef7fbe',-1),(35,5,'keychain de un auto','keychain de un auto','modelo_35_019fd92a.stl','thumb_35_019fd92a.png',1,'2026-08-13 22:21:25','2026-08-13 23:36:25','019fd92a-bbaf-7e2c-aaaf-7469db0da4a7',-1),(36,5,'Pista de carreras de formula 1 para usar de keychain','Pista de carreras de formula 1 para usar de keychain','modelo_36_019fd92c.stl','thumb_36_019fd92c.png',1,'2026-08-15 22:23:33','2026-08-15 23:53:33','019fd92c-abe5-7a5c-bab5-a1945286b8cc',-1),(37,2,'Estrella de mar','Estrella de mar','modelo_37_019fed87.stl','thumb_37_019fed87.png',1,'2026-08-15 23:23:33','2026-08-16 00:23:33','019fed87-c81f-7d52-830a-c4aac99f1a59',1);
/*!40000 ALTER TABLE `modelos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `planes`
--

DROP TABLE IF EXISTS `planes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `planes` (
  `id_plan` int NOT NULL AUTO_INCREMENT,
  `nombre_plan` varchar(50) NOT NULL,
  `limite_exportaciones_mensual` int NOT NULL,
  `precio` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id_plan`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `planes`
--

LOCK TABLES `planes` WRITE;
/*!40000 ALTER TABLE `planes` DISABLE KEYS */;
INSERT INTO `planes` VALUES (1,'PRO',15,10.00);
/*!40000 ALTER TABLE `planes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `suscripciones`
--

DROP TABLE IF EXISTS `suscripciones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `suscripciones` (
  `id_suscripcion` int NOT NULL,
  `id_plan` int NOT NULL,
  `id_usuario` int NOT NULL,
  `fecha_inicio` date NOT NULL,
  `fecha_fin` date NOT NULL,
  `estado` varchar(50) DEFAULT NULL,
  `metodo_pago` varchar(255) DEFAULT NULL,
  `modelos_restantes` int NOT NULL,
  PRIMARY KEY (`id_suscripcion`),
  KEY `fk_plan_idx` (`id_plan`),
  KEY `fk_usuario_idx` (`id_usuario`),
  CONSTRAINT `fk_plan` FOREIGN KEY (`id_plan`) REFERENCES `planes` (`id_plan`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `suscripciones`
--

LOCK TABLES `suscripciones` WRITE;
/*!40000 ALTER TABLE `suscripciones` DISABLE KEYS */;
INSERT INTO `suscripciones` VALUES (1,1,2,'2026-08-08','2026-09-07','Activa','Pasarela Ficticia',15),(2,1,4,'2026-08-08','2026-09-07','Activa','Pasarela Ficticia',15),(3,1,7,'2026-08-08','2026-09-07','Activa','Pasarela Ficticia',10);
/*!40000 ALTER TABLE `suscripciones` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `id_usuario` int NOT NULL AUTO_INCREMENT,
  `email` varchar(255) NOT NULL,
  `clave` varchar(255) NOT NULL,
  `nombre_usuario` varchar(50) NOT NULL,
  `fecha_registro` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `es_admin` tinyint NOT NULL DEFAULT '0',
  `imagen` varchar(255) DEFAULT NULL,
  `activo` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `email_UNIQUE` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES (1,'admin@admin.com','scrypt:32768:8:1$QtbAleDyfsF7dDcu$4ea970dc46ebdd8302d1a1bb7f6239c14431736f0640e1276b25c581e9645dbb74b57318050fbea14528b6cd1f548e2b61860c629c2275610584159cc8b9663c','admin','2026-01-01 14:58:21',1,'user_1_f323fd03.jpg',1),(2,'santiauat@hotmail.com','scrypt:32768:8:1$i7XacbQNjGrAkGsG$cc1f3c0d20913e5bbc8fe972e9e720919f3391dfc32eefa84a6db3ed26b45804488c68ca7a60d0ee0fa17a4df5d7a7061e8d06d46ca80db8fbc6745e09dfb2c3','santiaa','2026-01-01 15:01:00',0,'user_2_633f58d5.webp',1),(3,'fransbebobruno@gmail.com','scrypt:32768:8:1$4CkAnLVhHRw3tpxB$82d32b546a894fac4c011fd43ecfb2e1c99ee9828aa11a55f4851211f87e449f702c7657fcdaa20abda954e84209c6f7bae58c65efe7284531d947274a5b269f','franciscobr','2026-01-01 15:02:07',0,'user_3_317d6cae.jpg',1),(4,'jero@gmail.com','scrypt:32768:8:1$Q2Apslz6odrvAEMg$c612e9a0c94fc6fd04d02b43c41a8c2453f1801d129a9c1a66e6de3c152e69d4c5ef0352916a5ecb4a301e44ae4b9b607c3d298f27ad441f2c508bb50d764f96','jeroalvarez','2026-03-03 15:02:46',0,NULL,1),(5,'tomi@gmail.com','scrypt:32768:8:1$UoLuvwBNsYlo7qOe$4e03241fd1e13d9a4356afbe7107de893d431e07b0a6ab0b220f07140787bafd4d0e748d84e9c288dc95a24a01d0ea6413bc7858fab1e647d952fe69e1deee33','tomigigli','2026-03-03 15:03:02',0,NULL,1),(6,'benja@gmail.com','scrypt:32768:8:1$Kr2HLJQAMo37vY6d$dc3537a208b8f8300c75b795e69da838edfbe40c8621744896d6d03064fa9a6315128c622070b55e06c5fe16182755b45d532337c4c3772158c3fb7040f3fc92','benjafares','2026-03-03 15:03:19',0,NULL,1),(7,'laura@gmail.com','scrypt:32768:8:1$xU5kg2qCXCxj8Lz3$7da1190b8eb2ff1bafb01f9dfc83c2de97967575aee123d9cefa52bb9b9c00de8bec948bac2ff436d3ce3da3cabfb58e3e79343dbd458966cd32966290dc0c93','lauratulian','2026-03-03 15:03:31',0,NULL,1),(8,'gino@gmail.com','scrypt:32768:8:1$oVioNDn5w0vKO1IX$4058589052fe8653df637ad6298ae654cc698aa76be211e5265528e193917efd182acefe8dfc074d9f20395b6d4df94b5cef124e7e29bfcf28eadecbcc8ce842','ginoagostinelli','2026-06-05 15:04:03',0,NULL,1),(9,'juan@gmail.com','scrypt:32768:8:1$yatRgmwPbhJFocz6$eaf7f05242f6a8a58ca5729182d0454920f622450ff389649e76e2cb68c7858dd504d9e4a917d353e03416c77b47f19bc9a42418032a09c1bb9d473ec8fe51c0','juan perez','2026-06-06 15:05:34',0,'user_9_f1055c89.webp',1),(10,'juansito@gmail.com','scrypt:32768:8:1$sMEtQlwr3iWdLncX$4b09339b2c872ba794123ed03b3f0149887666dbe466323a5fc261ab48d77c316a82e7c40a702b41cbb89c38584a031aa8751b02544218fe49ae13b78b95d073','juansito','2026-06-10 15:06:23',0,NULL,1),(11,'victoria@gmail.com','scrypt:32768:8:1$EA4h6OitPbhFpvPt$27ac5deff17c1f702cec2f66fc67b07cabca09700f1f02b04df1d1d162d58af42815a7b51e9fb3ad82e514387508a83ba1e1a5b8fd3736c333721f1f5254a896','vicky garreta','2026-06-16 15:07:23',0,'user_11_42b33dae.jpg',1);
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `valoraciones`
--

DROP TABLE IF EXISTS `valoraciones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `valoraciones` (
  `id_valoracion` int NOT NULL AUTO_INCREMENT,
  `id_modelo` int NOT NULL,
  `id_usuario` int NOT NULL,
  `puntuacion` int NOT NULL,
  `comentario` varchar(255) DEFAULT NULL,
  `fecha` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_valoracion`),
  KEY `fk_usuario3_idx` (`id_usuario`),
  KEY `fk_modelo_idx` (`id_modelo`),
  CONSTRAINT `fk_modelo` FOREIGN KEY (`id_modelo`) REFERENCES `modelos` (`id_modelo`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_usuario3` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `valoraciones`
--

LOCK TABLES `valoraciones` WRITE;
/*!40000 ALTER TABLE `valoraciones` DISABLE KEYS */;
INSERT INTO `valoraciones` VALUES (1,11,3,4,'Imprimir con soportes!','2026-08-08 20:37:44'),(2,21,9,5,'Me gusto!','2026-08-08 21:48:28'),(3,8,9,5,'Muy lindo','2026-08-08 21:48:58'),(4,22,9,5,'Muy bueno','2026-08-08 21:50:20'),(5,35,9,2,'medio raro','2026-08-08 21:50:36'),(6,24,9,1,'Complicado de imprimir','2026-08-08 21:50:51'),(7,23,9,5,'hermoso','2026-08-08 21:51:13'),(8,31,9,5,'Wow!','2026-08-08 21:51:32'),(9,5,9,5,'','2026-08-08 21:52:04'),(10,17,9,5,'','2026-08-08 21:52:24'),(11,5,10,5,'Lo imprimi y quedo bastante bien','2026-08-08 21:53:07'),(12,6,10,4,'Buen set','2026-08-08 21:53:16'),(13,1,10,5,'Bastante util','2026-08-08 21:53:53'),(14,21,10,4,'Bellisimo','2026-08-08 21:54:07'),(15,8,10,5,'','2026-08-08 21:54:30'),(16,23,10,5,'','2026-08-08 21:54:41'),(17,1,11,4,'','2026-08-08 21:55:33'),(18,15,11,5,'Muy buenoo!','2026-08-08 21:56:05'),(19,21,11,5,'','2026-08-08 21:56:24'),(20,23,11,5,'','2026-08-08 21:56:35'),(21,27,11,3,'','2026-08-08 21:56:45');
/*!40000 ALTER TABLE `valoraciones` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-08-15 16:38:20
