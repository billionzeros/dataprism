import { Home } from "lucide-react";
import React from "react";
import Tabs from "./Tabs";

const Header = () => {
	return (
		<div className="bg-custom-gray-primary flex items-center px-2 py-[1px]">
			<div className="hover:bg-custom-gray-secondary w-fit p-2 cursor-pointer transition-all duration-150 active:translate-y-[1px] select-none rounded-md mr-3">
				<Home color="white" size={20} />
			</div>

			<div className="flex items-center">
				<Tabs />
			</div>
		</div>
	);
};

export default Header;
