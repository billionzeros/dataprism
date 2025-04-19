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
	ArrowDown,
	ChevronDown,
	Folder,
	FolderKanban,
	Leaf,
	Plus,
	Star,
	Users,
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
		title: "Energy Sector",
		projectId: "abcd-1234",
		icon: Leaf,
	},
	{
		title: "Project Alpha",
		projectId: "efgh-5678",
		icon: Folder,
	},
	{
		title: "Beta Initiative",
		projectId: "ijkl-9101",
		icon: Folder,
	},
	{
		title: "Shared Spaces",
		projectId: "mnop-1121",
		icon: Users,
	},
	{
		title: "Favourites",
		projectId: "qrst-3141",
		icon: Star,
	},
];

const GroupWorkspace = () => {
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
							children: "Workspaces",
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
										icon={FolderKanban}
									/>
									<p className="text-xs text-left font-semibold translate-y-[1px]">
										Workspaces
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
											<span>New Workspace</span>
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
										router.push(`/workspace/${item.projectId}`);
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

export default GroupWorkspace;
