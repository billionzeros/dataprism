import { GripVertical } from "lucide-react";
import type React from "react";

interface Props {
	children: React.ReactNode;
}

const BaseBlock: React.FC<Props> = ({ children }) => {
	return (
		<div className="flex relative items-center gap-1 group -translate-x-6">
			<span className="flex items-center opacity-0 group-hover:opacity-100 cursor-pointer duration-100 transition-all">
				<GripVertical size={18} className="text-custom-gray-secondary" />
			</span>

			<div>{children}</div>
		</div>
	);
};

export default BaseBlock;
