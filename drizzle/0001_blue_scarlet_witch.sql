CREATE TABLE `assessments` (
	`id` int AUTO_INCREMENT NOT NULL,
	`springId` int NOT NULL,
	`score` int NOT NULL,
	`factors` json NOT NULL,
	`reasons` json NOT NULL,
	`modelVersion` varchar(64) NOT NULL,
	`inputSnapshot` json NOT NULL,
	`confidence` enum('low','medium','high') NOT NULL,
	`generatedAt` timestamp NOT NULL DEFAULT (now()),
	`generatedBy` int,
	CONSTRAINT `assessments_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `auditLogs` (
	`id` int AUTO_INCREMENT NOT NULL,
	`actorId` int,
	`action` varchar(120) NOT NULL,
	`entityType` varchar(80) NOT NULL,
	`entityId` varchar(64) NOT NULL,
	`before` json,
	`after` json,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `auditLogs_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `monitoring` (
	`id` int AUTO_INCREMENT NOT NULL,
	`springId` int NOT NULL,
	`observedAt` timestamp NOT NULL,
	`dischargeLpm` int,
	`waterQualityStatus` varchar(64),
	`maintenanceStatus` varchar(64),
	`photoStoragePaths` json,
	`notes` text,
	`collectedBy` int,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `monitoring_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `observations` (
	`id` int AUTO_INCREMENT NOT NULL,
	`clientId` varchar(64) NOT NULL,
	`springId` int NOT NULL,
	`observedAt` timestamp NOT NULL,
	`dischargeLpm` int,
	`waterQualityStatus` varchar(64),
	`usersCount` int,
	`seasonalStatus` varchar(64),
	`notes` text,
	`voiceStoragePath` text,
	`photoStoragePaths` json,
	`location` json,
	`collectedBy` int,
	`syncState` enum('pending','synced','failed') NOT NULL DEFAULT 'pending',
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `observations_id` PRIMARY KEY(`id`),
	CONSTRAINT `observations_clientId_unique` UNIQUE(`clientId`)
);
--> statement-breakpoint
CREATE TABLE `plans` (
	`id` int AUTO_INCREMENT NOT NULL,
	`springId` int NOT NULL,
	`selectedRecommendations` json,
	`budgetRange` json,
	`beneficiaries` int,
	`validationNotes` text,
	`status` varchar(64) NOT NULL DEFAULT 'Draft',
	`reviewedBy` int,
	`approvedBy` int,
	`rejectionReason` text,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `plans_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `recommendations` (
	`id` int AUTO_INCREMENT NOT NULL,
	`springId` int NOT NULL,
	`interventionType` varchar(120) NOT NULL,
	`candidateLocation` json,
	`suitabilityFactors` json,
	`estimatedCostMin` int,
	`estimatedCostMax` int,
	`expectedPlanningBenefit` text,
	`constraints` json,
	`confidence` enum('low','medium','high') NOT NULL,
	`validationStatus` varchar(64) NOT NULL DEFAULT 'Pending',
	`generatedAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `recommendations_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `springs` (
	`id` int AUTO_INCREMENT NOT NULL,
	`clientId` varchar(64) NOT NULL,
	`villageId` int NOT NULL,
	`name` varchar(180) NOT NULL,
	`localName` varchar(180),
	`location` json NOT NULL,
	`elevationM` int,
	`usageTypes` json,
	`estimatedHouseholds` int NOT NULL DEFAULT 0,
	`baselineStatus` varchar(64),
	`currentStatus` varchar(64),
	`priorityScore` int,
	`priorityBand` enum('low','medium','high'),
	`confidence` enum('low','medium','high'),
	`dataCompleteness` int,
	`rechargeLayerRef` varchar(180),
	`approvalStatus` varchar(64) NOT NULL DEFAULT 'Draft',
	`createdBy` int,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `springs_id` PRIMARY KEY(`id`),
	CONSTRAINT `springs_clientId_unique` UNIQUE(`clientId`)
);
--> statement-breakpoint
CREATE TABLE `villages` (
	`id` int AUTO_INCREMENT NOT NULL,
	`name` varchar(180) NOT NULL,
	`localName` varchar(180),
	`district` varchar(120) NOT NULL,
	`state` varchar(120) NOT NULL,
	`centroid` json,
	`populationEstimate` int,
	`connectivityLevel` enum('low','medium','high') NOT NULL DEFAULT 'medium',
	`assignedFacilitatorIds` json,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `villages_id` PRIMARY KEY(`id`)
);
