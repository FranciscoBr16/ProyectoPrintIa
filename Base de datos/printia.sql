CREATE DATABASE  IF NOT EXISTS `printia` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `printia`;
-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: localhost    Database: printia
-- ------------------------------------------------------
-- Server version	8.0.44

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
  `exitoso` tinyint DEFAULT NULL,
  `fecha_generacion` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_metrica`),
  KEY `fk_modelo_idx` (`id_modelo`),
  CONSTRAINT `fk_modelo2` FOREIGN KEY (`id_modelo`) REFERENCES `modelos` (`id_modelo`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `metricas`
--

LOCK TABLES `metricas` WRITE;
/*!40000 ALTER TABLE `metricas` DISABLE KEYS */;
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
  `dim_x` float DEFAULT '9',
  `dim_y` float DEFAULT '3',
  `dim_z` float DEFAULT '3',
  `recomendaciones` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id_modelo`),
  KEY `fk_usuario2_idx` (`id_usuario`),
  CONSTRAINT `fk_usuario2` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `modelos`
--

LOCK TABLES `modelos` WRITE;
/*!40000 ALTER TABLE `modelos` DISABLE KEYS */;
INSERT INTO `modelos` VALUES (16,2,'soporte para celular','Modelo basado en: soporte para celular...','modelo_16_019dd535.stl','thumb_16_019dd535.png',1,'2026-04-28 17:49:34','2026-04-28 18:15:37',9,3,3,NULL),(17,1,'auto con forma de calabaza \r\n','Modelo basado en: auto con forma de ca...','modelo_17_019dd53c.stl','thumb_17_019dd53c.png',1,'2026-04-28 17:56:27','2026-04-28 21:24:57',100,33.3,33.3,NULL),(18,1,'Bajo fender (Instrumento)','Modelo basado en: Bajo fender (Instrum...','modelo_18_019dd552.stl','thumb_18_019dd552.png',0,'2026-04-28 18:21:09','2026-04-28 18:22:14',9,3,3,NULL),(19,1,'Guitarra stratocaster ','Modelo basado en: Guitarra stratocaste...','modelo_19_019dd555.stl','thumb_19_019dd555.png',0,'2026-04-28 18:23:45','2026-04-28 18:25:07',9,3,3,NULL),(20,1,'Maceta con forma de corazon','Maceta con forma de corazon','modelo_20_019dd5f9.stl','thumb_20_019dd5f9.png',0,'2026-04-28 21:23:07','2026-04-28 21:25:15',9,3,3,NULL),(21,1,'peon ajedrez','Peon ajedrez','modelo_21_019dd5fc.stl','thumb_21_019dd5fc.png',0,'2026-04-28 21:26:12','2026-04-28 21:28:15',9,3,3,NULL),(22,1,'A Pawn of Chess','A pawn of chess','modelo_22_019dd602.stl','thumb_22_019dd602.png',0,'2026-04-28 21:33:14','2026-04-28 21:34:30',9,3,3,NULL),(23,1,'A car with a flower up a roof','A car with a flower up a roof','modelo_23_019dd60a.stl','thumb_23_019dd60a.png',0,'2026-04-28 21:42:09','2026-04-28 21:44:12',9,3,3,NULL);
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
INSERT INTO `planes` VALUES (1,'PRO',-1,9.99);
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
INSERT INTO `suscripciones` VALUES (1,1,1,'2026-04-20','2026-05-20','Activa','Tarjeta',-1);
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
  `generaciones_usadas` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `email_UNIQUE` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES (1,'santiauat@hotmail.com','scrypt:32768:8:1$AMncDim1Y1W94ZDr$d4bc196cc86945d638dd233a04c4715f42e5db519381d07b14d191c79095d023c4a0925155dcf3e3f52b81d2d5c83929c293cf13b60589a7d478d552ce002f63','santiauat','2026-04-20 23:21:20',0,'user_1_3cdbe997.jpg',0),(2,'somosdecalle@gmail.com','scrypt:32768:8:1$Yvc00wgnDBKaRLNn$9f7232fe86e3ed9032b7cca49ba731b8dfb454122c8e716c046dc35fa1b4cda7a19bff152468ba98b4d0542ff607c5fe68aa72e2ab734a1b990e544934d259b0','mongotofloro','2026-04-20 23:46:49',0,'user_2_d29d44f2.jpg',0),(3,'ricardodarin@gmail.com','scrypt:32768:8:1$3Ru7A0GS96tat7Ez$e8bba12a0683d261fd6d2f46a502bf12f0dc6f41a094252bb78d3415e1f0fa850372e0d888c680ee5043532c2536f5b5580cd06ed2c5a580752637b60e413d27','ricdarin','2026-04-22 00:22:29',0,NULL,0),(4,'test@example.com','scrypt:32768:8:1$ROJA40JIHA92UgKW$169720327bdc0e5e4f546139e362781b6f9479fbbfc78099b1b6cbdeb7b64c82aaee8f0861d243b19d0bc0e6eae31190016b790f35efd817c9acefb62d1087cb','testuser','2026-04-22 21:53:43',0,NULL,0);
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `valoraciones`
--

LOCK TABLES `valoraciones` WRITE;
/*!40000 ALTER TABLE `valoraciones` DISABLE KEYS */;
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

-- Dump completed on 2026-04-28 18:50:37
