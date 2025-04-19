import {
	SidebarMenu,
	SidebarMenuButton,
	SidebarMenuItem,
} from "@/components/ui/sidebar";
import type React from "react";
import Icon from "../Icon";
import { cn } from "@/lib/utils";

type BaseMenuItemsProps = {
	open: boolean;
	title: string;
	icon: React.ElementType;
	tootipTitle?: string;
	onClick?: () => void;
};

const BaseMenuItem: React.FC<BaseMenuItemsProps> = ({
	open,
	tootipTitle,
	title,
	icon,
	onClick,
}) => {
	return (
		<SidebarMenu
			className={cn(
				!open ? "items-center flex flex-col gap-2" : "flex flex-col gap-1 px-2",
			)}
		>
			<SidebarMenuItem>
				<SidebarMenuButton
					onClick={onClick}
					onKeyDown={onClick}
					className="flex cursor-pointer items-center gap-2"
					tooltip={
						!open
							? {
									children: tootipTitle ?? title,
									side: "right",
									className: "bg-black text-custom-text-primary",
								}
							: undefined
					}
					asChild
				>
					<div>
						<Icon size={16} strokeWidth={2} className="font-bold" icon={icon} />
						{open && (
							<p className="text-xs text-left font-medium translate-y-[1px]">
								{title}
							</p>
						)}
						{!open && <span className="sr-only">{title}</span>}
					</div>
				</SidebarMenuButton>
			</SidebarMenuItem>
		</SidebarMenu>
	);
};

export default BaseMenuItem;
