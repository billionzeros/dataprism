import { cn } from "@/lib/utils";
import { useState } from "react";
import Icon from "../Icon";
import { ArrowRight, X } from "lucide-react";

const InfoCard: React.FC<{ sidebarOpen: boolean }> = ({ sidebarOpen }) => {
	const [open, setOpen] = useState(true);

	if (!open) {
		return null;
	}

	return (
		<div
			className={cn(
				"border-[2px] border-custom-gray-primary m-2 p-3 rounded-md flex flex-col gap-1 shadow-md",
				sidebarOpen ? "delay-300 opacity-100" : "opacity-0",
			)}
		>
			<div className="flex items-center justify-between">
				<div className="text-sm text-custom-text-primary/80 mb-[3px] font-bold font-inter select-none cursor-default">
					Prism AI
				</div>

				<Icon
					className="hover:bg-custom-gray-primary aspect-square p-[2px] shadow-md rounded-sm cursor-pointer transition-all duration-200 ease-in-out"
					size={18}
					icon={X}
					onClick={() => setOpen(false)}
					aria-label="Close"
					aria-hidden="true"
					aria-controls="info-card"
					aria-expanded={open}
				/>
			</div>
			<p className="text-xs text-custom-gray-secondary font-inter select-none cursor-default">
				Built to make <u>data talk to you</u> !! <br /> <br /> Ask Questions,
				and keep your conversations with LLMs organised.
			</p>
			<div className="text-custom-text-primary/80 cursor-pointer hover:text-custom-text-primary group flex items-center gap-1 text-xs font-bold font-inter mt-2">
				<span>Unlock Potential</span>
				<Icon
					className="text-custom-text-primary/80 group-hover:text-custom-text-primary"
					size={12}
					icon={ArrowRight}
				/>
			</div>
		</div>
	);
};

export default InfoCard;
