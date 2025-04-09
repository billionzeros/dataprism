import { initTRPC } from "@trpc/server";

const t = initTRPC.create();

export const router = t.router;

// This is Public Procedure, using which everyone can access the APIs
export const publicProcedure = t.procedure;
