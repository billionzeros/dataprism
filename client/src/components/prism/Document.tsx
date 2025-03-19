import type React from "react";
import BlockRenderer from "../blocks/BlockRenderer";
import Title from "./Title";
import { useAtomValue } from "jotai";
import { rootBlockId, getBlock } from "@/store/blocks";

const Document = () => {
	const rootBlock = useAtomValue(rootBlockId);

	const renderBlocks = (): Array<React.ReactNode> => {
		const components: Array<React.ReactNode> = [];
		let currentBlockId = rootBlock;

		while (currentBlockId) {
			const block = getBlock(currentBlockId);

			if (!block) break;

			components.push(<BlockRenderer key={block.cid.id} block={block} />);

			currentBlockId = block.cid.nextBlockId;
		}

		return components;
	};

	return (
		<div className="mt-10">
			<Title />
			<div className="cursor-text min-h-screen">{renderBlocks()}</div>
		</div>
	);
};

export default Document;
