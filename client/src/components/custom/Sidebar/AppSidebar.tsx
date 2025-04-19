import {
	Sidebar,
	SidebarContent,
	SidebarHeader,
	SidebarRail,
	SidebarSeparator,
	useSidebar,
} from "@/components/ui/sidebar";
import AppSidebarHeader from "./AppSidebarHeader";
import GroupWorkspace from "./Group/GroupWorkspace";
import GroupSources from "./Group/GroupSources";
import { cn } from "@/lib/utils";
import GroupChats from "./Group/GroupChats";
import type React from "react";
import InfoCard from "./InfoCard";
import BaseMenuItem from "./BaseMenuItem";
import { Home, LifeBuoy, Settings } from "lucide-react";
import GroupDocuments from "./Group/GroupDocuments";
import { useRouter } from "next/router";

export function AppSidebar() {
	const router = useRouter();

	const { open, toggleSidebar } = useSidebar();

	return (
		<Sidebar collapsible="icon" className="bg-custom-background">
			<SidebarHeader className="mb-2">
				<AppSidebarHeader open={open} toggleSidebar={toggleSidebar} />
			</SidebarHeader>

			<SidebarContent
				className={cn(
					open
						? "grid grid-rows-[10fr_2fr] gap-2 overflow-hidden"
						: "flex flex-col justify-between gap-3",
				)}
			>
				<div className="flex flex-col w-full items-center overflow-scroll">
					<div className="sticky top-0 w-full bg-custom-background z-50">
						<BaseMenuItem
							onClick={() => {
								router.push("/");
							}}
							title="Home"
							open={open}
							icon={Home}
						/>
						<SidebarSeparator className="my-2 shadow-md" />
					</div>

					<div className="px-2 flex items-center w-full flex-col gap-2">
						{router.pathname.includes("/workspace") ? <GroupDocuments /> : null}
						{router.pathname === "/" ? <GroupWorkspace /> : null}
						<GroupSources />
						<GroupChats />
					</div>
				</div>

				<div className="mb-5">
					<InfoCard sidebarOpen={open} />
					<SidebarSeparator className="my-2" />
					<BaseMenuItem title="Resources" open={open} icon={LifeBuoy} />
					<BaseMenuItem title="Settings" open={open} icon={Settings} />
				</div>
			</SidebarContent>

			<SidebarRail />
		</Sidebar>
	);
}
