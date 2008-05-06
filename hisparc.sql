-- MySQL dump 10.11
--
-- Host: localhost    Database: hisparc
-- ------------------------------------------------------
-- Server version	5.0.51a-3ubuntu5

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `cluster`
--

DROP TABLE IF EXISTS `cluster`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `cluster` (
  `cluster_id` int(10) unsigned NOT NULL auto_increment,
  `name` text NOT NULL,
  `contact_id` int(10) unsigned default NULL,
  `url` text,
  PRIMARY KEY  (`cluster_id`),
  UNIQUE KEY `name` (`name`(72)),
  KEY `clustercontact` (`contact_id`),
  CONSTRAINT `clustercontact` FOREIGN KEY (`contact_id`) REFERENCES `contact` (`contact_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `cluster`
--

LOCK TABLES `cluster` WRITE;
/*!40000 ALTER TABLE `cluster` DISABLE KEYS */;
/*!40000 ALTER TABLE `cluster` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `contact`
--

DROP TABLE IF EXISTS `contact`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `contact` (
  `contact_id` int(10) unsigned NOT NULL auto_increment,
  `location_id` int(10) unsigned default NULL,
  `contactposition_id` int(10) unsigned default NULL,
  `title` text,
  `firstname` text NOT NULL,
  `prefix` text,
  `lastname` text NOT NULL,
  `url` text,
  `email` text,
  `phone_work` text,
  `phone_home` text,
  PRIMARY KEY  (`contact_id`),
  UNIQUE KEY `name` (`firstname`(72),`prefix`(72),`lastname`(72)),
  KEY `contactlocation` (`location_id`),
  KEY `contactposition` (`contactposition_id`),
  CONSTRAINT `contactlocation` FOREIGN KEY (`location_id`) REFERENCES `location` (`location_id`),
  CONSTRAINT `contactposition` FOREIGN KEY (`contactposition_id`) REFERENCES `contactposition` (`contactposition_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `contact`
--

LOCK TABLES `contact` WRITE;
/*!40000 ALTER TABLE `contact` DISABLE KEYS */;
/*!40000 ALTER TABLE `contact` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `contactposition`
--

DROP TABLE IF EXISTS `contactposition`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `contactposition` (
  `contactposition_id` int(10) unsigned NOT NULL auto_increment,
  `description` text NOT NULL,
  PRIMARY KEY  (`contactposition_id`),
  UNIQUE KEY `description` (`description`(72))
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `contactposition`
--

LOCK TABLES `contactposition` WRITE;
/*!40000 ALTER TABLE `contactposition` DISABLE KEYS */;
INSERT INTO `contactposition` VALUES (1,'Docent'),(2,'Student'),(3,'Leerling'),(4,'Contactpersoon lokatie'),(5,'Webmaster'),(6,'Projectleider'),(7,'PhD Student'),(8,'Post doc'),(9,'Cluster coordinator'),(10,'Technische ondersteuning'),(11,'Onderwijskundige ondersteuning');
/*!40000 ALTER TABLE `contactposition` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `det_hisparc`
--

DROP TABLE IF EXISTS `det_hisparc`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `det_hisparc` (
  `detector_id` int(10) unsigned NOT NULL auto_increment,
  `station_id` int(10) unsigned NOT NULL,
  `status_id` int(10) unsigned NOT NULL,
  `startdate` date NOT NULL,
  `enddate` date default NULL,
  `latitude` double default NULL,
  `longitude` double default NULL,
  `height` double default NULL,
  `direction` double default NULL,
  `translation` point default NULL,
  `scintillators` multipoint default NULL,
  `password` text,
  PRIMARY KEY  USING BTREE (`detector_id`),
  KEY `hisparcstation` (`station_id`),
  KEY `hisparcstatus` (`status_id`),
  CONSTRAINT `hisparcstation` FOREIGN KEY (`station_id`) REFERENCES `station` (`station_id`),
  CONSTRAINT `hisparcstatus` FOREIGN KEY (`status_id`) REFERENCES `det_status` (`status_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `det_hisparc`
--

LOCK TABLES `det_hisparc` WRITE;
/*!40000 ALTER TABLE `det_hisparc` DISABLE KEYS */;
/*!40000 ALTER TABLE `det_hisparc` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `det_status`
--

DROP TABLE IF EXISTS `det_status`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `det_status` (
  `status_id` int(10) unsigned NOT NULL auto_increment,
  `description` text NOT NULL,
  PRIMARY KEY  (`status_id`),
  UNIQUE KEY `description` (`description`(72))
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `det_status`
--

LOCK TABLES `det_status` WRITE;
/*!40000 ALTER TABLE `det_status` DISABLE KEYS */;
INSERT INTO `det_status` VALUES (1,'Obsolete record'),(2,'Online'),(3,'Offline');
/*!40000 ALTER TABLE `det_status` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `location`
--

DROP TABLE IF EXISTS `location`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `location` (
  `location_id` int(10) unsigned NOT NULL auto_increment,
  `name` text NOT NULL,
  `organization_id` int(10) unsigned NOT NULL,
  `contact_id` int(10) unsigned default NULL,
  `locationstatus_id` int(10) unsigned default NULL,
  `address` text NOT NULL,
  `postalcode` text NOT NULL,
  `pobox` text,
  `pobox_postalcode` text,
  `city` text NOT NULL,
  `country` text NOT NULL,
  `phone` text,
  `fax` text,
  `url` text,
  `email` text,
  PRIMARY KEY  (`location_id`),
  UNIQUE KEY `name` (`name`(72)),
  KEY `locationcontact` (`contact_id`),
  KEY `locationorganization` (`organization_id`),
  KEY `locationstatus` (`locationstatus_id`),
  CONSTRAINT `locationcontact` FOREIGN KEY (`contact_id`) REFERENCES `contact` (`contact_id`),
  CONSTRAINT `locationorganization` FOREIGN KEY (`organization_id`) REFERENCES `organization` (`organization_id`),
  CONSTRAINT `locationstatus` FOREIGN KEY (`locationstatus_id`) REFERENCES `location_status` (`status_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `location`
--

LOCK TABLES `location` WRITE;
/*!40000 ALTER TABLE `location` DISABLE KEYS */;
/*!40000 ALTER TABLE `location` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `location_status`
--

DROP TABLE IF EXISTS `location_status`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `location_status` (
  `status_id` int(10) unsigned NOT NULL auto_increment,
  `description` text NOT NULL,
  PRIMARY KEY  (`status_id`),
  UNIQUE KEY `description` (`description`(72))
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `location_status`
--

LOCK TABLES `location_status` WRITE;
/*!40000 ALTER TABLE `location_status` DISABLE KEYS */;
INSERT INTO `location_status` VALUES (1,'Clusterkern');
/*!40000 ALTER TABLE `location_status` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `organization`
--

DROP TABLE IF EXISTS `organization`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `organization` (
  `organization_id` int(10) unsigned NOT NULL auto_increment,
  `name` text NOT NULL,
  `cluster_id` int(10) unsigned NOT NULL,
  `contact_id` int(10) unsigned default NULL,
  `url` text,
  PRIMARY KEY  (`organization_id`),
  UNIQUE KEY `name` (`name`(72)),
  KEY `organizationcluster` (`cluster_id`),
  KEY `organizationcontact` (`contact_id`),
  CONSTRAINT `organizationcluster` FOREIGN KEY (`cluster_id`) REFERENCES `cluster` (`cluster_id`),
  CONSTRAINT `organizationcontact` FOREIGN KEY (`contact_id`) REFERENCES `contact` (`contact_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `organization`
--

LOCK TABLES `organization` WRITE;
/*!40000 ALTER TABLE `organization` DISABLE KEYS */;
/*!40000 ALTER TABLE `organization` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `station`
--

DROP TABLE IF EXISTS `station`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `station` (
  `station_id` int(10) unsigned NOT NULL auto_increment,
  `location_id` int(10) unsigned NOT NULL,
  `contact_id` int(10) unsigned default NULL,
  `number` int(10) unsigned NOT NULL,
  PRIMARY KEY  (`station_id`),
  UNIQUE KEY `stationnumber` (`number`),
  KEY `stationlocation` (`location_id`),
  KEY `stationcontact` (`contact_id`),
  CONSTRAINT `stationcontact` FOREIGN KEY (`contact_id`) REFERENCES `contact` (`contact_id`),
  CONSTRAINT `stationlocation` FOREIGN KEY (`location_id`) REFERENCES `location` (`location_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=FIXED;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `station`
--

LOCK TABLES `station` WRITE;
/*!40000 ALTER TABLE `station` DISABLE KEYS */;
/*!40000 ALTER TABLE `station` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2008-05-06 13:07:33
