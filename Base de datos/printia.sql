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
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `facturas`
--

LOCK TABLES `facturas` WRITE;
/*!40000 ALTER TABLE `facturas` DISABLE KEYS */;
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
  `exitoso` tinyint DEFAULT NULL,
  `fecha_generacion` datetime DEFAULT CURRENT_TIMESTAMP,
  `recomendaciones` text,
  `total_descargas` int DEFAULT '0',
  PRIMARY KEY (`id_metrica`),
  KEY `fk_modelo_idx` (`id_modelo`),
  CONSTRAINT `fk_modelo2` FOREIGN KEY (`id_modelo`) REFERENCES `modelos` (`id_modelo`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `metricas`
--

LOCK TABLES `metricas` WRITE;
/*!40000 ALTER TABLE `metricas` DISABLE KEYS */;
INSERT INTO `metricas` VALUES (15,24,97.66,NULL,1,'2026-04-29 13:05:06',NULL,0),(16,25,80.74,NULL,1,'2026-05-04 20:02:54','<li>Escala: 100%</li>\n<li>Material: PLA</li>\n<li>Relleno: 20%</li>\n<li>Soportes: Sí</li>',0),(17,27,104.21,NULL,1,'2026-05-04 20:25:38','<li>Escala: 100%</li>\n<li>Material: PLA</li>\n<li>Relleno: 20%</li>\n<li>Soportes: Sí</li>',0),(18,29,56.36,NULL,1,'2026-05-05 11:38:24','<li>Escala: 100%</li>\n<li>Material: PLA</li>\n<li>Relleno: 20%</li>\n<li>Soportes: Sí</li>',0),(19,30,103.76,NULL,1,'2026-05-05 11:48:12','<li>Escala: 100%</li>\n<li>Material: PLA</li>\n<li>Relleno: 20%</li>\n<li>Soportes: Sí</li>',0),(20,31,81.76,NULL,1,'2026-05-05 11:54:48','<li>Escala: 100%</li>\n<li>Material: PLA</li>\n<li>Relleno: 20%</li>\n<li>Soportes: Sí</li>',0),(21,33,87.68,NULL,1,'2026-05-20 12:45:02','<li><b>Orientación en la cama:</b> Coloca la pieza con la cara posterior (la superficie plana donde se apoyaría el teléfono) completamente plana sobre la cama de impresión. Esto maximiza la adhesión, reduce drásticamente la necesidad de soportes para la estructura principal y mejora la calidad de la superficie visible.</li>\n<li><b>Soportes:</b> Se necesitarán soportes arbóreos (tree supports) con una densidad del 15% para los pequeños voladizos creados por los detalles en relieve de la cara frontal y para el pequeño labio inferior que sujeta el teléfono. Los soportes arbóreos son ideales para estas geometrías complejas y facilitan la remoción.</li>\n<li><b>Material:</b> PETG es el filamento más adecuado. Ofrece una buena resistencia mecánica y durabilidad para un soporte funcional, además de una resistencia moderada al calor que puede generarse al cargar un teléfono, superando al PLA en este aspecto.</li>\n<li><b>Altura de capa:</b> Se recomienda una altura de capa de 0.15 mm. Esto permitirá capturar con precisión los detalles finos y las líneas intrincadas del diseño cyberpunk en la superficie frontal, logrando un acabado estético de alta calidad.</li>\n<li><b>Grosor de pared (Perímetros / Wall loops):</b> Utiliza 3 perímetros (aproximadamente 1.2 mm de grosor) para asegurar una estructura robusta que soporte el peso del teléfono y para que los detalles superficiales tengan suficiente material para definirse bien sin que el relleno interfiera.</li>\n<li><b>Relleno (Infill):</b> Un relleno del 25% con patrón Gyroid proporcionará una buena resistencia estructural y estabilidad para el soporte, sin añadir un peso excesivo ni consumir demasiado material. El patrón Gyroid ofrece resistencia isotrópica, ideal para una pieza funcional.</li>\n<li><b>Velocidad de impresión:</b> Imprime a una velocidad de 50 mm/s para la mayoría de la pieza, pero reduce la velocidad de los perímetros exteriores a 30-40 mm/s. Esto ayudará a que los detalles finos y las texturas del diseño cyberpunk se definan con mayor nitidez y precisión.</li>',1),(22,34,82.78,NULL,1,'2026-05-20 12:52:15','<li><b>Orientación en la cama:</b> Colocar la pieza con la base plana directamente sobre la cama de impresión. Esto maximiza la superficie de contacto para una excelente adhesión y minimiza la necesidad de soportes para la estructura principal de la base, construyendo la parte vertical del soporte hacia arriba.</li>\n<li><b>Soportes:</b> Sí, se necesitarán. Se recomienda usar soportes arbóreos (tree supports) con una densidad del 15-20%. Aplicarlos principalmente debajo de las rejillas de la base, en los voladizos de la parte trasera del soporte vertical (donde se apoya el teléfono) y en cualquier detalle sobresaliente con ángulos superiores a 45 grados para asegurar la fidelidad de la geometría.</li>\n<li><b>Material:</b> PLA. Es la opción más adecuada para este soporte de teléfono, ya que permite una excelente reproducción de los detalles finos del diseño cyberpunk, es fácil de imprimir y ofrece la rigidez necesaria para un uso estático.</li>',0),(23,35,90.72,NULL,1,'2026-05-20 12:56:08','<li><b>Orientación en la cama:</b> Colocar la figura directamente sobre su base circular. Esta orientación proporciona la máxima superficie de contacto con la cama, asegurando una excelente adhesión y estabilidad durante toda la impresión, además de minimizar los soportes en la parte inferior de la base.</li>\n<li><b>Soportes:</b> Se necesitan soportes arbóreos (tree supports) en las zonas de voladizo pronunciado. Aplicarlos bajo los cuernos, la barba, los colmillos, la parte inferior de los hombros, los codos y las garras de los pies. Una densidad del 15% será suficiente para proporcionar estabilidad sin ser excesivamente difíciles de retirar, dada la complejidad de los detalles.</li>\n<li><b>Material:</b> PLA es el filamento más adecuado para esta figura. Dada su naturaleza decorativa y el alto nivel de detalle, el PLA ofrecerá la mejor calidad de superficie, facilidad de impresión y una buena reproducción de las texturas finas sin los desafíos de materiales más técnicos.</li>\n<li><b>Altura de capa:</b> Se recomienda una altura de capa de 0.12 mm. Este valor permitirá capturar con precisión los finos detalles de la armadura, el rostro, la barba y los cuernos, resultando en una superficie suave y una alta fidelidad al modelo original, aunque aumentará el tiempo de impresión.</li>\n<li><b>Grosor de pared (Perímetros):</b> Utilizar 3 perímetros (aproximadamente 1.2 mm de grosor). Esto proporcionará una estructura lo suficientemente robusta para una pieza decorativa sin añadir peso o tiempo de impresión innecesario, y ayudará a definir los detalles externos.</li>\n<li><b>Relleno (Infill):</b> Un porcentaje de relleno del 15% con un patrón cúbico (Cubic) es suficiente. Al ser una pieza principalmente decorativa, no requiere alta resistencia mecánica, y este relleno proporcionará una estructura interna adecuada sin consumir demasiado material ni aumentar excesivamente el tiempo de impresión.</li>\n<li><b>Velocidad de impresión:</b> Establecer una velocidad de impresión general de 40 mm/s. Para los perímetros exteriores (outer walls) y las zonas con voladizos o detalles finos (como la barba y los cuernos), reducir la velocidad a 25 mm/s para asegurar la máxima precisión y evitar defectos.</li>',0),(24,36,157.35,NULL,1,'2026-05-20 13:02:09','<li><b>Orientación en la cama:</b> Colocar la pieza con su base ancha y plana directamente sobre la cama de impresión. Esta es la orientación más estable, maximiza la adhesión y minimiza la necesidad de soportes al construir la estructura principal desde abajo.</li>\n<li><b>Soportes:</b> Se necesitarán soportes para los arcos de las ventanas y la puerta, así como para las almenas de la parte superior de ambas secciones de la torre. Se recomienda usar soportes arbóreos (tree supports) con una densidad del 15-20% para facilitar su remoción y minimizar marcas en las superficies visibles, especialmente en los intrincados arcos.</li>\n<li><b>Material:</b> PLA es el filamento más adecuado para este modelo. Dada su función probable como portalápices de escritorio, el PLA ofrece un buen equilibrio entre facilidad de impresión, detalle estético para los ladrillos y grietas, y suficiente resistencia para un uso estático en interiores.</li>\n<li><b>Altura de capa:</b> Se recomienda una altura de capa de 0.20 mm. Esto permitirá capturar adecuadamente los detalles de los ladrillos, las texturas de las \"ruinas\" y la curvatura de los arcos, mientras se mantiene un tiempo de impresión razonable para una pieza de este tamaño.</li>\n<li><b>Grosor de pared (Perímetros / Wall loops):</b> Utilizar 3 perímetros (aproximadamente 1.2 mm de grosor de pared). Esto proporcionará una estructura robusta para un portalápices, asegurando que las paredes sean lo suficientemente fuertes para el uso diario y para soportar los detalles de los ladrillos sin ser frágiles.</li>\n<li><b>Relleno (Infill):</b> Un porcentaje de relleno del 15% con un patrón cúbico (Cubic) o giroidal (Gyroid) será suficiente. Esto aportará estabilidad interna y resistencia a la pieza sin añadir un peso o consumo de material excesivo, adecuado para un objeto de escritorio.</li>\n<li><b>Velocidad de impresión:</b> Una velocidad general de 50 mm/s es apropiada. Sin embargo, para los perímetros exteriores y las zonas con detalles finos como los ladrillos y las grietas, se recomienda reducir la velocidad a 30-35 mm/s para mejorar la calidad superficial y la definición de los detalles.</li>',0),(25,37,114.24,NULL,1,'2026-05-20 13:10:30','<li><b>Orientación en la Cama:</b> Imprimir la pieza en su orientación natural, con la base plana hacia la cama de impresión. Esto maximiza la adhesión a la cama y minimiza la necesidad de soportes para la estructura principal, aprovechando la gran superficie de contacto.</li>\n<li><b>Soportes:</b> Se necesitan soportes. Se recomienda utilizar soportes arbóreos (tree supports) con una densidad del 15-20% y un ángulo de voladizo de 45-50 grados. Deben aplicarse específicamente dentro del arco de la entrada principal, en las aberturas de las ventanas (incluyendo la forma de trébol) y bajo los salientes de las almenas en la parte superior de la torre.</li>\n<li><b>Material:</b> PLA. Es el material más adecuado para este modelo decorativo y funcional (portalápices). Ofrece una excelente reproducción de detalles finos como la textura de ladrillo y las grietas, es fácil de imprimir y está disponible en una amplia gama de colores.</li>\n<li><b>Altura de Capa:</b> 0.15 mm. Esta altura de capa permitirá capturar eficazmente los detalles finos de la textura de ladrillo, las grietas y las formas intrincadas de las ventanas, logrando un buen equilibrio entre calidad visual y tiempo de impresión para un objeto de este tamaño y detalle.</li>\n<li><b>Grosor de Pared (Perímetros / Wall loops):</b> 3 perímetros (aproximadamente 1.2 mm con una boquilla de 0.4 mm). Esto proporcionará una estructura lo suficientemente robusta para un portalápices de escritorio, que soportará el uso diario sin ser excesivamente frágil, y ayudará a definir bien la textura exterior.</li>',0),(26,38,167.83,NULL,1,'2026-05-26 22:28:35','<li><b>Orientación en la cama:</b> Coloca la base del joyero directamente sobre la cama de impresión, apoyado en sus patas. Esta orientación proporciona la máxima superficie de contacto para una buena adhesión y minimiza la necesidad de soportes en la parte inferior visible de la pieza, que es la más ornamental.</li>\n<li><b>Soportes:</b> Son absolutamente necesarios debido a la complejidad de los voladizos. Se recomiendan soportes arbóreos (tree supports) con una densidad del 15-20%. Aplícalos bajo la moldura superior de la tapa (especialmente en la concha y los adornos laterales), bajo la cuerda decorativa que rodea el cuerpo del joyero, y bajo las curvas de las patas para asegurar una impresión limpia de estos detalles.</li>\n<li><b>Material:</b> PLA es el filamento más adecuado. Dada la naturaleza decorativa de la pieza y la abundancia de detalles finos, el PLA ofrece la mejor capacidad para reproducir estas características con alta fidelidad y un acabado estético, además de ser fácil de imprimir.</li>\n<li><b>Altura de capa:</b> Utiliza una altura de capa de 0.10-0.15 mm. Este valor es crucial para capturar la intrincada textura de la cuerda, los detalles de las hojas, la concha y los ornamentos de las patas, garantizando la máxima calidad superficial y la definición de los detalles finos.</li>\n<li><b>Grosor de pared (Perímetros / Wall loops):</b> Configura 3-4 perímetros (aproximadamente 1.2-1.6 mm). Esto proporcionará una estructura lo suficientemente robusta para una caja de joyería de uso decorativo sin aumentar excesivamente el tiempo de impresión o el consumo de material, y ayudará a definir las paredes internas y externas.</li>',0);
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
  `meshy_task_id` varchar(255) DEFAULT NULL,
  `feedback_ia` int DEFAULT '0',
  PRIMARY KEY (`id_modelo`),
  KEY `fk_usuario2_idx` (`id_usuario`),
  CONSTRAINT `fk_usuario2` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=39 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `modelos`
--

LOCK TABLES `modelos` WRITE;
/*!40000 ALTER TABLE `modelos` DISABLE KEYS */;
INSERT INTO `modelos` VALUES (16,2,'soporte para celular','Modelo basado en: soporte para celular...','modelo_16_019dd535.stl','thumb_16_019dd535.png',1,'2026-04-28 17:49:34','2026-04-28 18:15:37',9,3,3,NULL,0),(17,1,'auto con forma de calabaza \r\n','Modelo basado en: auto con forma de ca...','modelo_17_019dd53c.stl','thumb_17_019dd53c.png',1,'2026-04-28 17:56:27','2026-04-28 21:24:57',9,3,3,NULL,0),(18,1,'Bajo fender (Instrumento)','Modelo basado en: Bajo fender (Instrum...','modelo_18_019dd552.stl','thumb_18_019dd552.png',0,'2026-04-28 18:21:09','2026-04-28 18:22:14',9,3,3,NULL,0),(19,1,'Guitarra stratocaster ','Modelo basado en: Guitarra stratocaste...','modelo_19_019dd555.stl','thumb_19_019dd555.png',0,'2026-04-28 18:23:45','2026-04-28 18:25:07',9,3,3,NULL,0),(20,1,'Maceta con forma de corazon','Maceta con forma de corazon','modelo_20_019dd5f9.stl','thumb_20_019dd5f9.png',0,'2026-04-28 21:23:07','2026-04-28 21:25:15',9,3,3,NULL,0),(21,1,'peon ajedrez','Peon ajedrez','modelo_21_019dd5fc.stl','thumb_21_019dd5fc.png',0,'2026-04-28 21:26:12','2026-04-28 21:28:15',9,3,3,NULL,0),(22,1,'A Pawn of Chess','A pawn of chess','modelo_22_019dd602.stl','thumb_22_019dd602.png',0,'2026-04-28 21:33:14','2026-04-28 21:34:30',9,3,3,NULL,0),(23,1,'A car with a flower up a roof','A car with a flower up a roof','modelo_23_019dd60a.stl','thumb_23_019dd60a.png',0,'2026-04-28 21:42:09','2026-04-28 21:44:12',9,3,3,NULL,0),(24,2,'Un gato sentado sobre sus patas traseras','Un gato sentado sobre sus patas traseras','modelo_24_019dd957.stl','thumb_24_019dd957.png',1,'2026-04-29 13:05:06','2026-04-29 17:28:52',9,3,3,NULL,0),(25,1,'Un perro sentado ','Un perro sentado ','modelo_25_019df495.stl','thumb_25_019df495.png',0,'2026-05-04 20:02:54','2026-05-04 20:04:15',9,3,3,'019df495-f8f1-753c-927e-bdd3558373ce',0),(26,1,'Un perro sentado con un hueso en la boca','Un perro sentado  (Editado)','modelo_26_019df497.stl','thumb_26_019df497.png',0,'2026-05-04 20:04:45','2026-05-04 20:07:33',9,3,3,'019df497-b675-7367-a32c-9fbf666c5aec',0),(27,1,'hombre sentado\r\n','Hombre sentado\r\n','modelo_27_019df4aa.stl','thumb_27_019df4aa.png',0,'2026-05-04 20:25:38','2026-05-04 20:27:22',9,3,3,'019df4aa-cd3c-7778-add9-8bdf3f1307cb',0),(28,1,'hombre sentado tomando cafe\r\n','Hombre sentado\r\n (Editado)','modelo_28_019df4b2.stl','thumb_28_019df4b2.png',0,'2026-05-04 20:34:00','2026-05-04 20:35:43',9,3,3,'019df4b2-7c83-7ce1-8de3-eddf8667d7e1',0),(29,1,'llavero con forma de corazón, superficie plana, sin partes sueltas','Llavero con forma de corazón, ','modelo_29_019df7ee.stl','thumb_29_019df7ee.png',0,'2026-05-05 11:38:24','2026-05-05 11:39:20',9,3,3,'019df7ee-712c-799e-8ea5-7907bee11fd5',0),(30,1,'porta lapiceros con forma de calavera, base plana','Porta lapiceros con forma de c','modelo_30_019df7f7.stl','thumb_30_019df7f7.png',0,'2026-05-05 11:48:12','2026-05-05 11:49:56',9,3,3,'019df7f7-6773-7cc7-9880-e2fcc7e815c7',0),(31,1,'Perro sentado sobre sus patas traseras en el suelo, con un hueso en la boca','Perro sentado sobre sus patas ','modelo_31_019df7fd.stl','thumb_31_019df7fd.png',0,'2026-05-05 11:54:48','2026-05-06 19:09:13',9,3,3,'019df7fd-74ce-7eaa-b555-1f7bdb1c2c6d',-1),(33,1,'Un soporte para el teléfono móvil con diseño cyberpunk','Un soporte para el teléfono móvil con diseño cyberpunk','modelo_33_019e456b.stl','thumb_33_019e456b.png',0,'2026-05-20 12:45:02','2026-05-20 12:46:30',9,3,3,'019e456b-04af-7e85-935b-49a7d50d62f3',0),(34,1,'Un soporte para el teléfono móvil con diseño cyberpunk','Un soporte para el teléfono móvil con diseño cyberpunk','modelo_34_019e4571.stl','thumb_34_019e4571.png',0,'2026-05-20 12:52:15','2026-05-20 12:53:38',9,3,3,'019e4571-9e25-7044-9cf6-177f4910df4d',0),(35,1,'Un guerrero orco con una armadura pesada','Un guerrero orco con una armadura pesada','modelo_35_019e4575.stl','thumb_35_019e4575.png',0,'2026-05-20 12:56:08','2026-05-20 12:57:39',9,3,3,'019e4575-2964-70f5-9854-a36da4f7c812',0),(36,1,'Un portalápices de escritorio con forma de torre de un castillo medieval en ruinas.','Un portalápices de escritorio con forma de torre de un castillo medieval en ruinas.','modelo_36_019e457a.stl','thumb_36_019e457a.png',0,'2026-05-20 13:02:09','2026-05-20 13:04:46',9,3,3,'019e457a-ab42-71b6-9e6d-6ef766344787',0),(37,1,'Un portalápices de escritorio con forma de torre de un castillo medieval en ruinas','Un portalápices de escritorio con forma de torre de un castillo medieval en ruinas','modelo_37_019e4582.stl','thumb_37_019e4582.png',0,'2026-05-20 13:10:30','2026-05-20 13:12:24',9,3,3,'019e4582-4fc9-7d27-8311-9cae64366100',0),(38,1,'Joyero de una sola pieza, de tamaño mediano, con forma de caja','Joyero','modelo_38_019e6667.stl','thumb_38_019e6667.png',0,'2026-05-26 22:28:35','2026-05-26 22:31:23',9,3,3,'019e6667-6a86-7776-9177-ea53d82d1a2c',0);
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
INSERT INTO `suscripciones` VALUES (1,1,1,'2026-04-20','2026-05-20','Activa','Tarjeta',7),(3,1,7,'2026-06-01','2026-07-01','Activa','Pasarela Ficticia',15);
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
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES (1,'santiauat@hotmail.com','scrypt:32768:8:1$AMncDim1Y1W94ZDr$d4bc196cc86945d638dd233a04c4715f42e5db519381d07b14d191c79095d023c4a0925155dcf3e3f52b81d2d5c83929c293cf13b60589a7d478d552ce002f63','santiauat','2026-04-20 23:21:20',1,'user_1_3cdbe997.jpg',1),(2,'jperz@gmail.com','scrypt:32768:8:1$Yvc00wgnDBKaRLNn$9f7232fe86e3ed9032b7cca49ba731b8dfb454122c8e716c046dc35fa1b4cda7a19bff152468ba98b4d0542ff607c5fe68aa72e2ab734a1b990e544934d259b0','JuanPerez','2026-04-20 23:46:49',0,'user_2_d29d44f2.jpg',1),(3,'ricardodarin@gmail.com','scrypt:32768:8:1$3Ru7A0GS96tat7Ez$e8bba12a0683d261fd6d2f46a502bf12f0dc6f41a094252bb78d3415e1f0fa850372e0d888c680ee5043532c2536f5b5580cd06ed2c5a580752637b60e413d27','ricdarin','2026-04-22 00:22:29',0,NULL,1),(4,'test@example.com','scrypt:32768:8:1$ROJA40JIHA92UgKW$169720327bdc0e5e4f546139e362781b6f9479fbbfc78099b1b6cbdeb7b64c82aaee8f0861d243b19d0bc0e6eae31190016b790f35efd817c9acefb62d1087cb','testuser','2026-04-22 21:53:43',0,NULL,0),(5,'francisbrunis@hotmail.com','scrypt:32768:8:1$4fjDBJeTqAJOBQ34$c30093db8ce6888e41fb62419ec88061ef7d3a7caef2b7f321511a4272a9ecf40d884db0b173fad323f05a7f7e5b673b0dd4ffc85718c1cd2e79e6190b2bde41','FranciscoBruno','2026-05-20 12:49:26',1,NULL,1),(6,'tomiyi@gmail.com','scrypt:32768:8:1$WTSDZbYiPHSKEs8X$571fe688469993e3fe26b127b2b2f5c8f73fc17debabb523c2f52141252fca48ab934bd4d77e41251ea73b92ed296854d3934f084b75a9820e439bcc49a4ecc6','Tomasigli','2026-05-26 21:46:27',0,NULL,1),(7,'victor@gmail.com','scrypt:32768:8:1$xxlJt9ALdH7Vin7L$06ce5cc3d8bbb9b9e8cc4683cf92ebf73677700be6fd3d8215239237afc018a8c4a85c973971faaa19fa18663d2aa1348c3ec40a4f90e07a2ff7a635695b32ab','VicPerez','2026-05-27 21:42:07',0,NULL,1),(8,'prueba@gmail.com','scrypt:32768:8:1$qyb2PYvfH655u83w$b7b5b52ac3715be3ff6dff04ac83fc07d99ae1c5765b95747c5cf09f6b1e86a1f40d6414e1fb8faf53510f611d30d4a4f9817a2e7947f93f403278d005a4885a','pruebatest','2026-05-28 18:49:40',0,NULL,1);
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
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `valoraciones`
--

LOCK TABLES `valoraciones` WRITE;
/*!40000 ALTER TABLE `valoraciones` DISABLE KEYS */;
INSERT INTO `valoraciones` VALUES (1,24,1,5,'Se parece a mi gato!','2026-05-05 21:05:56'),(2,17,1,1,'No se imprime muy bien','2026-05-05 21:12:06');
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

-- Dump completed on 2026-06-18 18:42:15
