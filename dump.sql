-- MySQL dump 10.13  Distrib 5.7.18, for Linux (x86_64)
--
-- Host: localhost    Database: tradenew
-- ------------------------------------------------------
-- Server version	5.7.18-0ubuntu0.16.04.1

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
-- Table structure for table `account_emailaddress`
--

DROP TABLE IF EXISTS `account_emailaddress`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `account_emailaddress` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(254) NOT NULL,
  `verified` tinyint(1) NOT NULL,
  `primary` tinyint(1) NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  KEY `account_emailaddress_user_id_2c513194_fk_auth_user_id` (`user_id`),
  CONSTRAINT `account_emailaddress_user_id_2c513194_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `account_emailaddress`
--

LOCK TABLES `account_emailaddress` WRITE;
/*!40000 ALTER TABLE `account_emailaddress` DISABLE KEYS */;
/*!40000 ALTER TABLE `account_emailaddress` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `account_emailconfirmation`
--

DROP TABLE IF EXISTS `account_emailconfirmation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `account_emailconfirmation` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created` datetime(6) NOT NULL,
  `sent` datetime(6) DEFAULT NULL,
  `key` varchar(64) NOT NULL,
  `email_address_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `key` (`key`),
  KEY `account_emailconfirm_email_address_id_5b7f8c58_fk_account_e` (`email_address_id`),
  CONSTRAINT `account_emailconfirm_email_address_id_5b7f8c58_fk_account_e` FOREIGN KEY (`email_address_id`) REFERENCES `account_emailaddress` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `account_emailconfirmation`
--

