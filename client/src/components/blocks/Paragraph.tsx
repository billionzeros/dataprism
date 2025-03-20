import { cn } from "@/lib/utils";
import type React from "react";
import BaseBlock from "./BaseBlock";
import { useEffect, useRef, useState } from "react";
import {
	type BlockContent,
	type BlockCid,
	addBlockAfterAtom,
	removeBlockAtom,
} from "@/store/blocks";
import { useSetAtom } from "jotai";

interface Props {
	cid: BlockCid;
	content: BlockContent<"paragraph">["content"];
	onKeyDown?: (e: React.KeyboardEvent<HTMLDivElement>, cid: BlockCid) => void;
}

const Paragraph: React.FC<Props> = ({ cid, content, onKeyDown }) => {
	const addBlockAfter = useSetAtom(addBlockAfterAtom);
	const removeBlock = useSetAtom(removeBlockAtom);

	const editableRef = useRef<HTMLDivElement>(null);
	const [isEmpty, setIsEmpty] = useState(content.text.length === 0);
	const [textContent, setTextContent] = useState(content.text);

	const placeHolderContent = `Write, Press "Space" for AI, Type ' / ' for commands`;

	const variants: Record<Props["content"]["size"], string> = {
		small: "text-base",
		medium: "text-lg",
		large: "text-xl",
	};

	// Focus the element when it's the last block and empty
	useEffect(() => {
		const shouldFocus = cid.nextBlockId === null;

		if (shouldFocus && editableRef.current) {
			setTimeout(() => {
				editableRef.current?.focus();

				const selection = window.getSelection();
				const range = document.createRange();

				if (editableRef.current) {
					range.setStart(editableRef.current, 0);
					range.collapse(true);
					selection?.removeAllRanges();
					selection?.addRange(range);
				}
			}, 0);
		}
	}, [cid.nextBlockId]);

	const handleInput = (e: React.FormEvent<HTMLDivElement>) => {
		const currentContent = editableRef.current?.textContent || "";
		setTextContent(currentContent);
		setIsEmpty(currentContent.length === 0);
	};

	const handleBlur = () => {
		console.log("Push update to the Database", textContent);
	};

	const handleKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
		// Handle space key press
		if (e.key === " " || e.code === "Space") {
			console.log("Space pressed", textContent);
		}

		console.info("Key Pressed", e.key, e.code);

		// Handle enter key press
		if (e.key === "Enter" && !e.shiftKey) {
			e.preventDefault();

			const currentPosition =
				window.getSelection()?.getRangeAt(0).endOffset || 0;
			const currentText = editableRef.current?.textContent || "";

			const textBeforeCursor = currentText.substring(0, currentPosition);
			const textAfterCursor = currentText.substring(currentPosition);

			if (editableRef.current) {
				editableRef.current.textContent = textBeforeCursor;
				setTextContent(textBeforeCursor);
				setIsEmpty(textBeforeCursor.length === 0);
			}

			addBlockAfter({
				afterBlockId: cid.id,
				content: {
					type: "paragraph",
					content: {
						text: textAfterCursor,
						size: "medium",
					},
				},
			});
		}

		if (e.key === "Backspace" && textContent.length === 0) {
			removeBlock({
				blockId: cid.id,
			});
		}
	};

	return (
		<BaseBlock>
			<div className="relative w-full">
				<div
					ref={editableRef}
					contentEditable="plaintext-only"
					suppressContentEditableWarning
					onInput={handleInput}
					onKeyDown={handleKeyDown}
					onBlur={handleBlur}
					className={cn(
						"text-custom-text-primary w-full border-none outline-none overflow-wrap-break-word break-words whitespace-pre-wrap overflow-x-hidden min-h-[1.5em]",
						variants[content.size],
					)}
				>
					{content.text}
				</div>

				{isEmpty && (
					<div
						className={cn(
							"absolute top-0 left-0 pointer-events-none text-custom-gray-primary",
							variants[content.size],
						)}
					>
						{placeHolderContent}
					</div>
				)}
			</div>
		</BaseBlock>
	);
};

export default Paragraph;
