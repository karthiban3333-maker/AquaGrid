CREATE TABLE `geologicalStructures` (
  `id` int AUTO_INCREMENT NOT NULL,
  `villageId` int,
  `structureType` enum('fault','fracture','joint','contact','bedding') NOT NULL,
  `strike` int,
  `dip` int,
  `dipDirection` int,
  `geometry` json NOT NULL,
  `source` varchar(180) NOT NULL,
  `confidence` enum('low','medium','high') NOT NULL,
  `observedDate` timestamp,
  `createdAt` timestamp NOT NULL DEFAULT (now()),
  CONSTRAINT `geologicalStructures_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `lithology` (
  `id` int AUTO_INCREMENT NOT NULL,
  `villageId` int,
  `rockType` varchar(120) NOT NULL,
  `formationName` varchar(180),
  `geometry` json NOT NULL,
  `source` varchar(180) NOT NULL,
  `createdAt` timestamp NOT NULL DEFAULT (now()),
  CONSTRAINT `lithology_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `structures` (
  `id` int AUTO_INCREMENT NOT NULL,
  `villageId` int,
  `type` varchar(120) NOT NULL,
  `geometry` json NOT NULL,
  `condition` varchar(64),
  `yearBuilt` int,
  `source` varchar(180) NOT NULL,
  `verified` int NOT NULL DEFAULT 0,
  `createdAt` timestamp NOT NULL DEFAULT (now()),
  CONSTRAINT `structures_id` PRIMARY KEY(`id`)
);
