-- MariaDB dump 10.19  Distrib 10.4.28-MariaDB, for osx10.10 (x86_64)
--
-- Host: localhost    Database: ntuaflix
-- ------------------------------------------------------
-- Server version	10.4.28-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `Alt_Title`
--

DROP TABLE IF EXISTS `Alt_Title`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Alt_Title` (
  `Title_ID` char(9) NOT NULL,
  `Ordering` int(11) NOT NULL,
  `Title_AKA` varchar(255) DEFAULT NULL,
  `Region` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`Title_ID`,`Ordering`),
  CONSTRAINT `alt_title_ibfk_1` FOREIGN KEY (`Title_ID`) REFERENCES `Title` (`Title_ID`),
  CONSTRAINT `title_deletion_alt` FOREIGN KEY (`Title_ID`) REFERENCES `Title` (`Title_ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Genre`
--

DROP TABLE IF EXISTS `Genre`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Genre` (
  `Genre_ID` int(11) NOT NULL AUTO_INCREMENT,
  `Genre` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`Genre_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Is_Episode_Of`
--

DROP TABLE IF EXISTS `Is_Episode_Of`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Is_Episode_Of` (
  `Title_ID1` char(9) NOT NULL,
  `Title_ID2` char(9) NOT NULL,
  `Season` int(11) DEFAULT NULL,
  `Episode_Num` int(11) DEFAULT NULL,
  PRIMARY KEY (`Title_ID1`,`Title_ID2`),
  KEY `title2_deletion` (`Title_ID2`),
  CONSTRAINT `is_episode_of_ibfk_1` FOREIGN KEY (`Title_ID1`) REFERENCES `Title` (`Title_ID`),
  CONSTRAINT `is_episode_of_ibfk_2` FOREIGN KEY (`Title_ID2`) REFERENCES `Title` (`Title_ID`),
  CONSTRAINT `title1_deletion` FOREIGN KEY (`Title_ID1`) REFERENCES `Title` (`Title_ID`) ON DELETE CASCADE,
  CONSTRAINT `title2_deletion` FOREIGN KEY (`Title_ID2`) REFERENCES `Title` (`Title_ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Participates_In`
--

DROP TABLE IF EXISTS `Participates_In`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Participates_In` (
  `Title_ID` char(9) NOT NULL,
  `Name_ID` char(9) NOT NULL,
  `Ordering` int(11) DEFAULT NULL,
  `Job_Category` int(11) DEFAULT NULL,
  PRIMARY KEY (`Title_ID`,`Name_ID`),
  KEY `person_deletion_participates` (`Name_ID`),
  CONSTRAINT `participates_in_ibfk_1` FOREIGN KEY (`Title_ID`) REFERENCES `Title` (`Title_ID`),
  CONSTRAINT `participates_in_ibfk_2` FOREIGN KEY (`Name_ID`) REFERENCES `Person` (`Name_ID`),
  CONSTRAINT `person_deletion_participates` FOREIGN KEY (`Name_ID`) REFERENCES `Person` (`Name_ID`) ON DELETE CASCADE,
  CONSTRAINT `title_deletion_participates` FOREIGN KEY (`Title_ID`) REFERENCES `Title` (`Title_ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Person`
--

DROP TABLE IF EXISTS `Person`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Person` (
  `Name_ID` char(9) NOT NULL,
  `Name` varchar(255) DEFAULT NULL,
  `Image` varchar(255) DEFAULT NULL,
  `Birth_Year` tinyint(4) DEFAULT NULL,
  `Death_Year` tinyint(4) DEFAULT NULL,
  PRIMARY KEY (`Name_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Profession`
--

DROP TABLE IF EXISTS `Profession`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Profession` (
  `Profession_ID` int(11) NOT NULL AUTO_INCREMENT,
  `Profession` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`Profession_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Profession_Person`
--

DROP TABLE IF EXISTS `Profession_Person`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Profession_Person` (
  `Profession_ID` int(11) NOT NULL,
  `Name_ID` char(9) NOT NULL,
  PRIMARY KEY (`Profession_ID`,`Name_ID`),
  KEY `person_deletion` (`Name_ID`),
  CONSTRAINT `person_deletion` FOREIGN KEY (`Name_ID`) REFERENCES `Person` (`Name_ID`) ON DELETE CASCADE,
  CONSTRAINT `profession_deletion` FOREIGN KEY (`Profession_ID`) REFERENCES `Profession` (`Profession_ID`) ON DELETE CASCADE,
  CONSTRAINT `profession_person_ibfk_1` FOREIGN KEY (`Profession_ID`) REFERENCES `Profession` (`Profession_ID`),
  CONSTRAINT `profession_person_ibfk_2` FOREIGN KEY (`Name_ID`) REFERENCES `Person` (`Name_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Title`
--

DROP TABLE IF EXISTS `Title`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Title` (
  `Title_ID` char(9) NOT NULL,
  `Original_Title` varchar(225) NOT NULL,
  `Type` varchar(225) NOT NULL,
  `IMAGE` varchar(255) DEFAULT NULL,
  `Start_Year` tinyint(4) DEFAULT NULL,
  `End_Year` tinyint(4) DEFAULT NULL,
  `VOTES` int(11) DEFAULT NULL,
  `Average_Rating` decimal(3,1) DEFAULT NULL,
  PRIMARY KEY (`Title_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Title_Genre`
--

DROP TABLE IF EXISTS `Title_Genre`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Title_Genre` (
  `Title_ID` char(9) NOT NULL,
  `Genre_ID` int(11) NOT NULL,
  PRIMARY KEY (`Title_ID`,`Genre_ID`),
  KEY `genre_deletion` (`Genre_ID`),
  CONSTRAINT `genre_deletion` FOREIGN KEY (`Genre_ID`) REFERENCES `Genre` (`Genre_ID`) ON DELETE CASCADE,
  CONSTRAINT `title_deletion` FOREIGN KEY (`Title_ID`) REFERENCES `Title` (`Title_ID`) ON DELETE CASCADE,
  CONSTRAINT `title_genre_ibfk_1` FOREIGN KEY (`Title_ID`) REFERENCES `Title` (`Title_ID`),
  CONSTRAINT `title_genre_ibfk_2` FOREIGN KEY (`Genre_ID`) REFERENCES `Genre` (`Genre_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-12-17 14:59:36
