--
-- Dumping data for table `contactposition`
--

LOCK TABLES `inforecords_contactposition` WRITE;

INSERT INTO `inforecords_contactposition` VALUES (1,'Docent'),(2,'Student'),(3,'Leerling'),(4,'Contactpersoon lokatie'),(5,'Webmaster'),(6,'Projectleider'),(7,'PhD Student'),(8,'Post doc'),(9,'Cluster coordinator'),(10,'Technische ondersteuning'),(11,'Onderwijskundige ondersteuning');

UNLOCK TABLES;

--
-- Dumping data for table `detector_status`
--

LOCK TABLES `inforecords_detectorstatus` WRITE;

INSERT INTO `inforecords_detectorstatus` VALUES (1,'Obsolete record'),(2,'Online'),(3,'Offline');

UNLOCK TABLES;

--
-- Dumping data for table `electronics_status`
--

LOCK TABLES `inforecords_electronicsstatus` WRITE;

INSERT INTO `inforecords_electronicsstatus` VALUES (1,'Obsolete record'),(2,'Online'),(3,'Offline');

UNLOCK TABLES;

--
-- Dumping data for table `electronics_type`
--

LOCK TABLES `inforecords_electronicstype` WRITE;

INSERT INTO `inforecords_electronicstype` VALUES (1,'Nijmegen'),(2,'HiSPARC I'),(3,'HiSPARC II');

UNLOCK TABLES;

--
-- Dumping data for table `location_status`
--

LOCK TABLES `inforecords_locationstatus` WRITE;

INSERT INTO `inforecords_locationstatus` VALUES (1,'ONBEKEND'),(2,'Clusterkern');

UNLOCK TABLES;

--
-- Dumping data for table `pc_type`
--

LOCK TABLES `inforecords_pctype` WRITE;

INSERT INTO `inforecords_pctype` VALUES (1,'Detector'),(2,'Detector / Buffer Database'),(3,'Buffer Database'),(4,'Local Database'),(5,'Buffer / Local Database'),(6,'Detector / Buffer / Local database');

UNLOCK TABLES;
