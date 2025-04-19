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
	ChartNoAxesColumnDecreasingIcon,
	ChartNoAxesColumnIncreasing,
	ChevronDown,
	File,
	Files,
	Plus,
} from "lucide-react";
import {
	Collapsible,
	CollapsibleContent,
	CollapsibleTrigger,
} from "@/components/ui/collapsible";
import Icon from "../../Icon";
import { cn } from "@/lib/utils";
import { useRouter } from "next/router";
import {
	Tooltip,
	TooltipContent,
	TooltipTrigger,
} from "@/components/ui/tooltip";

const items = [
	{
		title: "Daily Active Users",
		pageId: "daily-active-users-lmno-789",
		icon: ChartNoAxesColumnIncreasing,
	},
	{
		title: "Investors Report",
		pageId: "investors-report-abcd-123",
		icon: ChartNoAxesColumnDecreasingIcon,
	},
	{
		title: "Daily Analytics",
		pageId: "daily-analytics-efgh-456",
		icon: File,
	},
];

const GroupDocuments = () => {
	const router = useRouter();

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
							children: "Documents",
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
										icon={Files}
									/>
									<p className="text-xs text-left font-semibold translate-y-[1px]">
										Documents
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
											<span>New Document</span>
										</TooltipContent>
									</Tooltip>
								</SidebarMenuSubItem>
							</div>
						</CollapsibleTrigger>
					</SidebarMenuButton>

					<CollapsibleContent>
						<SidebarMenuSub>
							{items.map((item) => (
								<SidebarMenuSubItem
									onClick={() => {
										router.push(`/workspace/page/${item.pageId}`);
									}}
									key={item.title}
								>
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

export default GroupDocuments;
