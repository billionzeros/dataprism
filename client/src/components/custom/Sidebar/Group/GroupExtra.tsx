import {
	SidebarMenu,
	SidebarMenuButton,
	SidebarMenuItem,
} from "@/components/ui/sidebar";
import { cn } from "@/lib/utils";
import { LifeBuoy, Settings } from "lucide-react";
import type React from "react";
import Icon from "../../Icon";

type GroupExtraProps = {
	open: boolean;
};

const GroupExtra: React.FC<GroupExtraProps> = ({ open }) => {
	return (
		<SidebarMenu
			className={cn(
				!open ? "items-center flex flex-col gap-2" : "flex flex-col gap-1 px-2",
			)}
		>
			<SidebarMenuItem>
				<SidebarMenuButton
					className="flex cursor-pointer items-center gap-2"
					tooltip={
						!open
							? {
									children: "Resources",
									side: "right",
									className: "bg-black text-custom-text-primary",
								}
							: undefined
					}
					asChild
				>
					<div>
						<Icon
							size={17}
							strokeWidth={2}
							className="font-bold"
							icon={LifeBuoy}
						/>
						{open && (
							<p className="text-xs text-left font-medium translate-y-[1px]">
								Resources
							</p>
						)}
						{!open && <span className="sr-only">Resources</span>}
					</div>
				</SidebarMenuButton>
			</SidebarMenuItem>
			<SidebarMenuItem>
				<SidebarMenuButton
					className="flex cursor-pointer items-center gap-2"
					tooltip={
						!open
							? {
									children: "Settings",
									side: "right",
									className: "bg-black text-custom-text-primary",
								}
							: undefined
					}
					asChild
				>
					<div>
						<Icon
							size={16}
							strokeWidth={2}
							className="font-bold"
							icon={Settings}
						/>
						{open && (
							<p className="text-xs text-left font-medium translate-y-[1px]">
								Settings
							</p>
						)}
						{!open && <span className="sr-only">Settings</span>}
					</div>
				</SidebarMenuButton>
			</SidebarMenuItem>
		</SidebarMenu>
	);
};

export default GroupExtra;
