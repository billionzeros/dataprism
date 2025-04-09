import { router } from "../trpc";
import { healthRouter } from "./hello.router";

export const appRouter = router({
	health: healthRouter,
});

export type AppRouter = typeof appRouter;
