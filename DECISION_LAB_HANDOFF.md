# Decision Lab integration

The existing Action plans route now hosts the integrated spring-revival decision workflow. It preserves the existing satellite map, navigation and visual language.

The workflow includes Recharge Trace, Why This Area, Simulate Revival, Risk & Avoidance, Spring Fingerprint and Verify in Field. Prototype calculations reuse the selected spring's existing decline, readings, confidence, households, use, elevation and priority fields. All inferred values are labeled as prototype/demo or indicative and do not claim an exact groundwater route or guaranteed discharge increase.

Field verification submits through the protected `fieldVerification.submit` tRPC procedure when connected authentication and a database are available. It writes to the existing `observations` table and retains `clientId` for idempotent offline sync. The UI still confirms local capture when the demo auth/database is unavailable. Photo selection is currently a UI placeholder; production should upload the image to private storage first and pass only its storage path to the procedure.

The existing relational schema already includes `springs`, `observations`, `assessments`, `recommendations`, `plans`, `monitoring` and `auditLogs`, so no parallel database was introduced.
