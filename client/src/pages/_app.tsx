import type { AppType } from "next/app";
import { Inter } from "next/font/google";
import { api } from "../utils/trpc";

import "@/styles/globals.css";

const inter = Inter({
	style: ["normal"],
	preload: true,
	variable: "--font-inter",
});

const MyApp: AppType = ({ Component, pageProps }) => {
	return (
		<div className={`${inter.variable} font-inter`}>
			<Component {...pageProps} />
		</div>
	);
};

export default api.withTRPC(MyApp);
