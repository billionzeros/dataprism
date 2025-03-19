import React from "react";
import Tools from "./Tools";
import Document from "./Document";

const Prism = () => {
	return (
		<div className="grid grid-cols-[1fr_10fr]">
			<Tools />
			<Document />
		</div>
	);
};

export default Prism;
