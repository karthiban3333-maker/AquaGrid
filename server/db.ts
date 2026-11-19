import { and, desc, eq } from "drizzle-orm";
import { drizzle } from "drizzle-orm/mysql2";
import { InsertUser, assessments, dataSources, observations, recommendations, springIssues, users } from "../drizzle/schema";
import { ENV } from './_core/env';

let _db: ReturnType<typeof drizzle> | null = null;

export async function getDb() {
  if (!_db && process.env.DATABASE_URL) {
    try {
      _db = drizzle(process.env.DATABASE_URL);
    } catch (error) {
      console.warn("[Database] Failed to connect:", error);
      _db = null;
    }
  }
  return _db;
}

export async function upsertUser(user: InsertUser): Promise<void> {
  if (!user.openId) throw new Error("User openId is required for upsert");
  const db = await getDb();
  if (!db) { console.warn("[Database] Cannot upsert user: database not available"); return; }
  try {
    const values: InsertUser = { openId: user.openId };
    const updateSet: Record<string, unknown> = {};
    const textFields = ["name", "email", "loginMethod"] as const;
    type TextField = (typeof textFields)[number];
    const assignNullable = (field: TextField) => {
      const value = user[field];
      if (value === undefined) return;
      const normalized = value ?? null;
      values[field] = normalized;
      updateSet[field] = normalized;
    };
    textFields.forEach(assignNullable);
    if (user.lastSignedIn !== undefined) { values.lastSignedIn = user.lastSignedIn; updateSet.lastSignedIn = user.lastSignedIn; }
    if (user.role !== undefined) { values.role = user.role; updateSet.role = user.role; }
    else if (user.openId === ENV.ownerOpenId) { values.role = 'admin'; updateSet.role = 'admin'; }
    if (!values.lastSignedIn) values.lastSignedIn = new Date();
    if (Object.keys(updateSet).length === 0) updateSet.lastSignedIn = new Date();
    await db.insert(users).values(values).onDuplicateKeyUpdate({ set: updateSet });
  } catch (error) {
    console.error("[Database] Failed to upsert user:", error);
    throw error;
  }
}

export async function getUserByOpenId(openId: string) {
  const db = await getDb();
  if (!db) return undefined;
  const result = await db.select().from(users).where(eq(users.openId, openId)).limit(1);
  return result.length > 0 ? result[0] : undefined;
}

export async function createFieldObservation(input: {
  clientId: string;
  springId: number;
  observedAt: Date;
  dischargeLpm?: number;
  waterQualityStatus?: string;
  seasonalStatus?: string;
  notes?: string;
  photoStoragePaths?: string[];
  location?: { lat: number; lng: number; accuracyM?: number };
  collectedBy?: number;
}) {
  const db = await getDb();
  if (!db) return { persisted: false, reason: "DATABASE_UNAVAILABLE" as const };
  await db.insert(observations).values({
    clientId: input.clientId,
    springId: input.springId,
    observedAt: input.observedAt,
    dischargeLpm: input.dischargeLpm,
    waterQualityStatus: input.waterQualityStatus,
    seasonalStatus: input.seasonalStatus,
    notes: input.notes,
    photoStoragePaths: input.photoStoragePaths,
    location: input.location,
    collectedBy: input.collectedBy,
    syncState: "pending",
  }).onDuplicateKeyUpdate({ set: { notes: input.notes, syncState: "pending" } });
  return { persisted: true } as const;
}

export async function createSpringIssue(input: {
  clientId: string;
  springId: number;
  issueType: string;
  description: string;
  reporterId?: number;
}) {
  const db = await getDb();
  if (!db) return { persisted: false, reason: "DATABASE_UNAVAILABLE" as const };
  await db.insert(springIssues).values({
    clientId: input.clientId,
    springId: input.springId,
    issueType: input.issueType,
    description: input.description,
    reporterId: input.reporterId,
    status: "open",
  }).onDuplicateKeyUpdate({ set: { description: input.description, issueType: input.issueType } });
  return { persisted: true } as const;
}

export async function persistDataSourceResult(input: {
  source: string;
  villageId?: number;
  result: { fetchedAt?: string; stale?: boolean; payload?: unknown; error?: string; sourceRecordId?: string };
}) {
  const db = await getDb();
  if (!db) return { persisted: false, reason: "DATABASE_UNAVAILABLE" as const };
  const previous = input.villageId === undefined ? [] : await db.select().from(dataSources)
    .where(and(eq(dataSources.source, input.source), eq(dataSources.villageId, input.villageId)))
    .orderBy(desc(dataSources.fetchedAt)).limit(1);
  const lastGood = previous.find((row) => row.stale === 0 && row.payload != null);
  const isStale = Boolean(input.result.stale);
  await db.insert(dataSources).values({
    source: input.source,
    sourceRecordId: input.result.sourceRecordId,
    villageId: input.villageId,
    fetchedAt: input.result.fetchedAt ? new Date(input.result.fetchedAt) : new Date(),
    payload: isStale ? lastGood?.payload ?? input.result.payload ?? null : input.result.payload ?? null,
    processingVersion: "phase1-etl-v0.1",
    stale: isStale ? 1 : 0,
    lastError: input.result.error,
  });
  return { persisted: true, stale: isStale, usedLastGoodValue: isStale && Boolean(lastGood) } as const;
}

export async function persistAssessment(input: { springId: number; score: number; factors: unknown; reasons: unknown; modelVersion: string; inputSnapshot: unknown; confidence: "low" | "medium" | "high" }) {
  const db = await getDb();
  if (!db) return { persisted: false, reason: "DATABASE_UNAVAILABLE" as const };
  await db.insert(assessments).values(input);
  return { persisted: true } as const;
}

export async function persistRecommendations(springId: number, result: { modelVersion?: string; sites?: Array<Record<string, any>>; inputSnapshot?: unknown }) {
  const db = await getDb();
  if (!db) return { persisted: false, reason: "DATABASE_UNAVAILABLE" as const };
  for (const site of result.sites ?? []) {
    await db.insert(recommendations).values({
      springId,
      interventionType: String(site.interventionType ?? "field validation required"),
      candidateLocation: site.location ?? null,
      suitabilityFactors: site,
      estimatedCostMin: site.estimatedCostMin,
      estimatedCostMax: site.estimatedCostMax,
      expectedPlanningBenefit: "Indicative planning benefit; field validation required.",
      constraints: site.riskFlags ?? [],
      modelVersion: result.modelVersion,
      inputSnapshot: result.inputSnapshot ?? site,
      confidence: site.confidence === "high" ? "high" : site.confidence === "medium" ? "medium" : "low",
    });
  }
  return { persisted: true, count: result.sites?.length ?? 0 } as const;
}
