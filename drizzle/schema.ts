import { int, json, mysqlEnum, mysqlTable, text, timestamp, varchar } from "drizzle-orm/mysql-core";

export const users = mysqlTable("users", {
  id: int("id").autoincrement().primaryKey(),
  openId: varchar("openId", { length: 64 }).notNull().unique(),
  name: text("name"),
  email: varchar("email", { length: 320 }),
  loginMethod: varchar("loginMethod", { length: 64 }),
  role: mysqlEnum("role", ["user", "visitor", "admin"]).default("user").notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
  lastSignedIn: timestamp("lastSignedIn").defaultNow().notNull(),
});

export const villages = mysqlTable("villages", {
  id: int("id").autoincrement().primaryKey(),
  name: varchar("name", { length: 180 }).notNull(),
  localName: varchar("localName", { length: 180 }),
  district: varchar("district", { length: 120 }).notNull(),
  state: varchar("state", { length: 120 }).notNull(),
  centroid: json("centroid"),
  populationEstimate: int("populationEstimate"),
  connectivityLevel: mysqlEnum("connectivityLevel", ["low", "medium", "high"]).default("medium").notNull(),
  assignedFacilitatorIds: json("assignedFacilitatorIds"),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
});

export const geologicalStructures = mysqlTable("geologicalStructures", {
  id: int("id").autoincrement().primaryKey(),
  villageId: int("villageId"),
  structureType: mysqlEnum("structureType", ["fault", "fracture", "joint", "contact", "bedding"]).notNull(),
  strike: int("strike"),
  dip: int("dip"),
  dipDirection: int("dipDirection"),
  geometry: json("geometry").notNull(),
  source: varchar("source", { length: 180 }).notNull(),
  confidence: mysqlEnum("confidence", ["low", "medium", "high"]).notNull(),
  observedDate: timestamp("observedDate"),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
});

export const lithology = mysqlTable("lithology", {
  id: int("id").autoincrement().primaryKey(),
  villageId: int("villageId"),
  rockType: varchar("rockType", { length: 120 }).notNull(),
  formationName: varchar("formationName", { length: 180 }),
  geometry: json("geometry").notNull(),
  source: varchar("source", { length: 180 }).notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
});

export const structures = mysqlTable("structures", {
  id: int("id").autoincrement().primaryKey(),
  villageId: int("villageId"),
  type: varchar("type", { length: 120 }).notNull(),
  geometry: json("geometry").notNull(),
  condition: varchar("condition", { length: 64 }),
  yearBuilt: int("yearBuilt"),
  source: varchar("source", { length: 180 }).notNull(),
  verified: int("verified").default(0).notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
});

export const springs = mysqlTable("springs", {
  id: int("id").autoincrement().primaryKey(),
  clientId: varchar("clientId", { length: 64 }).notNull().unique(),
  villageId: int("villageId").notNull(),
  name: varchar("name", { length: 180 }).notNull(),
  localName: varchar("localName", { length: 180 }),
  location: json("location").notNull(),
  elevationM: int("elevationM"),
  usageTypes: json("usageTypes"),
  estimatedHouseholds: int("estimatedHouseholds").default(0).notNull(),
  baselineStatus: varchar("baselineStatus", { length: 64 }),
  currentStatus: varchar("currentStatus", { length: 64 }),
  priorityScore: int("priorityScore"),
  priorityBand: mysqlEnum("priorityBand", ["low", "medium", "high"]),
  confidence: mysqlEnum("confidence", ["low", "medium", "high"]),
  dataCompleteness: int("dataCompleteness"),
  rechargeLayerRef: varchar("rechargeLayerRef", { length: 180 }),
  approvalStatus: varchar("approvalStatus", { length: 64 }).default("Draft").notNull(),
  createdBy: int("createdBy"),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
});

export const observations = mysqlTable("observations", {
  id: int("id").autoincrement().primaryKey(),
  clientId: varchar("clientId", { length: 64 }).notNull().unique(),
  springId: int("springId").notNull(),
  observedAt: timestamp("observedAt").notNull(),
  dischargeLpm: int("dischargeLpm"),
  waterQualityStatus: varchar("waterQualityStatus", { length: 64 }),
  usersCount: int("usersCount"),
  seasonalStatus: varchar("seasonalStatus", { length: 64 }),
  notes: text("notes"),
  voiceStoragePath: text("voiceStoragePath"),
  photoStoragePaths: json("photoStoragePaths"),
  location: json("location"),
  collectedBy: int("collectedBy"),
  syncState: mysqlEnum("syncState", ["pending", "synced", "failed"]).default("pending").notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
});

