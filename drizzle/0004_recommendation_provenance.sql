ALTER TABLE `recommendations` ADD `modelVersion` varchar(64);
--> statement-breakpoint
ALTER TABLE `recommendations` ADD `inputSnapshot` json;
