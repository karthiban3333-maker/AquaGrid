CREATE TABLE `dataSources` (
  `id` int AUTO_INCREMENT NOT NULL,
  `source` varchar(120) NOT NULL,
  `sourceRecordId` varchar(180),
  `villageId` int,
  `fetchedAt` timestamp NOT NULL,
  `observedFrom` timestamp,
  `observedTo` timestamp,
  `payload` json,
  `artifactPath` text,
  `spatialBounds` json,
  `processingVersion` varchar(64),
  `stale` int NOT NULL DEFAULT 0,
  `lastError` text,
  `createdAt` timestamp NOT NULL DEFAULT (now()),
  `updatedAt` timestamp NOT NULL DEFAULT (now()),
  CONSTRAINT `dataSources_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE INDEX `dataSources_source_village_idx` ON `dataSources` (`source`,`villageId`);
