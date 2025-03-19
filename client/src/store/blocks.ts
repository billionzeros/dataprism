import { atom } from "jotai";
import { v4 as uuidv4 } from "uuid";

/**
 * @description
 * `Block` is defined as the smallest unit of representation of the content, Each block has a unique id, a type, and a content
 * Blocks are oriented vertically, one block can have another block after it, before it and can also be nested inside another block.
 */
export type Block = {
	cid: BlockCid;
	content: BlockContent;
};

// The content of the block
export type BlockContent = {
	type: BlockType;

	text?: string;
	size?: "small" | "medium" | "large";
};

// Information about the block
export type BlockCid = {
	// Unique id of the block
	id: string;

	// Next and previous block id
	nextBlockId: string | null;
	prevBlockId: string | null;

	// When a block is nested inside another block, the parentBlockId will be the id of the parent block
	parentBlockId: string | null;
	parentBlockIndex: number | null; // The index of the block in the parent block
};

// The type of the block
export type BlockType =
	| "header"
	| "paragraph"
	| "code"
	| "image"
	| "list"
	| "quote"
	| "divider"
	| "column"
	| "chart";

// Record of all blocks in the document. based on the block id
export const blocks = new Map<string, Block>();

// Record of all blocks in the document. based on the block id, its going to be a linked list of blocks
export const blockMatrix = atom<Record<string, BlockCid>>({});

// The root block id of the document
export const rootBlockId = atom<string | null>(null);

// Add a new block to the document, after a specific blockId
export const addBlockAfter = atom(
	null,
	(get, set, arg: { afterBlockId: string; content: BlockContent }) => {
		const { afterBlockId, content } = arg;

		const blockMatrixValue = get(blockMatrix);
		const afterBlock = blocks.get(afterBlockId);

		const newBlock = createBlock(content);

		if (afterBlock?.cid.nextBlockId) {
			// Insert the new block between the afterBlock and the block after the afterBlock
			newBlock.cid.nextBlockId = afterBlock.cid.nextBlockId;
			afterBlock.cid.nextBlockId = newBlock.cid.id;
		}

		set(blockMatrix, {
			...blockMatrixValue,
			[newBlock.cid.id]: newBlock.cid,
		});

		blocks.set(newBlock.cid.id, newBlock);
	},
);

// Add a new block to the document, before a specific blockId
export const addBlockBefore = atom(
	null,
	(get, set, arg: { beforeBlockId: string; content: BlockContent }) => {
		const { beforeBlockId, content } = arg;

		const blockMatrixValue = get(blockMatrix);
		const beforeBlock = blocks.get(beforeBlockId);

		const newBlock = createBlock(content);

		if (beforeBlock?.cid.prevBlockId) {
			// Insert the new block between the beforeBlock and the block before the beforeBlock
			newBlock.cid.prevBlockId = beforeBlock.cid.prevBlockId;
			beforeBlock.cid.prevBlockId = newBlock.cid.id;
		}

		set(blockMatrix, {
			...blockMatrixValue,
			[newBlock.cid.id]: newBlock.cid,
		});

		blocks.set(newBlock.cid.id, newBlock);
	},
);

// Remove a block from the document, based on the blockId
export const removeBlock = atom(null, (get, set, arg: { blockId: string }) => {
	const { blockId } = arg;

	const blockMatrixValue = get(blockMatrix);
	const block = blocks.get(blockId);

	if (block) {
		if (block.cid.prevBlockId) {
			// If the block has a previous block, set the next block of the previous block to the next block of the block
			const prevBlock = blocks.get(block.cid.prevBlockId);
			if (prevBlock) {
				prevBlock.cid.nextBlockId = block.cid.nextBlockId;
			}
		}

		if (block.cid.nextBlockId) {
			// If the block has a next block, set the previous block of the next block to the previous block of the block
			const nextBlock = blocks.get(block.cid.nextBlockId);
			if (nextBlock) {
				nextBlock.cid.prevBlockId = block.cid.prevBlockId;
			}
		}

		delete blockMatrixValue[blockId];
		blocks.delete(blockId);
	}

	set(blockMatrix, {
		...blockMatrixValue,
	});
});

// Add a Block to the Root of the Document, if a root Block Exists it will become the next block of the new block
export const addRootBlock = atom(
	null,
	(get, set, arg: { content: BlockContent }) => {
		const { content } = arg;

		const blockMatrixValue = get(blockMatrix);
		const rootBlockIdValue = get(rootBlockId);

		const newBlock = createBlock(content);

		if (rootBlockIdValue) {
			const rootBlock = blocks.get(rootBlockIdValue);
			if (rootBlock) {
				newBlock.cid.nextBlockId = rootBlockIdValue;
				rootBlock.cid.prevBlockId = newBlock.cid.id;
			}
		}

		set(rootBlockId, newBlock.cid.id);
		set(blockMatrix, {
			...blockMatrixValue,
			[newBlock.cid.id]: newBlock.cid,
		});

		blocks.set(newBlock.cid.id, newBlock);
	},
);

/**
 * @description
 * Create a new block cid, with a unique id - at this point the other values are null
 * @returns
 * A new block cid
 */
export const createBlockCid = (): BlockCid => {
	return {
		id: uuidv4(),
		nextBlockId: null,
		prevBlockId: null,

		parentBlockId: null,
		parentBlockIndex: null,
	};
};

/**
 * @description
 * Create a new block with a unique id and the content
 * @param cid The block cid is the unique id of the block
 * @param content The content of the block
 * @returns  A new block
 */
export const createBlock = (content: BlockContent, cid?: BlockCid) => {
	return {
		cid: cid ?? createBlockCid(),
		content,
	};
};
