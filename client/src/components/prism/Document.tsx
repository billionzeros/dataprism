import React from "react";
import BlockRenderer from "../blocks/BlockRenderer";
import Header from "../blocks/Header";
import Title from "./Title";

const Document = () => {
	return (
		<div className="mt-10">
			<Title />
			<BlockRenderer>
				<Header content="Energy Price Metrics" size="large" />
			</BlockRenderer>
		</div>
	);
};

export default Document;
