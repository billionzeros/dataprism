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
import GroupExtra from "./Group/GroupExtra";
import type React from "react";
import InfoCard from "./InfoCard";
import BaseMenuItem from "./BaseMenuItem";
import { Home, LifeBuoy, Settings } from "lucide-react";

export function AppSidebar() {
	const { open, toggleSidebar } = useSidebar();
	return (
		<Sidebar collapsible="icon" className="bg-custom-background">
			<SidebarHeader className="mb-2">
				<AppSidebarHeader open={open} toggleSidebar={toggleSidebar} />
			</SidebarHeader>

			<SidebarContent
				className={cn(
					"flex flex-col justify-between gap-3",
					!open ? "items-center" : "",
				)}
			>
				<div className="flex flex-col w-full items-center gap-1">
					<BaseMenuItem title="Home" open={open} icon={Home} />
					<div className="px-2 flex items-center w-full flex-col gap-2">
						<GroupWorkspace />
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
