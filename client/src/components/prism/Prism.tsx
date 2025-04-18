import React from "react";
import Sidebar from "./Sidebar";
import Document from "./Document";
import { PanelRightClose } from "lucide-react";

const Prism = () => {
	return (
		<div className="flex min-h-full w-full relative">
			{/* <Sidebar className="hidden md:block transition-all duration-200 ease-in" /> */}
			<div className="px-2 w-full sm:px-4 mg:px-8 lg:px-10">
				<Document />
			</div>
		</div>
	);
};

export default Prism;
