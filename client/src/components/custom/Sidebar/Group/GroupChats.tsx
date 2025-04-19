import {
	SidebarMenu,
	SidebarMenuButton,
	SidebarMenuItem,
	SidebarMenuSub,
	SidebarMenuSubButton,
	SidebarMenuSubItem,
	useSidebar,
} from "@/components/ui/sidebar";
import React, { useState } from "react";
import {
	Bot,
	ChevronDown,
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
import { cn } from "@/lib/utils";

const items = [
	{
		title: "Chat with Prism AI",
		url: "#",
		icon: Bot,
	},
	{
		title: "Team Sync",
		url: "#",
		icon: Users,
	},
	{
		title: "General Discussion",
		url: "#",
		icon: MessageCircle,
	},
];

const GroupChats = () => {
	const [collapseOpen, setCollapseOpen] = useState(true);
	const { open: sidebarOpen, setOpen } = useSidebar();

	const handleOpen = () => {
		if (!sidebarOpen) {
			setOpen(true);

			if (!collapseOpen) {
				setCollapseOpen(true);
			}
		}
	};

	const toggleCollapse = () => {
		if (sidebarOpen) {
			setCollapseOpen((prev) => !prev);
		}
	};

	return (
		<SidebarMenu>
			<Collapsible open={collapseOpen} asChild className="group/collapsible">
				<SidebarMenuItem className="cursor-default">
					<SidebarMenuButton
						tooltip={{
							children: "Prism Chats",
							className: "bg-black text-custom-text-primary",
							side: "right",
						}}
						onClick={handleOpen}
						className="flex select-none items-center justify-between gap-2"
					>
						<CollapsibleTrigger
							asChild
							className="cursor-pointer flex-1 items-start"
							onClick={toggleCollapse}
						>
							<div className="flex items-center justify-between ">
								<div className="flex items-center gap-2">
									<Icon
										size={16}
										strokeWidth={2}
										className="font-bold"
										icon={MessagesSquare}
									/>
									<p className="text-xs text-left font-semibold translate-y-[1px]">
										Chats
									</p>
								</div>
								<SidebarMenuSubItem>
									<Tooltip>
										<TooltipTrigger asChild>
											<div className="hover:text-custom-text-primary hover:scale-110 duration-150 transition-all ease-in-out hover:bg-custom-gray-secondary/40 rounded-md aspect-video p-[4px]">
												<Icon
													className="cursor-pointer"
													icon={Plus}
													size={14}
													strokeWidth={3}
												/>
											</div>
										</TooltipTrigger>
										<TooltipContent side="right">
											<span>New Chat</span>
										</TooltipContent>
									</Tooltip>
								</SidebarMenuSubItem>
							</div>
						</CollapsibleTrigger>
					</SidebarMenuButton>

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

export default GroupChats;
