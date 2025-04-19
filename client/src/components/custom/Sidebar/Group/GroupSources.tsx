import {
	SidebarMenu,
	SidebarMenuButton,
	SidebarMenuItem,
	SidebarMenuSub,
	SidebarMenuSubButton,
	SidebarMenuSubItem,
} from "@/components/ui/sidebar";
import React from "react";
import { Database, DatabaseZap, FileText, Network, Plus } from "lucide-react";
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
		title: "Primary DB",
		url: "#",
		icon: Database,
	},
	{
		title: "Analytics API",
		url: "#",
		icon: Network,
	},
	{
		title: "Uploaded Docs",
		url: "#",
		icon: FileText,
	},
];

const GroupSources = () => {
	return (
		<SidebarMenu>
			<Collapsible defaultOpen asChild className="group/collapsible">
				<SidebarMenuItem className="cursor-default">
					<SidebarMenuButton
						tooltip={{
							children: "Sources",
							className: "bg-black text-custom-text-primary",
							side: "right",
						}}
						className="flex select-none items-center justify-between gap-2"
					>
						<CollapsibleTrigger
							asChild
							className="cursor-pointer flex-1 items-start"
						>
							<div className="flex items-center gap-2">
								<Icon
									size={17}
									strokeWidth={2}
									className="font-bold"
									icon={DatabaseZap}
								/>
								<p className="text-xs text-left font-semibold translate-y-[1px]">
									Sources
								</p>
							</div>
						</CollapsibleTrigger>
						{/* <Tooltip>
							<TooltipTrigger>
								<div className="p-[3px] hover:scale-110 group hover:bg-custom-gray-secondary/30 duration-100 transition-all select-none rounded-md">
									<Icon
										size={18}
										strokeWidth={2}
										className="font-bold group-hover:text-white"
										icon={Plus}
									/>
								</div>
							</TooltipTrigger>
							<TooltipContent side="right" className="bg-black shadow-md">
								<p className="text-xs">Talk to Prism</p>
							</TooltipContent>
						</Tooltip> */}
					</SidebarMenuButton>

					<CollapsibleContent>
						<SidebarMenuSub>
							{items.map((item) => (
								<SidebarMenuSubItem
									className="select-none cursor-pointer"
									key={item.title}
								>
									<SidebarMenuSubButton asChild>
										<div>
											<Icon className="font-bold" icon={item.icon} />
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

export default GroupSources;
