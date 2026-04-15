CREATE DATABASE  IF NOT EXISTS `printia` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `printia`;
-- MySQL dump 10.13  Distrib 8.0.42, for Win64 (x86_64)
--
-- Host: localhost    Database: printia
-- ------------------------------------------------------
-- Server version	8.0.42

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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
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
  PRIMARY KEY (`id_modelo`),
  KEY `fk_usuario2_idx` (`id_usuario`),
  CONSTRAINT `fk_usuario2` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `modelos`
--

LOCK TABLES `modelos` WRITE;
/*!40000 ALTER TABLE `modelos` DISABLE KEYS */;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `planes`
--

LOCK TABLES `planes` WRITE;
/*!40000 ALTER TABLE `planes` DISABLE KEYS */;
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
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `email_UNIQUE` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
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

-- Dump completed on 2026-04-15 15:54:20
