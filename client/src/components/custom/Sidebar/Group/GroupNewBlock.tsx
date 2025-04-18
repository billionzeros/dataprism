import type React from "react";
import CustomButton from "../../CustomButton";
import Icon from "../../Icon";
import { Plus } from "lucide-react";
import { cn } from "@/lib/utils";

type GroupNewBlockProps = {
	open: boolean;
};

const GroupNewBlock: React.FC<GroupNewBlockProps> = ({ open }) => {
	return (
		<div
			className={cn("p-0 flex items-center my-2", open ? "w-full" : "w-fit")}
		>
			{open ? (
				<div className={cn("px-2", open ? "w-full" : "w-fit")}>
					<CustomButton
						variant="default"
						size="sm"
						className="w-full bg-custom-gray-primary/60 hover:bg-custom-gray-primary/80 text-white"
					>
						<Icon
							icon={Plus}
							size={16}
							className="text-white"
							strokeWidth={2}
						/>
						Create New Block
					</CustomButton>
				</div>
			) : (
				<CustomButton
					variant="default"
					size="icon"
					className="rounded-full bg-red-500 w-fit hover:bg-red-600 text-white hover:scale-110 duration-100 transition-all shadow-md"
				>
					<Icon
						icon={Plus}
						size={12}
						strokeWidth={2}
						className="p-0 text-white m-0"
					/>
				</CustomButton>
			)}
		</div>
	);
};

export default GroupNewBlock;
