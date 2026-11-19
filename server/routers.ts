import { z } from "zod";
import { COOKIE_NAME } from "@shared/const";
import { getSessionCookieOptions } from "./_core/cookies";
import { systemRouter } from "./_core/systemRouter";
import { protectedProcedure, publicProcedure, router } from "./_core/trpc";
import { createFieldObservation, createSpringIssue } from "./db";
import { predictAndPersist, rankInterventions, refreshVillageSources } from "./geoEngine";

export const appRouter = router({
  system: systemRouter,
  auth: router({
    me: publicProcedure.query(opts => opts.ctx.user),
    logout: publicProcedure.mutation(({ ctx }) => {
      const cookieOptions = getSessionCookieOptions(ctx.req);
      ctx.res.clearCookie(COOKIE_NAME, { ...cookieOptions, maxAge: -1 });
      return { success: true } as const;
    }),
  }),
  fieldVerification: router({
    submit: protectedProcedure.input(z.object({
      clientId: z.string().min(8).max(64),
      springId: z.number().int().positive(),
      observedAt: z.coerce.date(),
      dischargeLpm: z.number().nonnegative().optional(),
      waterPresence: z.enum(["present", "low", "none"]),
      groundCondition: z.enum(["stable", "eroded", "saturated"]),
      interventionStatus: z.enum(["not_started", "in_progress", "completed"]),
      notes: z.string().max(4000).optional(),
      photoStoragePaths: z.array(z.string().max(500)).max(5).optional(),
      location: z.object({ lat: z.number(), lng: z.number(), accuracyM: z.number().nonnegative().optional() }).optional(),
    })).mutation(async ({ ctx, input }) => createFieldObservation({
      ...input,
      waterQualityStatus: input.waterPresence,
      seasonalStatus: `${input.groundCondition}:${input.interventionStatus}`,
      collectedBy: ctx.user.id,
    })),
  }),
  springIssues: router({
    // Demo visitors use the local role selector before Firebase Auth is connected.
    // Replace with protectedProcedure plus a visitor custom-claim check in production.
    submit: publicProcedure.input(z.object({
      clientId: z.string().min(8).max(64),
      springId: z.number().int().positive(),
      issueType: z.enum(["water_flow", "access", "pollution", "damage", "other"]),
      description: z.string().min(3).max(4000),
    })).mutation(({ input }) => createSpringIssue(input)),
  }),
  geoData: router({
    refreshVillage: protectedProcedure.input(z.object({
      villageId: z.string().min(1).max(180),
      polygon: z.array(z.array(z.number())).min(3).optional(),
      bounds: z.record(z.string(), z.number()).optional(),
      centroid: z.object({ lat: z.number(), lng: z.number() }).optional(),
      startDate: z.string().optional(),
      endDate: z.string().optional(),
    })).mutation(({ input }) => refreshVillageSources(input)),
    predictRecharge: protectedProcedure.input(z.object({
      springId: z.number().int().positive(),
      trainingSamples: z.array(z.record(z.string(), z.unknown())).min(4),
      predictionGrid: z.array(z.record(z.string(), z.unknown())).min(1),
    })).mutation(({ input }) => predictAndPersist(input)),
    rankInterventions: protectedProcedure.input(z.object({
      springId: z.number().int().positive(),
      sites: z.array(z.record(z.string(), z.unknown())).min(1),
    })).mutation(({ input }) => rankInterventions(input)),
  }),
});

export type AppRouter = typeof appRouter;
