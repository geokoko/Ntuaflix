<<<<<<< HEAD


DROP TABLE IF EXISTS `Title`;

CREATE TABLE `Title` (
  `Title_ID` char(9) NOT NULL,
=======
DROP DATABASE IF EXISTS tl;

CREATE DATABASE tl;
USE tl;

-- Drop tables if they exist
DROP TABLE IF EXISTS `Alt_Title`, `Is_Episode_Of`, `Participates_In`, `Title_Genre`, `Person`, `Genre`, `Title`;

-- Create table `Title`
CREATE TABLE `Title` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `Title_ID` char(9) NOT NULL UNIQUE,
>>>>>>> 9551302 (Changes to back-end:)
  `Original_Title` varchar(225) NOT NULL,
  `Type` varchar(225) NOT NULL,
  `IMAGE` varchar(255) DEFAULT NULL,
  `Start_Year` year DEFAULT NULL,
  `End_Year` year DEFAULT NULL,
<<<<<<< HEAD
  `Votes` int DEFAULT NULL,
  `Average_Rating` decimal(3,1) DEFAULT NULL,
  PRIMARY KEY (`Title_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `Alt_Title`;

CREATE TABLE `Alt_Title` (
  `Title_ID` char(9) NOT NULL,
  `Ordering` int NOT NULL,
  `Title_AKA` varchar(255) DEFAULT NULL,
  `Region` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`Title_ID`,`Ordering`),
  CONSTRAINT `alt_title_ibfk_1` FOREIGN KEY (`Title_ID`) REFERENCES `Title` (`Title_ID`),
  CONSTRAINT `title_deletion_alt` FOREIGN KEY (`Title_ID`) REFERENCES `Title` (`Title_ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


--
-- Table structure for table `Genre`
--

DROP TABLE IF EXISTS `Genre`;

CREATE TABLE `Genre` (
  `Genre_ID` int NOT NULL AUTO_INCREMENT,
  `Genre` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`Genre_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


--
-- Table structure for table `Is_Episode_Of`
--

DROP TABLE IF EXISTS `Is_Episode_Of`;

CREATE TABLE `Is_Episode_Of` (
  `Title_ID1` char(9) NOT NULL,
  `Title_ID2` char(9) NOT NULL,
  `Season` int DEFAULT NULL,
  `Episode_Num` int DEFAULT NULL,
  PRIMARY KEY (`Title_ID1`,`Title_ID2`),
  KEY `title2_deletion` (`Title_ID2`),
  CONSTRAINT `is_episode_of_ibfk_1` FOREIGN KEY (`Title_ID1`) REFERENCES `Title` (`Title_ID`),
  CONSTRAINT `is_episode_of_ibfk_2` FOREIGN KEY (`Title_ID2`) REFERENCES `Title` (`Title_ID`),
  CONSTRAINT `title1_deletion` FOREIGN KEY (`Title_ID1`) REFERENCES `Title` (`Title_ID`) ON DELETE CASCADE,
  CONSTRAINT `title2_deletion` FOREIGN KEY (`Title_ID2`) REFERENCES `Title` (`Title_ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Table structure for table `Person`
--

DROP TABLE IF EXISTS `Person`;

CREATE TABLE `Person` (
  `Name_ID` char(9) NOT NULL,
=======
  `Runtime` int DEFAULT NULL,
  `isAdult` int DEFAULT NULL,
  `Votes` int DEFAULT NULL,
  `Average_Rating` decimal(3,1) DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Create table `Alt_Title`
CREATE TABLE `Alt_Title` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `Title_FK` int NOT NULL,
  `Ordering` int NOT NULL,
  `Title_AKA` varchar(255) DEFAULT NULL,
  `Region` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  FOREIGN KEY (`Title_FK`) REFERENCES `Title` (`ID`) ON DELETE CASCADE,
  UNIQUE KEY `unique_alt_title` (`Title_FK`, `Title_AKA`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Create table `Genre`
CREATE TABLE `Genre` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `Genre` varchar(255) UNIQUE DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Create table `Is_Episode_Of`
CREATE TABLE `Episode` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `parentTitle_ID` int NOT NULL,
  `Title_ID` int NOT NULL,
  `Season` int DEFAULT NULL,
  `Episode_Num` int DEFAULT NULL,
  PRIMARY KEY (`ID`),
  FOREIGN KEY (`parentTitle_ID`) REFERENCES `Title` (`ID`) ON DELETE CASCADE,
  FOREIGN KEY (`Title_ID`) REFERENCES `Title` (`ID`) ON DELETE CASCADE,
  UNIQUE KEY `unique_episode` (`parentTitle_ID`, `Title_ID`, `Season`, `Episode_Num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Create table `Person`
CREATE TABLE `Person` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `Name_ID` char(9) NOT NULL UNIQUE,
>>>>>>> 9551302 (Changes to back-end:)
  `Name` varchar(255) DEFAULT NULL,
  `Image` varchar(255) DEFAULT NULL,
  `Birth_Year` year DEFAULT NULL,
  `Death_Year` year DEFAULT NULL,
<<<<<<< HEAD
  PRIMARY KEY (`Name_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;



DROP TABLE IF EXISTS `Participates_In`;

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

--
-- Table structure for table `Profession`
--

DROP TABLE IF EXISTS `Profession`;

CREATE TABLE `Profession` (
  `Profession_ID` int(11) NOT NULL AUTO_INCREMENT,
  `Profession` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`Profession_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


--
-- Table structure for table `Profession_Person`
--

DROP TABLE IF EXISTS `Profession_Person`;

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

--
-- Table structure for table `Title`
--

--
-- Table structure for table `Title_Genre`
--

DROP TABLE IF EXISTS `Title_Genre`;

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


/* Indexes for non-key columns */
CREATE INDEX idx_region ON Alt_Title (Region);
CREATE INDEX idx_title_aka ON Alt_Title (Title_AKA);
CREATE INDEX idx_genre ON Genre (Genre);
CREATE INDEX idx_season_episode ON Is_Episode_Of (Season, Episode_Num);
CREATE INDEX idx_job_category ON Participates_In (Job_Category);
CREATE INDEX idx_name ON Person (Name);
CREATE INDEX idx_birth_death_year ON Person (Birth_Year, Death_Year);
CREATE INDEX idx_profession ON Profession (Profession);

/* Triggers */

--Checking that end_year < start_year for series

DELIMITER //
CREATE TRIGGER check_end_year_before_insert 
BEFORE INSERT ON Title
FOR EACH ROW
BEGIN
  IF NEW.End_Year < NEW.Start_Year THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'End Year must be greater than or equal to Start Year';
  END IF;
END;
//

DELIMITER ;
=======
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Create table `Participates_In`
CREATE TABLE `Participates_In` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `Title_FK` int NOT NULL,
  `Name_FK` int NOT NULL,
  `Ordering` int(11) DEFAULT NULL,
  `Job_Category` varchar(255) DEFAULT NULL,
  `Character` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  FOREIGN KEY (`Title_FK`) REFERENCES `Title` (`ID`) ON DELETE CASCADE,
  FOREIGN KEY (`Name_FK`) REFERENCES `Person` (`ID`) ON DELETE CASCADE,
  UNIQUE KEY `unique_participation` (`Title_FK`, `Name_FK`, `Job_Category`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Create table `Title_Genre`
CREATE TABLE `Title_Genre` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `Title_FK` int NOT NULL,
  `Genre_FK` int NOT NULL,
  PRIMARY KEY (`ID`),
  FOREIGN KEY (`Title_FK`) REFERENCES `Title` (`ID`) ON DELETE CASCADE,
  FOREIGN KEY (`Genre_FK`) REFERENCES `Genre` (`ID`) ON DELETE CASCADE,
  UNIQUE KEY `unique_title_genre` (`Title_FK`, `Genre_FK`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Create indexes for non-key columns
CREATE INDEX idx_title_id ON `Title` (`Title_ID`);
CREATE INDEX idx_original_title ON `Title` (`Original_Title`);
CREATE INDEX idx_start_end_year ON `Title` (`Start_Year`, `End_Year`);
CREATE INDEX idx_type ON `Title` (`Type`);
CREATE INDEX idx_alt_title_ordering ON `Alt_Title` (`Ordering`);
CREATE INDEX idx_alt_title_aka ON `Alt_Title` (`Title_AKA`);
CREATE INDEX idx_alt_title_region ON `Alt_Title` (`Region`);
CREATE INDEX idx_genre ON `Genre` (`Genre`);
CREATE INDEX idx_episode_season ON `Episode` (`Season`);
CREATE INDEX idx_episode_number ON `Episode` (`Episode_Num`);
CREATE INDEX idx_person_name_id ON `Person` (`Name_ID`);
CREATE INDEX idx_person_name ON `Person` (`Name`);
CREATE INDEX idx_birth_death_year ON `Person` (`Birth_Year`, `Death_Year`);
CREATE INDEX idx_participates_ordering ON `Participates_In` (`Ordering`);
CREATE INDEX idx_participates_job_category ON `Participates_In` (`Job_Category`);
CREATE INDEX idx_profession ON `Profession` (`Profession`);
>>>>>>> 9551302 (Changes to back-end:)
