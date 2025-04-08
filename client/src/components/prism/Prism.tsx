import React from "react";
import Tools from "./Tools";
import Document from "./Document";
import { PanelRightClose } from "lucide-react";

const Prism = () => {
	return (
		<div className="flex min-h-full min-w-screen relative">
			<Tools className="hidden md:block transition-all duration-200 ease-in" />
			<PanelRightClose
				className="md:hidden text-custom-gray-secondary absolute top-4 left-4 cursor-pointer hover:scale-110 duration-150 transition-all shadow-md"
				size={18}
				strokeWidth={1.5}
			/>
			<div className="px-2 w-full sm:px-4 mg:px-8 lg:px-10">
				<Document />
			</div>
		</div>
	);
};

export default Prism;
