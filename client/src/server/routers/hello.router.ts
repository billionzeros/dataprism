import { publicProcedure, router } from "../trpc";

export const healthRouter = router({
	ping: publicProcedure.query(() => {
		return {
			message: "pong",
		};
	}),
});

export type HealthRouter = typeof healthRouter;
