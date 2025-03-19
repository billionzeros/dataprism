import { CirclePlus, DatabaseZap, GitFork, MessagesSquare } from "lucide-react";
import React from "react";

const Tools = () => {
	return (
		<div className="grid h-fit mt-10 sticky top-10 left-5 select-none">
			<div className="bg-custom-gray-primary rounded-md w-fit p-2 flex flex-col gap-2">
				<div className="flex items-center flex-col gap-1 cursor-pointer hover:bg-custom-gray-secondary p-2 rounded-md">
					<CirclePlus className="text-white" size={24} />
					<span className="text-xs text-custom-text-primary">Add</span>
				</div>

				<div className="flex items-center flex-col gap-1 cursor-pointer hover:bg-custom-gray-secondary p-2 rounded-md">
					<GitFork className="text-white" size={24} />
					<span className="text-xs text-custom-text-primary">Fork</span>
				</div>

				<div className="flex items-center flex-col gap-1 cursor-pointer hover:bg-custom-gray-secondary p-2 rounded-md">
					<DatabaseZap className="text-white" size={24} />
					<span className="text-xs text-custom-text-primary">Source</span>
				</div>

				<div className="flex items-center flex-col gap-1 cursor-pointer hover:bg-custom-gray-secondary p-2 rounded-md">
					<MessagesSquare className="text-white" size={24} />
					<span className="text-xs text-custom-text-primary">Chats</span>
				</div>
			</div>
		</div>
	);
};

export default Tools;
