import { cn } from "@/lib/utils";
import { Plus, DatabaseZap, GitFork, MessagesSquare } from "lucide-react";
import type React from "react";

interface Props {
	className?: string;
}

const Sidebar: React.FC<Props> = ({ className }) => {
	return (
		<div className={cn("h-screen top-0 sticky", className)}>
			<div className="border-r-[1px] h-full flex flex-col items-center pt-4 px-3 gap-5 w-fit border-custom-gray-primary">
				<div className="group relative cursor-pointer ">
					<div className="bg-red-500 rounded-full hover:scale-110 duration-150 transition-all shadow-md p-1 w-fit">
						<Plus className="text-white" size={18} strokeWidth={1.5} />
					</div>
					<div className="absolute left-8 top-1/2 -translate-y-1/2 invisible group-hover:visible">
						<span className="text-custom-text-primary font-mono bg-black shadow-md p-2 rounded-lg text-xs font-normal whitespace-nowrap">
							Create New
						</span>
					</div>
				</div>

				<div className="group relative cursor-pointer hover:scale-110 duration-150 transition-all shadow-md">
					<GitFork
						className="text-custom-gray-secondary"
						size={20}
						strokeWidth={1.0}
					/>
					<div className="absolute left-8 top-1/2 -translate-y-1/2 invisible group-hover:visible">
						<span className="text-custom-text-primary font-mono bg-black shadow-md p-2 rounded-lg text-xs font-normal whitespace-nowrap">
							Fork
						</span>
					</div>
				</div>

				<div className="group relative cursor-pointer hover:scale-110 duration-150 transition-all shadow-md">
					<DatabaseZap
						className="text-custom-gray-secondary"
						size={20}
						strokeWidth={1.0}
					/>
					<div className="absolute left-8 top-1/2 -translate-y-1/2 invisible group-hover:visible">
						<span className="text-custom-text-primary font-mono bg-black shadow-md p-2 rounded-lg text-xs font-normal whitespace-nowrap">
							Database
						</span>
					</div>
				</div>

				<div className="group relative cursor-pointer hover:scale-110 duration-150 transition-all shadow-md">
					<MessagesSquare
						className="text-custom-gray-secondary"
						size={20}
						strokeWidth={1.0}
					/>
					<div className="absolute left-8 top-1/2 -translate-y-1/2 invisible group-hover:visible">
						<span className="text-custom-text-primary font-mono bg-black shadow-md p-2 rounded-lg text-xs font-normal whitespace-nowrap">
							AI Chats
						</span>
					</div>
				</div>
			</div>
		</div>
	);
};

export default Sidebar;
