import { ChartArea, X } from "lucide-react";
import React from "react";

const Tabs = () => {
	return (
		<div className="flex items-center">
			<div className="flex items-center gap-2 px-4 py-2 border-r-[0.5px] select-none border-custom-gray-primary relative cursor-pointer">
				<ChartArea
					strokeWidth={1.0}
					className="text-custom-gray-secondary active:translate-y-[1px]"
					size={18}
				/>
				<span className="text-custom-text-primary text-xs font-normal">
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
