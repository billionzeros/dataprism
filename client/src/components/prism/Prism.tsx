import React from "react";
import Tools from "./Tools";
import Document from "./Document";

const Prism = () => {
	return (
		<div className="grid lg:grid-cols-[1fr_10fr_1fr] px-4 sm:px-10">
			<Tools />
			<Document />
			<div />
		</div>
	);
};

export default Prism;
