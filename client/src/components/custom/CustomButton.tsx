import type React from "react";
import { Button, type buttonVariants } from "../ui/button";
import { cva, type VariantProps } from "class-variance-authority";

export interface ButtonProps
	extends React.ButtonHTMLAttributes<HTMLButtonElement>,
		VariantProps<typeof buttonVariants> {
	asChild?: boolean;
}

const CustomButton: React.FC<ButtonProps> = ({ ...props }) => {
	return <Button {...props} />;
};

export default CustomButton;
