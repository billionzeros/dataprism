import { publicProcedure, router } from "../trpc";
import { createDocumentInput, createDocumentResponse } from "./schema/schema";

export const documentRouter = router({
	create: publicProcedure
		.input(createDocumentInput)
		.output(createDocumentResponse)
		.query(() => {
			return {
				documentId: "123",
				title: "My Document",
			};
		}),
});

export type DocumentRouter = typeof documentRouter;