export const assessments = mysqlTable("assessments", {
  id: int("id").autoincrement().primaryKey(),
  springId: int("springId").notNull(),
  score: int("score").notNull(),
  factors: json("factors").notNull(),
  reasons: json("reasons").notNull(),
  modelVersion: varchar("modelVersion", { length: 64 }).notNull(),
  inputSnapshot: json("inputSnapshot").notNull(),
  confidence: mysqlEnum("confidence", ["low", "medium", "high"]).notNull(),
  generatedAt: timestamp("generatedAt").defaultNow().notNull(),
  generatedBy: int("generatedBy"),
});

export const recommendations = mysqlTable("recommendations", {
  id: int("id").autoincrement().primaryKey(),
  springId: int("springId").notNull(),
  interventionType: varchar("interventionType", { length: 120 }).notNull(),
  candidateLocation: json("candidateLocation"),
  suitabilityFactors: json("suitabilityFactors"),
  estimatedCostMin: int("estimatedCostMin"),
  estimatedCostMax: int("estimatedCostMax"),
  expectedPlanningBenefit: text("expectedPlanningBenefit"),
  constraints: json("constraints"),
  modelVersion: varchar("modelVersion", { length: 64 }),
  inputSnapshot: json("inputSnapshot"),
  confidence: mysqlEnum("confidence", ["low", "medium", "high"]).notNull(),
  validationStatus: varchar("validationStatus", { length: 64 }).default("Pending").notNull(),
  generatedAt: timestamp("generatedAt").defaultNow().notNull(),
});

export const plans = mysqlTable("plans", {
  id: int("id").autoincrement().primaryKey(),
  springId: int("springId").notNull(),
  selectedRecommendations: json("selectedRecommendations"),
  budgetRange: json("budgetRange"),
  beneficiaries: int("beneficiaries"),
  validationNotes: text("validationNotes"),
  status: varchar("status", { length: 64 }).default("Draft").notNull(),
  reviewedBy: int("reviewedBy"),
  approvedBy: int("approvedBy"),
  rejectionReason: text("rejectionReason"),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
});

export const monitoring = mysqlTable("monitoring", {
  id: int("id").autoincrement().primaryKey(),
  springId: int("springId").notNull(),
  observedAt: timestamp("observedAt").notNull(),
  dischargeLpm: int("dischargeLpm"),
  waterQualityStatus: varchar("waterQualityStatus", { length: 64 }),
  maintenanceStatus: varchar("maintenanceStatus", { length: 64 }),
  photoStoragePaths: json("photoStoragePaths"),
  notes: text("notes"),
  collectedBy: int("collectedBy"),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
});

export const springIssues = mysqlTable("springIssues", {
  id: int("id").autoincrement().primaryKey(),
  clientId: varchar("clientId", { length: 64 }).notNull().unique(),
  springId: int("springId").notNull(),
  issueType: varchar("issueType", { length: 80 }).notNull(),
  description: text("description").notNull(),
  reporterId: int("reporterId"),
  status: mysqlEnum("status", ["open", "reviewing", "resolved"]).default("open").notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
});

export const auditLogs = mysqlTable("auditLogs", {
  id: int("id").autoincrement().primaryKey(),
  actorId: int("actorId"),
  action: varchar("action", { length: 120 }).notNull(),
  entityType: varchar("entityType", { length: 80 }).notNull(),
  entityId: varchar("entityId", { length: 64 }).notNull(),
  before: json("before"),
  after: json("after"),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
});

export const dataSources = mysqlTable("dataSources", {
  id: int("id").autoincrement().primaryKey(),
  source: varchar("source", { length: 120 }).notNull(),
  sourceRecordId: varchar("sourceRecordId", { length: 180 }),
  villageId: int("villageId"),
  fetchedAt: timestamp("fetchedAt").notNull(),
  observedFrom: timestamp("observedFrom"),
  observedTo: timestamp("observedTo"),
  payload: json("payload"),
  artifactPath: text("artifactPath"),
  spatialBounds: json("spatialBounds"),
  processingVersion: varchar("processingVersion", { length: 64 }),
  stale: int("stale").default(0).notNull(),
  lastError: text("lastError"),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
});

export type User = typeof users.$inferSelect;
export type InsertUser = typeof users.$inferInsert;
export type Village = typeof villages.$inferSelect;
export type Spring = typeof springs.$inferSelect;
export type Observation = typeof observations.$inferSelect;
export type Assessment = typeof assessments.$inferSelect;
export type Recommendation = typeof recommendations.$inferSelect;
export type Plan = typeof plans.$inferSelect;
export type SpringIssue = typeof springIssues.$inferSelect;
export type DataSource = typeof dataSources.$inferSelect;
export type GeologicalStructure = typeof geologicalStructures.$inferSelect;
export type Lithology = typeof lithology.$inferSelect;
export type ConservationStructure = typeof structures.$inferSelect;
