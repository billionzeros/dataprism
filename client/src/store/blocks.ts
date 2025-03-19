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

	isRoot: boolean;

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
export const blocks = new Map<BlockCid["id"], BlockContent>();

// The root block id of the document
export let rootBlockId: string | null = null;

// Record of all blocks in the document. based on the block id, its going to be a linked list of blocks
export const blockMatrixAtom = atom<Record<string, BlockCid>>({});

// Add a new block to the document, after a specific blockId
export const addBlockAfterAtom = atom(
	null,
	(get, set, arg: { afterBlockId: string; content: BlockContent }) => {
		const { afterBlockId, content } = arg;

		const blockMatrix = get(blockMatrixAtom);
		const afterBlock = blockMatrix[afterBlockId];

		const newBlockCid = createBlockCid();

		if (afterBlock?.nextBlockId) {
			// Insert the new block between the afterBlock and the block after the afterBlock
			newBlockCid.nextBlockId = afterBlock.nextBlockId;
			afterBlock.nextBlockId = newBlockCid.id;
		}

		set(blockMatrixAtom, {
			...blockMatrix,
			[newBlockCid.id]: newBlockCid,
		});

		blocks.set(newBlockCid.id, content);
	},
);

// Add a new block to the document, before a specific blockId
export const addBlockBeforeAtom = atom(
	null,
	(get, set, arg: { beforeBlockId: string; content: BlockContent }) => {
		const { beforeBlockId, content } = arg;

		const blockMatrix = get(blockMatrixAtom);
		const beforeBlock = blockMatrix[beforeBlockId];

		const newBlockCid = createBlockCid();

		if (beforeBlock?.prevBlockId) {
			// Insert the new block between the beforeBlock and the block before the beforeBlock
			newBlockCid.prevBlockId = beforeBlock.prevBlockId;
			beforeBlock.prevBlockId = newBlockCid.id;
		}

		set(blockMatrixAtom, {
			...blockMatrix,
			[newBlockCid.id]: newBlockCid,
		});

		blocks.set(newBlockCid.id, content);
	},
);

// Remove a block from the document, based on the blockId
export const removeBlockAtom = atom(
	null,
	(get, set, arg: { blockId: string }) => {
		const { blockId } = arg;

		const blockMatrix = get(blockMatrixAtom);
		const blockCid = blockMatrix[blockId];

		if (blockCid) {
			if (blockCid.prevBlockId) {
				// If the block has a previous block, set the next block of the previous block to the next block of the block
				const prevBlockCid = blockMatrix[blockCid.prevBlockId];
				if (prevBlockCid) {
					prevBlockCid.nextBlockId = blockCid.nextBlockId;
				}
			}

			if (blockCid.nextBlockId) {
				// If the block has a next block, set the previous block of the next block to the previous block of the block
				const nextBlockCid = blockMatrix[blockCid.nextBlockId];
				if (nextBlockCid) {
					nextBlockCid.prevBlockId = blockCid.prevBlockId;
				}
			}

			delete blockMatrix[blockId];
			blocks.delete(blockId);
		}

		set(blockMatrixAtom, {
			...blockMatrix,
		});
	},
);

// Add a Block to the Root of the Document, if a root Block Exists it will become the next block of the new block
export const addBlockAtRootAtom = atom(
	null,
	(get, set, arg: { content: BlockContent }) => {
		const { content } = arg;

		const blockMatrix = get(blockMatrixAtom);

		const newBlockCid = createBlockCid();

		if (rootBlockId) {
			const rootBlockCid = blockMatrix[rootBlockId];
			if (rootBlockCid) {
				newBlockCid.nextBlockId = rootBlockCid.id;
				rootBlockCid.prevBlockId = newBlockCid.id;
			}
		}

		set(blockMatrixAtom, {
			...blockMatrix,
			[newBlockCid.id]: newBlockCid,
		});

		blocks.set(newBlockCid.id, content);
		rootBlockId = newBlockCid.id;
	},
);

// Add a Block to the End of the Document, if the root does not exist the new block will become the root
export const addBlockAtEndAtom = atom(
	null,
	(get, set, arg: { content: BlockContent }) => {
		const { content } = arg;

		const blockMatrix = get(blockMatrixAtom);

		const newBlockCid = createBlockCid();

		let currentBlockId = rootBlockId;

		while (currentBlockId) {
			const blockCid = blockMatrix[currentBlockId];

			if (!blockCid) break;

			const block = getBlock(blockCid.id);

			if (!block) break;

			if (!blockCid.nextBlockId) {
				blockCid.nextBlockId = newBlockCid.id;
				newBlockCid.prevBlockId = blockCid.id;
				break;
			}

			currentBlockId = blockCid.nextBlockId;
		}

		if (!rootBlockId) {
			rootBlockId = newBlockCid.id;
			newBlockCid.isRoot = true;
		}

		const prevBlockCid = newBlockCid.prevBlockId;

		set(blockMatrixAtom, {
			...blockMatrix,
			[newBlockCid.id]: newBlockCid,
		});

		blocks.set(newBlockCid.id, content);
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
		isRoot: false,
		parentBlockId: null,
		parentBlockIndex: null,
	};
};

/**
 * @description Get a block based on the block id
 * @param blockId The unique id of the block
 * @returns
 * The block with the block id
 */
export const getBlock = (blockId: string) => {
	return blocks.get(blockId);
};

// Find the last block id in the document
export const getLastBlockId = (
	blockMatrix: Record<string, BlockCid>,
): string | null => {
	if (!rootBlockId) return null;

	let currentId = rootBlockId;
	let lastId = rootBlockId;

	while (currentId) {
		lastId = currentId;
		const block = blockMatrix[currentId];
		if (!block || !block.nextBlockId) break;
		currentId = block.nextBlockId;
	}

	return lastId;
};
