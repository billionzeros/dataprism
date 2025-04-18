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
	Bot,
	MessageCircle,
	MessagesSquare,
	Plus,
	Settings,
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
		title: "Chat with Prism AI",
		url: "#",
		icon: <Icon icon={Bot} strokeWidth={2} size={14} />,
	},
	{
		title: "Team Sync",
		url: "#",
		icon: <Icon icon={Users} strokeWidth={2} size={14} />,
	},
	{
		title: "General Discussion",
		url: "#",
		icon: <Icon icon={MessageCircle} strokeWidth={2} size={14} />,
	},
];

const GroupChats = () => {
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
								children: "Prism Chats",
								className: "bg-custom-gray-primary text-custom-gray-secondary",
							}}
							className="flex items-center justify-between gap-2"
						>
							<div className="flex items-center gap-2">
								<Icon
									size={16}
									strokeWidth={2}
									className="font-bold"
									icon={MessagesSquare}
								/>
								<p className="text-xs text-left font-medium translate-y-[1px]">
									Chats
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
								<TooltipContent className="bg-custom-gray-primary shadow-md">
									<p className="text-xs">Talk to Prism</p>
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

export default GroupChats;
