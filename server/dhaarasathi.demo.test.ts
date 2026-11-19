import { describe, expect, it } from "vitest";
import { springs } from "../client/src/pages/Home";

describe("DhaaraSathi demo contract", () => {
  it("ships a varied pilot dataset with high-priority and healthy springs", () => {
    expect(springs.length).toBeGreaterThanOrEqual(8);
    expect(springs.some((spring) => spring.priority === "High")).toBe(true);
    expect(springs.some((spring) => spring.priority === "Low")).toBe(true);
    expect(springs.every((spring) => spring.id && spring.village && spring.localName)).toBe(true);
  });

  it("includes sample satellite evidence metadata for every spring", () => {
    expect(springs.every((spring) => spring.satelliteScene.startsWith("S2A_"))).toBe(true);
    expect(springs.every((spring) => spring.cloudCover >= 0 && spring.cloudCover <= 100)).toBe(true);
    expect(springs.every((spring) => Number(spring.ndvi) >= -1 && Number(spring.ndvi) <= 1)).toBe(true);
    expect(springs.every((spring) => Number(spring.ndwi) >= -1 && Number(spring.ndwi) <= 1)).toBe(true);
  });

  it("keeps low-confidence evidence explicit instead of treating it as healthy", () => {
    const lowConfidence = springs.find((spring) => spring.confidence === "Low");
    expect(lowConfidence).toBeDefined();
    expect(lowConfidence?.readings).toHaveLength(0);
    expect(lowConfidence?.reasons.some((reason) => reason.toLowerCase().includes("no discharge"))).toBe(true);
    expect(lowConfidence?.lastObserved).toMatch(/awaiting/i);
  });

  it("uses a workflow state that is safe for a human approval handoff", () => {
    expect(springs.some((spring) => spring.status === "Technical Validated")).toBe(true);
    expect(springs.some((spring) => spring.status === "Officer Approved")).toBe(true);
    expect(springs.some((spring) => spring.status === "Monitoring")).toBe(true);
  });
});
