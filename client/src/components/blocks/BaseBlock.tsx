import { GripVertical } from "lucide-react";
import type React from "react";

interface Props {
	children: React.ReactNode;
}

const BaseBlock: React.FC<Props> = ({ children }) => {
	return (
		<div className="relative w-full group -translate-x-6">
			{/* Position the grip absolutely so it doesn't affect layout */}
			<div className="absolute left-0 top-1.5 opacity-0 group-hover:opacity-100 transition-opacity duration-100">
				<GripVertical
					size={18}
					className="text-custom-gray-secondary cursor-grab"
				/>
			</div>

			{/* Add left padding for the grip icon space */}
			<div className="w-full pl-6">{children}</div>
		</div>
	);
};

export default BaseBlock;
