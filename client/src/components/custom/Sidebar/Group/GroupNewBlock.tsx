import type React from "react";
import CustomButton from "../../CustomButton";
import Icon from "../../Icon";
import { Plus } from "lucide-react";
import { cn } from "@/lib/utils";
import {
	Tooltip,
	TooltipContent,
	TooltipTrigger,
} from "@/components/ui/tooltip";
import { TooltipArrow } from "@radix-ui/react-tooltip";

type GroupNewBlockProps = {
	open: boolean;
};

const GroupNewBlock: React.FC<GroupNewBlockProps> = ({ open }) => {
	return (
		<div
			className={cn(
				"p-0 flex items-center my-2",
				open ? "w-full justify-start" : "w-full justify-center",
			)}
		>
			{open ? (
				<div className={cn("px-2 w-full")}>
					<CustomButton
						variant="default"
						size="sm"
						className="w-full bg-custom-gray-primary/60 hover:bg-custom-gray-primary/80 text-white"
					>
						<Icon
							icon={Plus}
							size={16}
							className="text-white mr-2"
							strokeWidth={2}
						/>
						Create New Block
					</CustomButton>
				</div>
			) : (
				<Tooltip>
					<TooltipTrigger asChild>
						<div className="p-[6px] translate-x-[1px] cursor-pointer rounded-md bg-red-500 hover:bg-red-600 text-white hover:scale-110 duration-100 transition-all shadow-md flex items-center justify-center">
							<Icon
								icon={Plus}
								size={16}
								strokeWidth={2}
								className="text-white"
							/>
							<span className="sr-only">Create New Block</span>{" "}
						</div>
					</TooltipTrigger>
					<TooltipContent
						side="right"
						className="bg-black text-custom-text-primary font-mono shadow-md text-xs font-normal"
					>
						<p>Create New Block</p>
					</TooltipContent>
				</Tooltip>
			)}
		</div>
	);
};

export default GroupNewBlock;
