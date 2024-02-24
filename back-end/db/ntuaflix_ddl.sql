DROP DATABASE IF EXISTS tl;

CREATE DATABASE tl;
USE tl;

-- Drop tables if they exist
DROP TABLE IF EXISTS `Alt_Title`, `Is_Episode_Of`, `Participates_In`, `Title_Genre`, `Person`, `Genre`, `Title`, `Profession`, `Profession_Person`;

-- Create table `Title`
CREATE TABLE `Title` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `Title_ID` varchar(255) NOT NULL UNIQUE,
  `Original_Title` varchar(255) NOT NULL,
  `Type` varchar(255) NOT NULL,
  `IMAGE` varchar(255) DEFAULT NULL,
  `Start_Year` int DEFAULT NULL,
  `End_Year` int DEFAULT NULL,
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
  UNIQUE KEY `unique_combination` (`Title_FK`, `Ordering`),
  FOREIGN KEY (`Title_FK`) REFERENCES `Title` (`ID`) ON DELETE CASCADE
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
  `Title_FK` int NOT NULL UNIQUE,
  `Parent_Title_FK` varchar(225) NOT NULL,
  `Season` int DEFAULT NULL,
  `Episode_Num` int DEFAULT NULL,
  PRIMARY KEY (`ID`),
  FOREIGN KEY (`Title_FK`) REFERENCES `Title` (`ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Create table `Person`
CREATE TABLE `Person` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `Name_ID` varchar(255) NOT NULL UNIQUE,
  `Name` varchar(255) DEFAULT NULL,
  `Image` varchar(255) DEFAULT NULL UNIQUE,
  `Birth_Year` int DEFAULT NULL,
  `Death_Year` int DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Create table `Participates_In`
CREATE TABLE `Participates_In` (
  `Title_FK` int NOT NULL ,
  `Name_FK` int NOT NULL,
  `Ordering` int(11) DEFAULT NULL,
  `Job_Category` varchar(255) DEFAULT NULL,
  `Character` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`Title_FK`, `Name_FK`, `Job_Category`),
  FOREIGN KEY (`Title_FK`) REFERENCES `Title` (`ID`) ON DELETE CASCADE,
  FOREIGN KEY (`Name_FK`) REFERENCES `Person` (`ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Create table `Title_Genre`
CREATE TABLE `Title_Genre` (
  `Title_FK` int NOT NULL,
  `Genre_FK` int NOT NULL,
  PRIMARY KEY (`Title_FK`, `Genre_FK`),
  FOREIGN KEY (`Title_FK`) REFERENCES `Title` (`ID`) ON DELETE CASCADE,
  FOREIGN KEY (`Genre_FK`) REFERENCES `Genre` (`ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Create table `Profession`
CREATE TABLE `Profession` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `Profession` varchar(255) DEFAULT NULL UNIQUE,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Create table `Profession_Person`
CREATE TABLE `Profession_Person` (
  `Profession_FK` int NOT NULL,
  `Name_FK` int NOT NULL,
  PRIMARY KEY (`Profession_FK`, `Name_FK`),
  FOREIGN KEY (`Profession_FK`) REFERENCES `Profession` (`ID`) ON DELETE CASCADE,
  FOREIGN KEY (`Name_FK`) REFERENCES `Person` (`ID`) ON DELETE CASCADE
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

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
