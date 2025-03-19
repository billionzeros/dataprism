import { ChartArea, X } from "lucide-react";
import React from "react";

const Tabs = () => {
	return (
		<div className="flex items-center">
			{/* Active tab */}
			<div className="flex items-center gap-2 px-4 py-2 border-x select-none border-custom-gray-secondary relative cursor-pointer">
				<ChartArea className="text-custom-text-primary" size={18} />
				<span className="text-custom-text-primary text-sm font-normal">
					Energy Price Metrics
				</span>
				<X
					className="text-custom-gray-secondary active:translate-y-[1px]"
					size={15}
				/>
			</div>
		</div>
	);
};

export default Tabs;
