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
import GroupChats from "./Group/GroupChats";
import GroupExtra from "./Group/GroupExtra";
import Icon from "../Icon";
import { ArrowRight, X } from "lucide-react";
import { useState } from "react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

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
					<div className="px-2 flex items-center w-full flex-col gap-2">
						<GroupWorkspace />
						<GroupSources />
						<GroupChats />
					</div>
				</div>

				<div className="mb-5">
					<InfoCard />
					<SidebarSeparator className="my-2" />
					<GroupExtra open={open} />
				</div>
			</SidebarContent>

			<SidebarRail />
		</Sidebar>
	);
}

const InfoCard = () => {
	const [open, setOpen] = useState(true);

	if (!open) {
		return null;
	}

	return (
		<div className="border-[2px] border-custom-gray-primary m-2 p-3 rounded-md flex flex-col gap-1 shadow-md">
			<div className="flex items-center justify-between">
				<div className="text-sm text-custom-text-primary/80 mb-[3px] font-bold font-inter select-none cursor-default">
					Prism AI
				</div>

				<Icon
					className="hover:bg-custom-gray-primary aspect-square p-[2px] shadow-md rounded-sm cursor-pointer transition-all duration-200 ease-in-out"
					size={18}
					icon={X}
					onClick={() => setOpen(false)}
					aria-label="Close"
					aria-hidden="true"
					aria-controls="info-card"
					aria-expanded={open}
				/>
			</div>
			<p className="text-xs text-custom-gray-secondary font-inter select-none cursor-default">
				Built to make <u>data talk to you</u> !! <br /> <br /> Ask Questions,
				and keep your conversations with LLMs organised.
			</p>
			<div className="text-custom-text-primary/80 cursor-pointer hover:text-custom-text-primary group flex items-center gap-1 text-xs font-bold font-inter mt-2">
				<span>Unlock Potential</span>
				<Icon
					className="text-custom-text-primary/80 group-hover:text-custom-text-primary"
					size={12}
					icon={ArrowRight}
				/>
			</div>
		</div>
	);
};
