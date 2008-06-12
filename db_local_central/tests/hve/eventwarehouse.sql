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
-- Table structure for table `calculateddata`
--

DROP TABLE IF EXISTS `calculateddata`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `calculateddata` (
  `calculateddatatype_id` int(10) unsigned NOT NULL,
  `event_id` bigint(20) NOT NULL,
  `integervalue` int(10) unsigned default NULL,
  `doublevalue` double default NULL,
  PRIMARY KEY  (`calculateddatatype_id`,`event_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `calculateddata`
--

LOCK TABLES `calculateddata` WRITE;
/*!40000 ALTER TABLE `calculateddata` DISABLE KEYS */;
/*!40000 ALTER TABLE `calculateddata` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `calculateddatatype`
--

DROP TABLE IF EXISTS `calculateddatatype`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `calculateddatatype` (
  `calculateddatatype_id` int(10) unsigned NOT NULL auto_increment,
  `eventtype_id` int(10) unsigned NOT NULL,
  `valuetype_id` int(10) unsigned default NULL,
  `description` varchar(40) default NULL,
  `uploadcode` varchar(3) default NULL,
  `public` tinyint(1) unsigned NOT NULL default '0',
  PRIMARY KEY  (`calculateddatatype_id`),
  UNIQUE KEY `i_eventtype_id` (`eventtype_id`,`uploadcode`)
) ENGINE=MyISAM AUTO_INCREMENT=17 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `calculateddatatype`
--

LOCK TABLES `calculateddatatype` WRITE;
/*!40000 ALTER TABLE `calculateddatatype` DISABLE KEYS */;
INSERT INTO `calculateddatatype` VALUES (1,1,3,'Raw pulse height scintillator 1','PH1',0),(2,1,3,'Raw pulse height scintillator 2','PH2',0),(3,1,3,'Raw pulse height scintillator 3','PH3',0),(4,1,3,'Raw pulse height scintillator 4','PH4',0),(5,1,3,'Raw integral scintillator 1','IN1',0),(6,1,3,'Raw integral scintillator 2','IN2',0),(7,1,3,'Raw integral scintillator 3','IN3',0),(8,1,3,'Raw integral scintillator 4','IN4',0),(9,1,3,'Raw baseline scintillator 1','BL1',0),(10,1,3,'Raw baseline scintillator 2','BL2',0),(11,1,3,'Raw baseline scintillator 3','BL3',0),(12,1,3,'Raw baseline scintillator 4','BL4',0),(13,1,1,'Raw number of peaks scintillator 1','NP1',0),(14,1,1,'Raw number of peaks scintillator 2','NP2',0),(15,1,1,'Raw number of peaks scintillator 3','NP3',0),(16,1,1,'Raw number of peaks scintillator 4','NP4',0);
/*!40000 ALTER TABLE `calculateddatatype` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `errorlog`
--

DROP TABLE IF EXISTS `errorlog`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `errorlog` (
  `errorlog_id` int(10) unsigned NOT NULL auto_increment,
  `date` date NOT NULL,
  `time` time NOT NULL,
  `message` text,
  PRIMARY KEY  (`errorlog_id`,`date`,`time`),
  KEY `i_date` (`date`,`time`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `errorlog`
--

LOCK TABLES `errorlog` WRITE;
/*!40000 ALTER TABLE `errorlog` DISABLE KEYS */;
/*!40000 ALTER TABLE `errorlog` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `event`
--

DROP TABLE IF EXISTS `event`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `event` (
  `event_id` bigint(20) NOT NULL auto_increment,
  `sensor_id` int(10) unsigned NOT NULL,
  `eventtype_id` int(10) unsigned NOT NULL,
  `date` date default NULL,
  `time` time default NULL,
  `nanoseconds` int(10) unsigned default NULL,
  PRIMARY KEY  (`event_id`),
  KEY `i_sensor_id` (`sensor_id`,`eventtype_id`,`date`,`time`,`nanoseconds`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `event`
--

LOCK TABLES `event` WRITE;
/*!40000 ALTER TABLE `event` DISABLE KEYS */;
/*!40000 ALTER TABLE `event` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=MyISAM AUTO_INCREMENT=34 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `eventdatatype`
--

LOCK TABLES `eventdatatype` WRITE;
/*!40000 ALTER TABLE `eventdatatype` DISABLE KEYS */;
INSERT INTO `eventdatatype` VALUES (1,1,1,'Software version','SVR',0),(2,1,1,'GPS event number','GEN',0),(3,1,1,'ADC settings event number','AEN',0),(4,1,1,'GPS status','GST',0),(5,1,1,'Software dead time','SDT',0),(6,1,5,'Trace 1','TR1',0),(7,1,5,'Trace 2','TR2',0),(8,1,5,'Trace 3','TR3',0),(9,1,5,'Trace 4','TR4',0),(10,1,1,'GPS readout delay','GRD',0),(11,2,1,'Software version','SVR',0),(12,2,1,'ADC count minimum 1','AI1',0),(13,2,1,'ADC count maximum 1','AA1',0),(14,2,1,'ADC count zero voltage 1','AZ1',0),(15,2,3,'ADC voltage per count 1','AV1',0),(20,2,3,'Time minimum 1','TI1',0),(21,2,3,'Time maximum 1','TA1',0),(22,2,1,'Number of samples 1','NS1',0),(16,2,1,'ADC count minimum 2','AI2',0),(17,2,1,'ADC count maximum 2','AA2',0),(18,2,1,'ADC count zero voltage 2','AZ2',0),(19,2,3,'ADC voltage per count 2','AV2',0),(23,2,3,'Time minimum 2','TI2',0),(24,2,3,'Time maximum 2','TA2',0),(25,2,1,'Number of samples 2','NS2',0),(26,3,1,'Software version','SVR',0),(27,3,3,'GPS latitude','GLA',0),(28,3,3,'GPS longitude','GLO',0),(29,3,3,'GPS height','GHE',0),(30,3,1,'GPS status','GST',0),(31,3,1,'GPS event number','GEN',0),(32,3,4,'Satellite numbers','SNU',0),(33,3,5,'Satellite strengths','SST',0);
/*!40000 ALTER TABLE `eventdatatype` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eventgroup`
--

DROP TABLE IF EXISTS `eventgroup`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `eventgroup` (
  `masterevent_id` bigint(20) NOT NULL,
  `event_id` bigint(20) default NULL,
  PRIMARY KEY  (`masterevent_id`),
  KEY `i_event_id` (`event_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `eventgroup`
--

LOCK TABLES `eventgroup` WRITE;
/*!40000 ALTER TABLE `eventgroup` DISABLE KEYS */;
/*!40000 ALTER TABLE `eventgroup` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eventtype`
--

DROP TABLE IF EXISTS `eventtype`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `eventtype` (
  `eventtype_id` int(10) unsigned NOT NULL auto_increment,
  `description` varchar(40) default NULL,
  `masterevent` tinyint(1) unsigned default NULL,
  `uploadcode` varchar(3) default NULL,
  PRIMARY KEY  (`eventtype_id`),
  UNIQUE KEY `i_uploadcode` (`uploadcode`)
) ENGINE=MyISAM AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `eventtype`
--

LOCK TABLES `eventtype` WRITE;
/*!40000 ALTER TABLE `eventtype` DISABLE KEYS */;
INSERT INTO `eventtype` VALUES (1,'HiSPARC coincidence',NULL,'CIC'),(2,'HiSPARC ADC settings',NULL,'ADC'),(3,'HiSPARC GPS',NULL,'GPS');
/*!40000 ALTER TABLE `eventtype` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `valuetype`
--

DROP TABLE IF EXISTS `valuetype`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `valuetype` (
  `valuetype_id` int(10) unsigned NOT NULL auto_increment,
  `valuefield` varchar(15) NOT NULL,
  `description` varchar(40) default NULL,
  PRIMARY KEY  (`valuetype_id`)
) ENGINE=MyISAM AUTO_INCREMENT=7 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `valuetype`
--

LOCK TABLES `valuetype` WRITE;
/*!40000 ALTER TABLE `valuetype` DISABLE KEYS */;
INSERT INTO `valuetype` VALUES (1,'integervalue','MySQL integer'),(2,'bigintvalue','MySQL big integer'),(3,'doublevalue','MySQL double'),(4,'textvalue','MySQL text'),(5,'blobvalue','MySQL compressed text'),(6,'datevalue','MySQL date');
/*!40000 ALTER TABLE `valuetype` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2008-06-03 20:31:29
