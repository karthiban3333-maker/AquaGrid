CREATE TABLE `springIssues` (
	`id` int AUTO_INCREMENT NOT NULL,
	`clientId` varchar(64) NOT NULL,
	`springId` int NOT NULL,
	`issueType` varchar(80) NOT NULL,
	`description` text NOT NULL,
	`reporterId` int,
	`status` enum('open','reviewing','resolved') NOT NULL DEFAULT 'open',
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `springIssues_id` PRIMARY KEY(`id`),
	CONSTRAINT `springIssues_clientId_unique` UNIQUE(`clientId`)
);
--> statement-breakpoint
ALTER TABLE `users` MODIFY COLUMN `role` enum('user','visitor','admin') NOT NULL DEFAULT 'user';