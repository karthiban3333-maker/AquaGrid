/**
 * Unified type exports
 * Import shared types from this single entry point.
 */

export type * from "../drizzle/schema";
export * from "./_core/errors";

export type GeoJsonGeometry = { type: "Polygon" | "LineString" | "MultiPolygon"; coordinates: unknown };
export type GeoJsonFeature = { type: "Feature"; properties: Record<string, unknown>; geometry: GeoJsonGeometry };
export type GeoJsonFeatureCollection = { type: "FeatureCollection"; features: GeoJsonFeature[]; modelVersion?: string; caveat?: string };
export type SpringshedResponse = { catchment: GeoJsonFeature; streamNetwork: GeoJsonFeatureCollection; flowAccumulation: number[][]; flowDirection: number[][]; metadata: Record<string, unknown> };
export type PrioritySurfaceResponse = GeoJsonFeatureCollection;
export type LiveEvidenceResponse = { status: string; fetchedAt: string; coordinates: { lat: number; lng: number }; weather?: Record<string, unknown>; sentinel2?: Record<string, unknown>; uncertainty: string };
