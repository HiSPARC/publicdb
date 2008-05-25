-- MySQL dump 10.11
--
-- Host: localhost    Database: eventwarehouse
-- ------------------------------------------------------
-- Server version	5.0.51a-3ubuntu5.1

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
-- Table structure for table `eventdata`
--

DROP TABLE IF EXISTS `eventdata`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `eventdata` (
  `eventdatatype_id` int(10) unsigned NOT NULL,
  `event_id` bigint(20) NOT NULL,
  `integervalue` int(10) unsigned default NULL,
  `doublevalue` double default NULL,
  `textvalue` text,
  `blobvalue` blob,
  PRIMARY KEY  (`eventdatatype_id`,`event_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `eventdata`
--

LOCK TABLES `eventdata` WRITE;
/*!40000 ALTER TABLE `eventdata` DISABLE KEYS */;
/*!40000 ALTER TABLE `eventdata` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eventdatatype`
--

DROP TABLE IF EXISTS `eventdatatype`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `eventdatatype` (
  `eventdatatype_id` int(10) unsigned NOT NULL auto_increment,
  `eventtype_id` int(10) unsigned NOT NULL,
  `valuetype_id` int(10) unsigned NOT NULL,
  `description` varchar(40) default NULL,
  `uploadcode` varchar(3) default NULL,
  `public` tinyint(1) unsigned NOT NULL default '0',
  PRIMARY KEY  (`eventdatatype_id`),
  UNIQUE KEY `i_eventtype_id` (`eventtype_id`,`uploadcode`)
) ENGINE=MyISAM AUTO_INCREMENT=35 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `eventdatatype`
--

LOCK TABLES `eventdatatype` WRITE;
/*!40000 ALTER TABLE `eventdatatype` DISABLE KEYS */;
INSERT INTO `eventdatatype` VALUES (1,1,1,'Software version','SVR',1),(2,1,1,'GPS event number','GEN',1),(3,1,1,'ADC settings event number','AEN',1),(4,1,1,'GPS status','GST',1),(5,1,1,'Software dead time','SDT',1),(6,1,5,'Trace 1','TR1',1),(7,1,5,'Trace 2','TR2',1),(8,1,5,'Trace 3','TR3',1),(9,1,5,'Trace 4','TR4',1),(10,1,1,'GPS readout delay','GRD',1),(11,2,1,'Software version','SVR',1),(12,2,1,'ADC count minimum 1','AI1',1),(13,2,1,'ADC count maximum 1','AA1',1),(14,2,1,'ADC count zero voltage 1','AZ1',1),(15,2,3,'ADC voltage per count 1','AV1',1),(20,2,3,'Time minimum 1','TI1',1),(21,2,3,'Time maximum 1','TA1',1),(22,2,1,'Number of samples 1','NS1',1),(16,2,1,'ADC count minimum 2','AI2',1),(17,2,1,'ADC count maximum 2','AA2',1),(18,2,1,'ADC count zero voltage 2','AZ2',1),(19,2,3,'ADC voltage per count 2','AV2',1),(23,2,3,'Time minimum 2','TI2',1),(24,2,3,'Time maximum 2','TA2',1),(25,2,1,'Number of samples 2','NS2',1),(26,3,1,'Software version','SVR',1),(27,3,3,'GPS latitude','GLA',1),(28,3,3,'GPS longitude','GLO',1),(29,3,3,'GPS height','GHE',1),(30,3,1,'GPS status','GST',1),(31,3,1,'GPS event number','GEN',1),(32,3,4,'Satellite numbers','SNU',1),(33,3,5,'Satellite strengths','SST',1),(34,1,5,'BLOB','BLB',1);
/*!40000 ALTER TABLE `eventdatatype` ENABLE KEYS */;
UNLOCK TABLES;

/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2008-05-23 13:52:41
