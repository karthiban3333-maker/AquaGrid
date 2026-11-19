import { persistAssessment, persistDataSourceResult, persistRecommendations } from "./db";

const GEO_ENGINE_URL = process.env.GEO_ENGINE_URL ?? "http://127.0.0.1:8000";

async function postGeoEngine(path: string, body: unknown) {
  const response = await fetch(`${GEO_ENGINE_URL}${path}`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) throw new Error(`Geo-engine returned ${response.status}`);
  return response.json() as Promise<Record<string, unknown>>;
}

export type VillageRefreshInput = {
  villageId: string;
  polygon?: number[][];
  bounds?: Record<string, number>;
  centroid?: { lat: number; lng: number };
  startDate?: string;
  endDate?: string;
};

export async function refreshVillageSources(input: VillageRefreshInput) {
  const result = await postGeoEngine(`/etl/village/${encodeURIComponent(input.villageId)}/refresh`, {
      village_id: input.villageId,
      polygon: input.polygon,
      bounds: input.bounds,
      centroid: input.centroid,
      start_date: input.startDate,
      end_date: input.endDate,
    });
  const sourceResults = ["sentinel-2", "chirps", "dem"] as const;
  const persisted = await Promise.all(sourceResults.map((source) => persistDataSourceResult({
    source,
    result: (result[source] ?? { stale: true, error: "Source missing from geo-engine response" }) as { fetchedAt?: string; stale?: boolean; payload?: unknown; error?: string; sourceRecordId?: string },
  })));
  return { villageId: input.villageId, sources: result, persisted };
}

export function predictRecharge(input: { trainingSamples: Record<string, unknown>[]; predictionGrid: Record<string, unknown>[] }) {
  return postGeoEngine("/predict-recharge", { training_samples: input.trainingSamples, prediction_grid: input.predictionGrid });
}

export async function rankInterventions(input: { springId: number; sites: Record<string, unknown>[] }) {
  const result = await postGeoEngine("/suitability/interventions", { sites: input.sites });
  const persisted = await persistRecommendations(input.springId, { ...result, inputSnapshot: input.sites });
  return { ...result, persisted };
}

export async function predictAndPersist(input: { springId: number; trainingSamples: Record<string, unknown>[]; predictionGrid: Record<string, unknown>[] }) {
  const result = await predictRecharge(input);
  const firstProbability = Number((result.probability as number[] | undefined)?.[0] ?? 0);
  const persisted = await persistAssessment({
    springId: input.springId,
    score: Math.round(firstProbability * 100),
    factors: result.topFeatureContributions ?? [],
    reasons: ["Model trained on limited pilot data; field validation required."],
    modelVersion: String(result.modelVersion ?? "phase3-unknown"),
    inputSnapshot: input,
    confidence: firstProbability >= 0.7 ? "medium" : "low",
  });
  return { ...result, persisted };
}
