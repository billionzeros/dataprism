import type { AppType } from "next/app";
import { Inter } from "next/font/google";
import { api } from "../utils/trpc";
import { Toaster } from "@/components/ui/toaster";

import "@/styles/globals.css";
import { SidebarProvider } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/custom/Sidebar/AppSidebar";
import { TooltipProvider } from "@/components/ui/tooltip";

const inter = Inter({
	style: ["normal"],
	preload: false,
	variable: "--font-inter",
});

const MyApp: AppType = ({ Component, pageProps }) => {
	return (
		<div className={`${inter.variable} font-inter w-full h-full`}>
			<SidebarProvider>
				<TooltipProvider>
					<AppSidebar />
					<div className="w-full">
						<Component {...pageProps} />
					</div>
				</TooltipProvider>
			</SidebarProvider>
			<Toaster />
		</div>
	);
};

export default api.withTRPC(MyApp);
