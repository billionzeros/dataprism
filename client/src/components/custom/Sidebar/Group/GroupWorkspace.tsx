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
		icon: <Icon icon={Folder} strokeWidth={2} size={14} />,
	},
	{
		title: "Beta Initiative",
		url: "#",
		icon: <Icon icon={Folder} strokeWidth={2} size={14} />,
	},
	{
		title: "Shared Spaces",
		url: "#",
		icon: <Icon icon={Users} strokeWidth={2} size={14} />,
	},
	{
		title: "Favourites",
		url: "#",
		icon: <Icon icon={Star} strokeWidth={2} size={14} />,
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
								className:
									"bg-custom-gray-primary text-custom-gray-secondary/80",
							}}
							className="flex items-center justify-between gap-2"
						>
							<div className="flex items-center gap-2">
								<Icon
									size={16}
									strokeWidth={2}
									className="font-bold"
									icon={FolderKanban}
								/>
								<p className="text-xs text-left font-medium translate-y-[1px]">
									Workspace
								</p>
							</div>

							<Tooltip>
								<TooltipTrigger>
									<div className="p-[3px] hover:scale-110 group hover:bg-custom-gray-primar duration-100 transition-all select-none rounded-md">
										<Icon
											size={16}
											strokeWidth={2}
											className="font-bold group-hover:text-white"
											icon={Plus}
										/>
									</div>
								</TooltipTrigger>
								<TooltipContent className="bg-custom-gray-primary shadow-md">
									<p className="text-xs">Create new workspace</p>
									<TooltipArrow className="fill-custom-gray-primary/80 shadow-md" />
								</TooltipContent>
							</Tooltip>
						</SidebarMenuButton>
					</CollapsibleTrigger>

					<CollapsibleContent>
						<SidebarMenuSub>
							{items.map((item) => (
								<SidebarMenuSubItem key={item.title}>
									<SidebarMenuSubButton asChild>
										<a href={item.url}>
											{item.icon}
											<span>{item.title}</span>
										</a>
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
