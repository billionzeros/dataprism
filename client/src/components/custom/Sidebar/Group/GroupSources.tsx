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
	ChevronDown,
	Database,
	DatabaseZap,
	FileText,
	Network,
	Plus,
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
							children: "Sources",
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
										icon={DatabaseZap}
									/>
									<p className="text-xs text-left font-semibold translate-y-[1px]">
										Sources
									</p>
								</div>
								<div>
									<Icon
										className={cn(
											!collapseOpen
												? "-rotate-90 translate-y-[1px] duration-200 transition-all ease-in-out"
												: "duration-200 translate-y-[1px] ease-in-out",
										)}
										size={14}
										icon={ChevronDown}
									/>
								</div>
							</div>
						</CollapsibleTrigger>
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
