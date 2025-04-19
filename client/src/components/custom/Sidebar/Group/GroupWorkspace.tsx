import {
	SidebarMenu,
	SidebarMenuButton,
	SidebarMenuItem,
	SidebarMenuSub,
	SidebarMenuSubButton,
	SidebarMenuSubItem,
} from "@/components/ui/sidebar";
import React from "react";
import {
	Folder,
	FolderKanban,
	Plus,
	Settings,
	Star,
	Users,
} from "lucide-react";
import {
	Collapsible,
	CollapsibleContent,
	CollapsibleTrigger,
} from "@/components/ui/collapsible";
import Icon from "../../Icon";
import {
	Tooltip,
	TooltipContent,
	TooltipTrigger,
} from "@/components/ui/tooltip";
import { TooltipArrow } from "@radix-ui/react-tooltip";

const items = [
	{
		title: "Project Alpha",
		url: "#",
		icon: Folder,
	},
	{
		title: "Beta Initiative",
		url: "#",
		icon: Folder,
	},
	{
		title: "Shared Spaces",
		url: "#",
		icon: Users,
	},
	{
		title: "Favourites",
		url: "#",
		icon: Star,
	},
];

const GroupWorkspace = () => {
	return (
		<SidebarMenu>
			<Collapsible defaultOpen asChild className="group/collapsible">
				<SidebarMenuItem className="cursor-default">
					<CollapsibleTrigger
						asChild
						className="cursor-pointer flex-1 items-start"
					>
						<SidebarMenuButton
							tooltip={{
								children: "Workspace",
								className: "bg-black text-custom-text-primary",
								side: "right",
							}}
							className="flex select-none items-center justify-between gap-2"
						>
							<div className="flex items-center gap-2">
								<Icon
									size={16}
									strokeWidth={2}
									className="font-bold"
									icon={FolderKanban}
								/>
								<p className="text-xs text-left font-semibold translate-y-[1px]">
									Workspace
								</p>
							</div>

							<Tooltip>
								<TooltipTrigger>
									<div className="p-[3px] hover:scale-110 group hover:bg-custom-gray-secondary/30 duration-100 transition-all select-none rounded-md">
										<Icon
											size={16}
											strokeWidth={2}
											className="font-bold group-hover:text-white"
											icon={Plus}
										/>
									</div>
								</TooltipTrigger>
								<TooltipContent
									side="right"
									className="bg-black text-custom-text-primary shadow-md"
								>
									<p className="text-xs">Create New File</p>
									<TooltipArrow className="fill-custom-gray-primary/80 shadow-md" />
								</TooltipContent>
							</Tooltip>
						</SidebarMenuButton>
					</CollapsibleTrigger>

					<CollapsibleContent>
						<SidebarMenuSub>
							{items.map((item) => (
								<SidebarMenuSubItem key={item.title}>
									<SidebarMenuSubButton
										className="select-none cursor-pointer"
										asChild
									>
										<div>
											<Icon icon={item.icon} />
											<span>{item.title}</span>
										</div>
									</SidebarMenuSubButton>
								</SidebarMenuSubItem>
							))}
						</SidebarMenuSub>
					</CollapsibleContent>
				</SidebarMenuItem>
			</Collapsible>
		</SidebarMenu>
	);
};

export default GroupWorkspace;