LOCK TABLES `account_emailconfirmation` WRITE;
/*!40000 ALTER TABLE `account_emailconfirmation` DISABLE KEYS */;
/*!40000 ALTER TABLE `account_emailconfirmation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(80) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=73 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can add user',2,'add_user'),(5,'Can change user',2,'change_user'),(6,'Can delete user',2,'delete_user'),(7,'Can add permission',3,'add_permission'),(8,'Can change permission',3,'change_permission'),(9,'Can delete permission',3,'delete_permission'),(10,'Can add group',4,'add_group'),(11,'Can change group',4,'change_group'),(12,'Can delete group',4,'delete_group'),(13,'Can add content type',5,'add_contenttype'),(14,'Can change content type',5,'change_contenttype'),(15,'Can delete content type',5,'delete_contenttype'),(16,'Can add session',6,'add_session'),(17,'Can change session',6,'change_session'),(18,'Can delete session',6,'delete_session'),(19,'Can add site',7,'add_site'),(20,'Can change site',7,'change_site'),(21,'Can delete site',7,'delete_site'),(22,'Can add Транзакциии кошелька',8,'add_wallethistory'),(23,'Can change Транзакциии кошелька',8,'change_wallethistory'),(24,'Can delete Транзакциии кошелька',8,'delete_wallethistory'),(25,'Can add Кошелёк пользователя',9,'add_userwallet'),(26,'Can change Кошелёк пользователя',9,'change_userwallet'),(27,'Can delete Кошелёк пользователя',9,'delete_userwallet'),(28,'Can add Баланс пользователя',10,'add_userbalance'),(29,'Can change Баланс пользователя',10,'change_userbalance'),(30,'Can delete Баланс пользователя',10,'delete_userbalance'),(31,'Can add История баланса',11,'add_userholdings'),(32,'Can change История баланса',11,'change_userholdings'),(33,'Can delete История баланса',11,'delete_userholdings'),(34,'Can add Криптовалюта',12,'add_coin'),(35,'Can change Криптовалюта',12,'change_coin'),(36,'Can delete Криптовалюта',12,'delete_coin'),(37,'Can add Биржа',13,'add_exchanges'),(38,'Can change Биржа',13,'change_exchanges'),(39,'Can delete Биржа',13,'delete_exchanges'),(40,'Can add Кошелёк',14,'add_wallets'),(41,'Can change Кошелёк',14,'change_wallets'),(42,'Can delete Кошелёк',14,'delete_wallets'),(43,'Can add Биржа пользователя',15,'add_userexchanges'),(44,'Can change Биржа пользователя',15,'change_userexchanges'),(45,'Can delete Биржа пользователя',15,'delete_userexchanges'),(46,'Can add periodic task',16,'add_periodictask'),(47,'Can change periodic task',16,'change_periodictask'),(48,'Can delete periodic task',16,'delete_periodictask'),(49,'Can add crontab',17,'add_crontabschedule'),(50,'Can change crontab',17,'change_crontabschedule'),(51,'Can delete crontab',17,'delete_crontabschedule'),(52,'Can add interval',18,'add_intervalschedule'),(53,'Can change interval',18,'change_intervalschedule'),(54,'Can delete interval',18,'delete_intervalschedule'),(55,'Can add periodic tasks',19,'add_periodictasks'),(56,'Can change periodic tasks',19,'change_periodictasks'),(57,'Can delete periodic tasks',19,'delete_periodictasks'),(58,'Can add email confirmation',20,'add_emailconfirmation'),(59,'Can change email confirmation',20,'change_emailconfirmation'),(60,'Can delete email confirmation',20,'delete_emailconfirmation'),(61,'Can add email address',21,'add_emailaddress'),(62,'Can change email address',21,'change_emailaddress'),(63,'Can delete email address',21,'delete_emailaddress'),(64,'Can add social application',22,'add_socialapp'),(65,'Can change social application',22,'change_socialapp'),(66,'Can delete social application',22,'delete_socialapp'),(67,'Can add social application token',23,'add_socialtoken'),(68,'Can change social application token',23,'change_socialtoken'),(69,'Can delete social application token',23,'delete_socialtoken'),(70,'Can add social account',24,'add_socialaccount'),(71,'Can change social account',24,'change_socialaccount'),(72,'Can delete social account',24,'delete_socialaccount');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(30) NOT NULL,
  `last_name` varchar(30) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
INSERT INTO `auth_user` VALUES (1,'pbkdf2_sha256$36000$LtASs5h8z6Jr$86bqPC/cu3f7mc51eHP6x+VnXEjz2sBweIO64qzQHIA=','2017-06-30 10:06:27.351789',1,'proofx','','','achievement008@gmail.com',1,1,'2017-06-30 10:04:56.036433');
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
INSERT INTO `django_admin_log` VALUES (1,'2017-06-30 10:10:57.158147','1','<btc-e>',1,'[{\"added\": {}}]',13,1),(2,'2017-06-30 10:11:12.539173','2','<bittrex>',1,'[{\"added\": {}}]',13,1),(3,'2017-06-30 10:11:24.177797','3','<poloniex>',1,'[{\"added\": {}}]',13,1),(4,'2017-06-30 10:11:40.061400','1','Yandex Money',1,'[{\"added\": {}}]',14,1),(5,'2017-06-30 10:11:47.078118','2','ETH',1,'[{\"added\": {}}]',14,1),(6,'2017-06-30 10:11:51.193279','3','BTC',1,'[{\"added\": {}}]',14,1),(7,'2017-06-30 11:49:52.591526','1','<proofx Yandex Money: 0E-8>',3,'',9,1);
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_celery_beat_crontabschedule`
--

DROP TABLE IF EXISTS `django_celery_beat_crontabschedule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_celery_beat_crontabschedule` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `minute` varchar(64) NOT NULL,
  `hour` varchar(64) NOT NULL,
  `day_of_week` varchar(64) NOT NULL,
  `day_of_month` varchar(64) NOT NULL,
  `month_of_year` varchar(64) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_celery_beat_crontabschedule`
--

LOCK TABLES `django_celery_beat_crontabschedule` WRITE;
/*!40000 ALTER TABLE `django_celery_beat_crontabschedule` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_celery_beat_crontabschedule` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_celery_beat_intervalschedule`
--

DROP TABLE IF EXISTS `django_celery_beat_intervalschedule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_celery_beat_intervalschedule` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `every` int(11) NOT NULL,
  `period` varchar(24) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_celery_beat_intervalschedule`
--

LOCK TABLES `django_celery_beat_intervalschedule` WRITE;
/*!40000 ALTER TABLE `django_celery_beat_intervalschedule` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_celery_beat_intervalschedule` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_celery_beat_periodictask`
--

DROP TABLE IF EXISTS `django_celery_beat_periodictask`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_celery_beat_periodictask` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `task` varchar(200) NOT NULL,
  `args` longtext NOT NULL,
  `kwargs` longtext NOT NULL,
  `queue` varchar(200) DEFAULT NULL,
  `exchange` varchar(200) DEFAULT NULL,
  `routing_key` varchar(200) DEFAULT NULL,
  `expires` datetime(6) DEFAULT NULL,
  `enabled` tinyint(1) NOT NULL,
  `last_run_at` datetime(6) DEFAULT NULL,
  `total_run_count` int(10) unsigned NOT NULL,
  `date_changed` datetime(6) NOT NULL,
  `description` longtext NOT NULL,
  `crontab_id` int(11) DEFAULT NULL,
  `interval_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `django_celery_beat_p_crontab_id_d3cba168_fk_django_ce` (`crontab_id`),
  KEY `django_celery_beat_p_interval_id_a8ca27da_fk_django_ce` (`interval_id`),
  CONSTRAINT `django_celery_beat_p_crontab_id_d3cba168_fk_django_ce` FOREIGN KEY (`crontab_id`) REFERENCES `django_celery_beat_crontabschedule` (`id`),
  CONSTRAINT `django_celery_beat_p_interval_id_a8ca27da_fk_django_ce` FOREIGN KEY (`interval_id`) REFERENCES `django_celery_beat_intervalschedule` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_celery_beat_periodictask`
--

LOCK TABLES `django_celery_beat_periodictask` WRITE;
/*!40000 ALTER TABLE `django_celery_beat_periodictask` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_celery_beat_periodictask` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_celery_beat_periodictasks`
--

DROP TABLE IF EXISTS `django_celery_beat_periodictasks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_celery_beat_periodictasks` (
  `ident` smallint(6) NOT NULL,
  `last_update` datetime(6) NOT NULL,
  PRIMARY KEY (`ident`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_celery_beat_periodictasks`
--

LOCK TABLES `django_celery_beat_periodictasks` WRITE;
/*!40000 ALTER TABLE `django_celery_beat_periodictasks` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_celery_beat_periodictasks` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (21,'account','emailaddress'),(20,'account','emailconfirmation'),(1,'admin','logentry'),(4,'auth','group'),(3,'auth','permission'),(2,'auth','user'),(5,'contenttypes','contenttype'),(17,'django_celery_beat','crontabschedule'),(18,'django_celery_beat','intervalschedule'),(16,'django_celery_beat','periodictask'),(19,'django_celery_beat','periodictasks'),(6,'sessions','session'),(7,'sites','site'),(24,'socialaccount','socialaccount'),(22,'socialaccount','socialapp'),(23,'socialaccount','socialtoken'),(12,'trade','coin'),(13,'trade','exchanges'),(10,'trade','userbalance'),(15,'trade','userexchanges'),(11,'trade','userholdings'),(9,'trade','userwallet'),(8,'trade','wallethistory'),(14,'trade','wallets');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_migrations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=43 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2017-06-30 10:03:45.384796'),(2,'auth','0001_initial','2017-06-30 10:03:47.350399'),(3,'account','0001_initial','2017-06-30 10:03:47.905756'),(4,'account','0002_email_max_length','2017-06-30 10:03:48.187047'),(5,'admin','0001_initial','2017-06-30 10:03:48.719391'),(6,'admin','0002_logentry_remove_auto_add','2017-06-30 10:03:48.762550'),(7,'contenttypes','0002_remove_content_type_name','2017-06-30 10:03:49.058469'),(8,'auth','0002_alter_permission_name_max_length','2017-06-30 10:03:49.211002'),(9,'auth','0003_alter_user_email_max_length','2017-06-30 10:03:49.332249'),(10,'auth','0004_alter_user_username_opts','2017-06-30 10:03:49.346642'),(11,'auth','0005_alter_user_last_login_null','2017-06-30 10:03:49.486073'),(12,'auth','0006_require_contenttypes_0002','2017-06-30 10:03:49.494375'),(13,'auth','0007_alter_validators_add_error_messages','2017-06-30 10:03:49.519109'),(14,'auth','0008_alter_user_username_max_length','2017-06-30 10:03:49.727435'),(15,'django_celery_beat','0001_initial','2017-06-30 10:03:50.651859'),(16,'sessions','0001_initial','2017-06-30 10:03:50.757255'),(17,'sites','0001_initial','2017-06-30 10:03:50.820587'),(18,'sites','0002_alter_domain_unique','2017-06-30 10:03:50.873890'),(19,'socialaccount','0001_initial','2017-06-30 10:03:51.977811'),(20,'socialaccount','0002_token_max_lengths','2017-06-30 10:03:52.050387'),(21,'socialaccount','0003_extra_data_default_dict','2017-06-30 10:03:52.069528'),(22,'trade','0001_initial','2017-06-30 10:03:52.969614'),(23,'trade','0002_auto_20170613_1345','2017-06-30 10:03:53.067385'),(24,'trade','0003_userexchanges_error','2017-06-30 10:03:53.218317'),(25,'trade','0004_auto_20170614_0951','2017-06-30 10:03:53.934632'),(26,'trade','0005_userwallet_address','2017-06-30 10:03:54.055871'),(27,'trade','0006_auto_20170614_1025','2017-06-30 10:03:54.104850'),(28,'trade','0007_auto_20170614_1146','2017-06-30 10:03:54.462990'),(29,'trade','0008_auto_20170614_1318','2017-06-30 10:03:54.634999'),(30,'trade','0009_auto_20170615_1106','2017-06-30 10:03:54.910979'),(31,'trade','0010_auto_20170615_1227','2017-06-30 10:03:55.116144'),(32,'trade','0011_userwallet_access_token','2017-06-30 10:03:55.292224'),(33,'trade','0012_auto_20170620_0921','2017-06-30 10:03:55.984477'),(34,'trade','0013_auto_20170620_0933','2017-06-30 10:03:56.242522'),(35,'trade','0014_auto_20170620_1022','2017-06-30 10:03:56.352906'),(36,'trade','0015_userexchanges_total_usd','2017-06-30 10:03:56.473686'),(37,'trade','0016_userwallet_total_usd','2017-06-30 10:03:56.602310'),(38,'trade','0017_userwallet_last_update','2017-06-30 10:03:56.755852'),(39,'trade','0018_userholdings','2017-06-30 10:03:56.951475'),(40,'trade','0019_userwallet_total_btc','2017-06-30 10:03:57.098690'),(41,'trade','0020_auto_20170629_1353','2017-06-30 10:03:57.168075'),(42,'trade','0021_auto_20170630_0823','2017-06-30 10:03:57.921938');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('p5ftlmx4duq2lfg0rqbxws3zw3cto521','OGYzYzczMjZhNWNhMDY5NjljNWY1ZDc5Y2ZiMzA4ZDIwMjZmNzI2NDp7Il9zZXNzaW9uX2V4cGlyeSI6MCwiX2F1dGhfdXNlcl9oYXNoIjoiNDFkN2JlMTFlMmEzYmM3Y2QwYWUxNjA3NDI3ZWQ2NmNlNzY2YmU5OCIsIl9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmQifQ==','2017-07-14 10:06:27.362044');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_site`
--

DROP TABLE IF EXISTS `django_site`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_site` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `domain` varchar(100) NOT NULL,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_site_domain_a2e37b91_uniq` (`domain`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_site`
--

LOCK TABLES `django_site` WRITE;
/*!40000 ALTER TABLE `django_site` DISABLE KEYS */;
INSERT INTO `django_site` VALUES (1,'example.com','example.com');
/*!40000 ALTER TABLE `django_site` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `socialaccount_socialaccount`
--

DROP TABLE IF EXISTS `socialaccount_socialaccount`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `socialaccount_socialaccount` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `provider` varchar(30) NOT NULL,
  `uid` varchar(191) NOT NULL,
  `last_login` datetime(6) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `extra_data` longtext NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `socialaccount_socialaccount_provider_uid_fc810c6e_uniq` (`provider`,`uid`),
  KEY `socialaccount_socialaccount_user_id_8146e70c_fk_auth_user_id` (`user_id`),
  CONSTRAINT `socialaccount_socialaccount_user_id_8146e70c_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `socialaccount_socialaccount`
--

LOCK TABLES `socialaccount_socialaccount` WRITE;
/*!40000 ALTER TABLE `socialaccount_socialaccount` DISABLE KEYS */;
/*!40000 ALTER TABLE `socialaccount_socialaccount` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `socialaccount_socialapp`
--

DROP TABLE IF EXISTS `socialaccount_socialapp`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `socialaccount_socialapp` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `provider` varchar(30) NOT NULL,
  `name` varchar(40) NOT NULL,
  `client_id` varchar(191) NOT NULL,
  `secret` varchar(191) NOT NULL,
  `key` varchar(191) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `socialaccount_socialapp`
--

LOCK TABLES `socialaccount_socialapp` WRITE;
/*!40000 ALTER TABLE `socialaccount_socialapp` DISABLE KEYS */;
/*!40000 ALTER TABLE `socialaccount_socialapp` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `socialaccount_socialapp_sites`
--

DROP TABLE IF EXISTS `socialaccount_socialapp_sites`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `socialaccount_socialapp_sites` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `socialapp_id` int(11) NOT NULL,
  `site_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `socialaccount_socialapp_sites_socialapp_id_site_id_71a9a768_uniq` (`socialapp_id`,`site_id`),
  KEY `socialaccount_socialapp_sites_site_id_2579dee5_fk_django_site_id` (`site_id`),
  CONSTRAINT `socialaccount_social_socialapp_id_97fb6e7d_fk_socialacc` FOREIGN KEY (`socialapp_id`) REFERENCES `socialaccount_socialapp` (`id`),
  CONSTRAINT `socialaccount_socialapp_sites_site_id_2579dee5_fk_django_site_id` FOREIGN KEY (`site_id`) REFERENCES `django_site` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `socialaccount_socialapp_sites`
--

LOCK TABLES `socialaccount_socialapp_sites` WRITE;
/*!40000 ALTER TABLE `socialaccount_socialapp_sites` DISABLE KEYS */;
/*!40000 ALTER TABLE `socialaccount_socialapp_sites` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `socialaccount_socialtoken`
--

DROP TABLE IF EXISTS `socialaccount_socialtoken`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `socialaccount_socialtoken` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `token` longtext NOT NULL,
  `token_secret` longtext NOT NULL,
  `expires_at` datetime(6) DEFAULT NULL,
  `account_id` int(11) NOT NULL,
  `app_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `socialaccount_socialtoken_app_id_account_id_fca4e0ac_uniq` (`app_id`,`account_id`),
  KEY `socialaccount_social_account_id_951f210e_fk_socialacc` (`account_id`),
  CONSTRAINT `socialaccount_social_account_id_951f210e_fk_socialacc` FOREIGN KEY (`account_id`) REFERENCES `socialaccount_socialaccount` (`id`),
  CONSTRAINT `socialaccount_social_app_id_636a42d7_fk_socialacc` FOREIGN KEY (`app_id`) REFERENCES `socialaccount_socialapp` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `socialaccount_socialtoken`
--

LOCK TABLES `socialaccount_socialtoken` WRITE;
/*!40000 ALTER TABLE `socialaccount_socialtoken` DISABLE KEYS */;
/*!40000 ALTER TABLE `socialaccount_socialtoken` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `trade_coin`
--

DROP TABLE IF EXISTS `trade_coin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `trade_coin` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `short_name` varchar(20) NOT NULL,
  `full_name` varchar(40) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=286 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `trade_coin`
--

LOCK TABLES `trade_coin` WRITE;
/*!40000 ALTER TABLE `trade_coin` DISABLE KEYS */;
INSERT INTO `trade_coin` VALUES (1,'ARDR','Ardor'),(2,'DCR','Decred'),(3,'RIC','Riecoin'),(4,'NXTI','NXTInspect'),(5,'SOC','SocialCoin'),(6,'XHC','Honorcoin'),(7,'DVK','DvoraKoin'),(8,'NOBL','NobleCoin'),(9,'CYC','Conspiracy Coin'),(10,'CNMT','Coinomat1'),(11,'VRC','VeriCoin'),(12,'ABY','ArtByte'),(13,'PINK','Pinkcoin'),(14,'BOST','BoostCoin'),(15,'HYP','HyperStake'),(16,'EXE','Execoin'),(17,'DAO','The DAO'),(18,'GEMZ','GetGems'),(19,'LBC','LBRY Credits'),(20,'COMM','CommunityCoin'),(21,'ACH','Altcoin Herald'),(22,'EXP','Expanse'),(23,'MEC','Megacoin'),(24,'SRG','Surge'),(25,'WOLF','InsanityCoin'),(26,'UIS','Unitus'),(27,'SUM','SummerCoin'),(28,'NAS','NAS'),(29,'SJCX','Storjcoin X'),(30,'XXC','CREDS'),(31,'PASC','PascalCoin'),(32,'CHA','Chancecoin'),(33,'JUG','JuggaloCoin'),(34,'GML','GameleagueCoin'),(35,'HIRO','Hirocoin'),(36,'PPC','Peercoin'),(37,'MNTA','Moneta'),(38,'PRT','Particle'),(39,'BCY','BitCrystals'),(40,'SC','Siacoin'),(41,'GIAR','Giarcoin'),(42,'PTS','BitShares PTS'),(43,'DGB','DigiByte'),(44,'LGC','Logicoin'),(45,'CNOTE','C-Note'),(46,'SDC','Shadow'),(47,'MMNXT','MMNXT'),(48,'GAP','Gapcoin'),(49,'MIL','Millennium Coin'),(50,'CORG','CorgiCoin'),(51,'RDD','Reddcoin'),(52,'SRCC','SourceCoin'),(53,'XLB','Libertycoin'),(54,'LCL','Limecoin Lite'),(55,'CACH','CACHeCoin'),(56,'WIKI','Wikicoin'),(57,'CLAM','CLAMS'),(58,'FAC','Faircoin'),(59,'FCT','Factom'),(60,'FRK','Franko'),(61,'XAI','Sapience AIFX'),(62,'NXC','Nexium'),(63,'PLX','ParallaxCoin'),(64,'XAP','API Coin'),(65,'DNS','BitShares DNS'),(66,'QORA','Qora'),(67,'NAV','NAVCoin'),(68,'EMC2','Einsteinium'),(69,'AUR','Auroracoin'),(70,'CCN','Cannacoin'),(71,'C2','Coin2.0'),(72,'SUN','Suncoin'),(73,'FIBRE','Fibrecoin'),(74,'VOOT','VootCoin'),(75,'XSI','Stability Shares'),(76,'IOC','IO Digital Currency'),(77,'NBT','NuBits'),(78,'CINNI','CinniCoin'),(79,'MAX','MaxCoin'),(80,'XCP','Counterparty'),(81,'HOT','Hotcoin'),(82,'HUGE','BIGcoin'),(83,'QBK','Qibuck'),(84,'BTM','Bitmark'),(85,'GUE','Guerillacoin'),(86,'HUC','Huntercoin'),(87,'SQL','Squallcoin'),(88,'BBL','BitBlock'),(89,'USDE','USDE'),(90,'VOX','Voxels'),(91,'XSV','Silicon Valley Coin'),(92,'URO','Uro'),(93,'UNITY','SuperNET'),(94,'CC','Colbert Coin'),(95,'NOTE','DNotes'),(96,'KDC','KlondikeCoin'),(97,'GRC','Gridcoin Research'),(98,'STEEM','STEEM'),(99,'ITC','Information Coin'),(100,'1CR','1CRedit'),(101,'BDG','Badgercoin'),(102,'SWARM','SWARM'),(103,'MAST','MastiffCoin'),(104,'USDT','Tether USD'),(105,'XC','XCurrency'),(106,'GPC','GROUPCoin'),(107,'AIR','AIRcoin'),(108,'GNT','Golem'),(109,'STR','Stellar'),(110,'FZN','Fuzon'),(111,'YIN','Yincoin'),(112,'XST','StealthCoin'),(113,'SLR','SolarCoin'),(114,'LQD','LIQUID'),(115,'FRQ','FairQuark'),(116,'AC','AsiaCoin'),(117,'BITCNY','BitCNY'),(118,'PMC','Premine'),(119,'MRC','microCoin'),(120,'TAC','Talkcoin'),(121,'XVC','Vcash'),(122,'ETC','Ethereum Classic'),(123,'ECC','ECCoin'),(124,'ADN','Aiden'),(125,'XRP','Ripple'),(126,'JPC','JackpotCoin'),(127,'KEY','KeyCoin'),(128,'TWE','Twecoin'),(129,'METH','CryptoMETH'),(130,'BALLS','Snowballs'),(131,'MMXIV','Maieuticoin'),(132,'FLT','FlutterCoin'),(133,'XEM','NEM'),(134,'XCH','ClearingHouse'),(135,'DIS','DistroCoin'),(136,'BBR','Boolberry'),(137,'NRS','NoirShares'),(138,'XBC','BitcoinPlus'),(139,'XPM','Primecoin'),(140,'DIEM','Diem'),(141,'MCN','Moneta Verde'),(142,'EMO','EmotiCoin'),(143,'IXC','iXcoin'),(144,'GOLD','GoldEagles'),(145,'SMC','SmartCoin'),(146,'FVZ','FVZCoin'),(147,'NEOS','Neoscoin'),(148,'MYR','Myriadcoin'),(149,'PIGGY','New Piggycoin'),(150,'MUN','Muniti'),(151,'WDC','Worldcoin'),(152,'YANG','Yangcoin'),(153,'VIA','Viacoin'),(154,'DRKC','DarkCash'),(155,'AXIS','Axis'),(156,'EAC','EarthCoin'),(157,'SILK','Silkcoin'),(158,'XCN','Cryptonite'),(159,'CRYPT','CryptCoin'),(160,'BELA','Belacoin'),(161,'NSR','NuShares'),(162,'UTC','UltraCoin'),(163,'MIN','Minerals'),(164,'FLAP','FlappyCoin'),(165,'DICE','NeoDICE'),(166,'BITUSD','BitUSD'),(167,'XUSD','CoinoUSD'),(168,'QCN','QuazarCoin'),(169,'HZ','Horizon'),(170,'ARCH','ARCHcoin'),(171,'XDN','DigitalNote'),(172,'PAWN','Pawncoin'),(173,'FZ','Frozen'),(174,'BLOCK','Blocknet'),(175,'CON','Coino'),(176,'NXT','NXT'),(177,'SPA','Spaincoin'),(178,'LOL','LeagueCoin'),(179,'TOR','TorCoin'),(180,'CAI','CaiShen'),(181,'BLU','BlueCoin'),(182,'POT','PotCoin'),(183,'GAME','GameCredits'),(184,'PAND','PandaCoin'),(185,'SYNC','Sync'),(186,'YACC','YACCoin'),(187,'AEON','AEON Coin'),(188,'YC','YellowCoin'),(189,'AMP','Synereo AMP'),(190,'FLDC','FoldingCoin'),(191,'DRM','Dreamcoin'),(192,'LOVE','LOVEcoin'),(193,'BTCS','Bitcoin-sCrypt'),(194,'GNS','GenesisCoin'),(195,'RZR','Razor'),(196,'UTIL','UtilityCoin'),(197,'ENC','Entropycoin'),(198,'APH','AphroditeCoin'),(199,'H2O','H2O Coin'),(200,'STRAT','Stratis'),(201,'XPB','Pebblecoin'),(202,'DOGE','Dogecoin'),(203,'MINT','Mintcoin'),(204,'CURE','Curecoin'),(205,'BURST','Burst'),(206,'GLB','Globe'),(207,'SHIBE','ShibeCoin'),(208,'ZEC','Zcash'),(209,'RBY','Rubycoin'),(210,'SXC','Sexcoin'),(211,'NTX','NTX'),(212,'CGA','Cryptographic Anomaly'),(213,'XCR','Crypti'),(214,'X13','X13Coin'),(215,'IFC','Infinitecoin'),(216,'LSK','Lisk'),(217,'NMC','Namecoin'),(218,'SSD','Sonic'),(219,'EFL','Electronic Gulden'),(220,'WC','WhiteCoin'),(221,'MAID','MaidSafeCoin'),(222,'LTBC','LTBCoin'),(223,'MTS','Metiscoin'),(224,'Q2C','QubitCoin'),(225,'GPUC','GPU Coin'),(226,'NOXT','NobleNXT'),(227,'BTCD','BitcoinDark'),(228,'GDN','Global Denomination'),(229,'BCC','BTCtalkcoin'),(230,'FCN','Fantomcoin'),(231,'ULTC','Umbrella-LTC'),(232,'BITS','Bitstar'),(233,'eTOK','eToken'),(234,'SHOPX','ShopX'),(235,'BNS','BonusCoin'),(236,'RADS','Radium'),(237,'INDEX','CoinoIndex'),(238,'MMC','MemoryCoin'),(239,'UVC','UniversityCoin'),(240,'XMR','Monero'),(241,'DIME','Dimecoin'),(242,'PRC','ProsperCoin'),(243,'CNL','ConcealCoin'),(244,'LEAF','Leafcoin'),(245,'HVC','Heavycoin'),(246,'VTC','Vertcoin'),(247,'XDP','Dogeparty'),(248,'REP','Augur'),(249,'LTCX','LiteCoinX'),(250,'OPAL','Opal'),(251,'SBD','Steem Dollars'),(252,'EBT','EBTcoin'),(253,'QTL','Quatloo'),(254,'GRCX','Gridcoin'),(255,'MON','Monocle'),(256,'JLH','jl777hodl'),(257,'BTC','Bitcoin'),(258,'SYS','Syscoin'),(259,'MZC','MazaCoin'),(260,'BCN','Bytecoin'),(261,'AERO','Aerocoin'),(262,'FOX','FoxCoin'),(263,'FLO','Florincoin'),(264,'BANK','BankCoin'),(265,'XMG','Magi'),(266,'DASH','Dash'),(267,'N5X','N5coin'),(268,'TRUST','TrustPlus'),(269,'FRAC','Fractalcoin'),(270,'LTC','Litecoin'),(271,'LC','Limecoin'),(272,'NL','Nanolite'),(273,'NAUT','Nautiluscoin'),(274,'OMNI','Omni'),(275,'GRS','Groestlcoin'),(276,'DSH','Dashcoin'),(277,'BURN','BurnerCoin'),(278,'BTS','BitShares'),(279,'MRS','Marscoin'),(280,'BDC','Black Dragon Coin'),(281,'ETH','Ethereum'),(282,'GEO','GeoCoin'),(283,'BLK','BlackCoin'),(284,'GNO','Gnosis'),(285,'BONES','Bones');
/*!40000 ALTER TABLE `trade_coin` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `trade_exchanges`
--

DROP TABLE IF EXISTS `trade_exchanges`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `trade_exchanges` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `exchange` varchar(255) NOT NULL,
  `url` varchar(200) NOT NULL,
  `driver` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `trade_exchanges`
--

LOCK TABLES `trade_exchanges` WRITE;
/*!40000 ALTER TABLE `trade_exchanges` DISABLE KEYS */;
INSERT INTO `trade_exchanges` VALUES (1,'btc-e','https://btc-e.nz/','1'),(2,'bittrex','https://bittrex.com/','2'),(3,'poloniex','https://poloniex.com/','3');
/*!40000 ALTER TABLE `trade_exchanges` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `trade_userbalance`
--

DROP TABLE IF EXISTS `trade_userbalance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `trade_userbalance` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `coin` varchar(10) NOT NULL,
  `balance` decimal(30,8) NOT NULL,
  `btc_value` decimal(30,8) NOT NULL,
  `last_update` datetime(6) NOT NULL,
  `ue_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `trade_userbalance_ue_id_183f2acc_fk_trade_userexchanges_id` (`ue_id`),
  CONSTRAINT `trade_userbalance_ue_id_183f2acc_fk_trade_userexchanges_id` FOREIGN KEY (`ue_id`) REFERENCES `trade_userexchanges` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `trade_userbalance`
--

LOCK TABLES `trade_userbalance` WRITE;
/*!40000 ALTER TABLE `trade_userbalance` DISABLE KEYS */;
/*!40000 ALTER TABLE `trade_userbalance` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `trade_userexchanges`
--

DROP TABLE IF EXISTS `trade_userexchanges`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `trade_userexchanges` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `apikey` varchar(255) NOT NULL,
  `apisecret` varchar(255) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `is_correct` tinyint(1) NOT NULL,
  `total_btc` decimal(30,8) NOT NULL,
  `exchange_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `error` varchar(1000) NOT NULL,
  `total_usd` decimal(30,8) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `trade_userexchanges_exchange_id_66cb8e85_fk_trade_exchanges_id` (`exchange_id`),
  KEY `trade_userexchanges_user_id_fdd78d6a_fk_auth_user_id` (`user_id`),
  CONSTRAINT `trade_userexchanges_exchange_id_66cb8e85_fk_trade_exchanges_id` FOREIGN KEY (`exchange_id`) REFERENCES `trade_exchanges` (`id`),
  CONSTRAINT `trade_userexchanges_user_id_fdd78d6a_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `trade_userexchanges`
--

LOCK TABLES `trade_userexchanges` WRITE;
/*!40000 ALTER TABLE `trade_userexchanges` DISABLE KEYS */;
/*!40000 ALTER TABLE `trade_userexchanges` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `trade_userholdings`
--

DROP TABLE IF EXISTS `trade_userholdings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `trade_userholdings` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type` varchar(255) NOT NULL,
  `total_btc` decimal(30,8) NOT NULL,
  `total_usd` decimal(30,8) NOT NULL,
  `date_time` datetime(6) NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `trade_userholdings_user_id_eee18bcb_fk_auth_user_id` (`user_id`),
  CONSTRAINT `trade_userholdings_user_id_eee18bcb_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `trade_userholdings`
--

LOCK TABLES `trade_userholdings` WRITE;
/*!40000 ALTER TABLE `trade_userholdings` DISABLE KEYS */;
/*!40000 ALTER TABLE `trade_userholdings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `trade_userwallet`
--

DROP TABLE IF EXISTS `trade_userwallet`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `trade_userwallet` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `balance` decimal(30,8) NOT NULL,
  `user_id` int(11) NOT NULL,
  `wallet_id` int(11) NOT NULL,
  `address` varchar(511) NOT NULL,
  `access_token` varchar(511) DEFAULT NULL,
  `total_usd` decimal(30,8) NOT NULL,
  `last_update` datetime(6) NOT NULL,
  `total_btc` decimal(30,8) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `trade_userwallet_user_id_ff95ccb0_fk_auth_user_id` (`user_id`),
  KEY `trade_userwallet_wallet_id_640ae669_fk_trade_wallets_id` (`wallet_id`),
  CONSTRAINT `trade_userwallet_user_id_ff95ccb0_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `trade_userwallet_wallet_id_640ae669_fk_trade_wallets_id` FOREIGN KEY (`wallet_id`) REFERENCES `trade_wallets` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `trade_userwallet`
--

LOCK TABLES `trade_userwallet` WRITE;
/*!40000 ALTER TABLE `trade_userwallet` DISABLE KEYS */;
/*!40000 ALTER TABLE `trade_userwallet` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `trade_wallethistory`
--

DROP TABLE IF EXISTS `trade_wallethistory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `trade_wallethistory` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `number` bigint(20) NOT NULL,
  `date` datetime(6) NOT NULL,
  `t_from` longtext NOT NULL,
  `t_to` longtext NOT NULL,
  `type` varchar(255) NOT NULL,
  `value` decimal(30,8) NOT NULL,
  `hash` varchar(511) NOT NULL,
  `uw_id` int(11) NOT NULL,
  `block_hash` varchar(511) DEFAULT NULL,
  `comment` longtext,
  `details` varchar(1000) DEFAULT NULL,
  `title` varchar(1000) DEFAULT NULL,
  `usd_value` decimal(30,8) NOT NULL,
  `user_comment` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `trade_wallethistory_uw_id_number_e0602cb1_uniq` (`uw_id`,`number`),
  CONSTRAINT `trade_wallethistory_uw_id_38e51992_fk_trade_userwallet_id` FOREIGN KEY (`uw_id`) REFERENCES `trade_userwallet` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `trade_wallethistory`
--

LOCK TABLES `trade_wallethistory` WRITE;
/*!40000 ALTER TABLE `trade_wallethistory` DISABLE KEYS */;
/*!40000 ALTER TABLE `trade_wallethistory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `trade_wallets`
--

DROP TABLE IF EXISTS `trade_wallets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `trade_wallets` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `trade_wallets`
--

LOCK TABLES `trade_wallets` WRITE;
/*!40000 ALTER TABLE `trade_wallets` DISABLE KEYS */;
INSERT INTO `trade_wallets` VALUES (1,'Yandex Money'),(2,'ETH'),(3,'BTC');
/*!40000 ALTER TABLE `trade_wallets` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2017-06-30 14:52:33
