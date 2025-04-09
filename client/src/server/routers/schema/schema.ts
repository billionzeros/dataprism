import { z } from "zod";

// --- Create Document ----
export const createDocumentInput = z.object({
	title: z.string().default(""),
});

export type CreateDocumentInput = z.infer<typeof createDocumentInput>;

export const createDocumentResponse = z.object({
	documentId: z.string(),
	title: z.string(),
});
export type CreateDocumentResponse = z.infer<typeof createDocumentResponse>;

// ------------------------
