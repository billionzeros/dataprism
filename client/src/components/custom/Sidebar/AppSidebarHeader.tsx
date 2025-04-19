import {
	SidebarMenu,
	SidebarMenuItem,
	SidebarMenuButton, // Import SidebarMenuButton
} from "@/components/ui/sidebar";
import { Command, PanelRightClose, PanelRightOpen } from "lucide-react";
import type React from "react";
import Icon from "../Icon";
import { cn } from "@/lib/utils"; // Import cn
import { Tooltip } from "@radix-ui/react-tooltip";
import { TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";

type SidebarHeaderProps = {
	open: boolean;
	toggleSidebar: () => void;
};

const AppSidebarHeader: React.FC<SidebarHeaderProps> = ({
	open,
	toggleSidebar,
}) => {
	return (
		<SidebarMenu className="bg-none pt-2">
			<SidebarMenuItem className="bg-none p-0 flex items-center justify-between">
				<div
					className={cn(
						"flex items-center gap-2",
						!open && "w-full justify-center",
					)}
				>
					<div
						className={cn(
							"flex aspect-square items-center justify-center rounded-lg text-sidebar-primary-foreground",
							"bg-custom-gray-primary/60 p-[6px] cursor-pointer",
							"hover:bg-custom-gray-primary/80",
							"transition-colors duration-200 ease-in-out",
							"shadow-md",
							"hover:scale-110",
							"translate-x-[1px]",
						)}
					>
						<Icon icon={Command} size={17} />
					</div>
					{open && (
						<span className="translate-y-[1px] select-none text-base font-semibold">
							Prism
						</span>
					)}
				</div>
				{open && (
					<SidebarMenuButton
						className="w-fit hover:bg-sidebar-accent"
						onClick={toggleSidebar}
						tooltip={{
							children: "Toggle Sidebar",
							className: "bg-black text-custom-text-primary",
							side: "right",
						}}
					>
						<Icon
							size={2}
							strokeWidth={2}
							icon={PanelRightOpen}
							className="text-sidebar-foreground hover:text-sidebar-accent-foreground"
						/>
						<span className="sr-only">Toggle Sidebar</span>
					</SidebarMenuButton>
				)}
			</SidebarMenuItem>
		</SidebarMenu>
	);
};

export default AppSidebarHeader;
