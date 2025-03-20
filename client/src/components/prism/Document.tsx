import React, { useState } from "react";
import BlockRenderer from "../blocks/BlockRenderer";
import Title from "./Title";
import { useAtomValue, useSetAtom } from "jotai";
import {
	getBlock,
	addBlockAtEndAtom,
	blockMatrixAtom,
	rootBlockId,
	getLastBlockId,
	type BlockContent,
} from "@/store/blocks";

const Document = () => {
	const blockMatrix = useAtomValue(blockMatrixAtom);
	const addBlockAtEnd = useSetAtom(addBlockAtEndAtom);

	const renderBlocks = (): Array<React.ReactNode> => {
		const components: Array<React.ReactNode> = [];
		let currentBlockId = rootBlockId;

		while (currentBlockId) {
			const blockCid = blockMatrix[currentBlockId];

			if (!blockCid) break;

			const blockContent = getBlock(blockCid.id);

			if (!blockContent) break;

			const nextBlockId = blockCid.nextBlockId;

			components.push(
				<React.Fragment key={`block-fragment-${blockCid.id}`}>
					<BlockRenderer
						key={blockCid.id}
						blockCid={blockCid}
						blockContent={blockContent}
					/>
				</React.Fragment>,
			);

			currentBlockId = nextBlockId;
		}

		return components;
	};

	const handleOnClick = (e: React.MouseEvent | React.KeyboardEvent) => {
		const target = e.target as HTMLElement;

		if (
			target.getAttribute("contenteditable") === "true" ||
			target.closest('[contenteditable="true"]') ||
			target.closest(".block-renderer")
		) {
			return;
		}

		e.preventDefault();

		const lastBlockId = getLastBlockId(blockMatrix);
		if (lastBlockId) {
			const lastBlock = getBlock(lastBlockId);

			if (
				lastBlock &&
				lastBlock.type === "paragraph" &&
				lastBlock.content.text?.length === 0
			) {
				return;
			}
		}

		const content: BlockContent<"paragraph"> = {
			type: "paragraph",

			content: {
				size: "medium",
				text: "",
			},
		};

		addBlockAtEnd({
			content,
		});
	};

	console.info("BlockMatrix", blockMatrix);

	return (
		<div className="mt-10">
			<Title />
			<div
				onClick={handleOnClick}
				onKeyDown={(e) => {
					if (
						e.key === "Enter" &&
						!(e.target as HTMLElement).isContentEditable
					) {
						handleOnClick(e);
					}
				}}
				className="cursor-text min-h-screen"
			>
				{renderBlocks()}
			</div>
		</div>
	);
};

export default Document;
