import { SidebarHeader } from "@/components/ui/sidebar";
import { PanelRightClose, PanelRightOpen } from "lucide-react";
import type React from "react";
import Icon from "../Icon";

type SidebarHeaderProps = {
	open: boolean;
	toggleSidebar: () => void;
};

const AppSidebarHeader: React.FC<SidebarHeaderProps> = ({
	open,
	toggleSidebar,
}) => {
	return (
		<>
			{open ? (
				<div className="flex items-center justify-between">
					<h1 className="text-2xl font-bold text-custom-text">Prism</h1>
					{open ? (
						<Icon
							className="text-custom-gray-secondary cursor-pointer hover:scale-110 duration-150 transition-all"
							icon={PanelRightOpen}
							onClick={toggleSidebar}
						/>
					) : (
						<Icon
							className="text-custom-gray-secondary cursor-pointer hover:scale-110 duration-150 transition-all"
							icon={PanelRightClose}
							onClick={toggleSidebar}
						/>
					)}
				</div>
			) : null}
		</>
	);
};

export default AppSidebarHeader;
