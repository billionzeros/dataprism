import {
	Sidebar,
	SidebarContent,
	SidebarHeader,
	SidebarMenu,
	SidebarMenuButton,
	SidebarMenuItem,
	SidebarRail,
	SidebarSeparator,
	useSidebar,
} from "@/components/ui/sidebar";
import AppSidebarHeader from "./AppSidebarHeader";
import GroupWorkspace from "./Group/GroupWorkspace";
import GroupSources from "./Group/GroupSources";
import { cn } from "@/lib/utils";
import GroupNewBlock from "./Group/GroupNewBlock";
import GroupFork from "./Group/GroupFork";
import GroupChats from "./Group/GroupChats";
import { LifeBuoy, Settings } from "lucide-react";
import Icon from "../Icon";
import GroupExtra from "./Group/GroupExtra";

// Menu items.

export function AppSidebar() {
	const { open, toggleSidebar } = useSidebar();
	return (
		<Sidebar collapsible="icon" className="bg-custom-background">
			<SidebarHeader>
				<AppSidebarHeader open={open} toggleSidebar={toggleSidebar} />
			</SidebarHeader>
			<SidebarContent
				className={cn(
					"flex flex-col justify-between gap-3",
					!open ? "items-center" : "",
				)}
			>
				<div className="flex flex-col w-full items-center gap-3">
					<GroupNewBlock open={open} />
					<div className="px-2 flex items-center w-full flex-col gap-2">
						<GroupWorkspace />
						<GroupSources />
						<GroupChats />
						<GroupFork />
					</div>
				</div>

				<div className="mb-20">
					<GroupExtra open={open} />
				</div>
			</SidebarContent>

			<SidebarRail />
		</Sidebar>
	);
}
