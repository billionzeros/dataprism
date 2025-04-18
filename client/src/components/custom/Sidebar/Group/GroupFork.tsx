import {
	SidebarMenu,
	SidebarMenuButton,
	SidebarMenuItem,
} from "@/components/ui/sidebar";
import React from "react";
import { GitFork } from "lucide-react";
import Icon from "../../Icon";

const GroupFork = () => {
	return (
		<SidebarMenu>
			<SidebarMenuItem className="cursor-default">
				<SidebarMenuButton
					tooltip={{
						children: "Fork",
						className: "bg-custom-gray-primary text-custom-gray-secondary",
					}}
					className="flex items-center justify-between gap-2"
				>
					<div className="flex items-center gap-2">
						<Icon
							size={16}
							strokeWidth={2}
							className="font-bold"
							icon={GitFork}
						/>
						<p className="text-xs text-left font-medium translate-y-[1px]">
							Fork
						</p>
					</div>
				</SidebarMenuButton>
			</SidebarMenuItem>
		</SidebarMenu>
	);
};

export default GroupFork;
