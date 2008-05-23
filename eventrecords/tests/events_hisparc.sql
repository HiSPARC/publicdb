DROP TABLE IF EXISTS `events_hisparc`;
CREATE TABLE `events_hisparc` (
  `event_id` bigint(20) unsigned NOT NULL auto_increment,
  `gpsevent_id` bigint(20) unsigned NOT NULL,
  `adcevent_id` bigint(20) unsigned NOT NULL,
  `softwaredeadtime` double NOT NULL,
  `gpsreadoutdelay` double NOT NULL,
  `trace1` blob,
  `trace2` blob,
  PRIMARY KEY  (`event_id`)
);
