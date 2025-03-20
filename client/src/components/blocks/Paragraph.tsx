import { cn } from "@/lib/utils";
import type React from "react";
import BaseBlock from "./BaseBlock";
import { useEffect, useRef, useState } from "react";
import type { BlockContent, BlockCid } from "@/store/blocks";

interface Props {
	cid: BlockCid;
	content: BlockContent<"paragraph">["content"];
}

const Paragraph: React.FC<Props> = ({ cid, content }) => {
	const editableRef = useRef<HTMLDivElement>(null);
	const [isEmpty, setIsEmpty] = useState(content.text.length === 0);

	const placeHolderContent = `Write, Press "Space" for AI, Type ' / ' for commands`;

	const variants: Record<Props["content"]["size"], string> = {
		small: "text-base",
		medium: "text-lg",
		large: "text-xl",
	};

	useEffect(() => {
		const shouldFocus = cid.nextBlockId === null && isEmpty;

		if (shouldFocus && editableRef.current) {
			editableRef.current.focus();
		}
	}, [cid.nextBlockId, isEmpty]);

	const handleKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
		if (e.key === " " || e.code === "Space") {
			console.log("Space pressed");
		}
	};

	const handleInput = (e: React.FormEvent<HTMLDivElement>) => {
		const currentContent = editableRef.current?.textContent || "";
		setIsEmpty(currentContent.length === 0);
	};

	const handleBlur = (e: React.FocusEvent<HTMLDivElement>) => {
		console.log("Push update to the Database");
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
				/>

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
