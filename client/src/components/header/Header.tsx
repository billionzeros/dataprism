import React from "react";
import Tabs from "./Tabs";

const Header = () => {
	return (
		<div className="flex items-center py-[1px] border-b-[1px] border-r-[1px] border-custom-gray-primary">
			<div className="flex items-center">
				<Tabs />
			</div>
		</div>
	);
};

export default Header;
