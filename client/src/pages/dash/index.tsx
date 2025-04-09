import Header from "@/components/header/Header";
import React from "react";
import Prism from "@/components/prism/Prism";

const DashPage = () => {
	return (
		<main className="bg-custom-background min-h-screen max-w-full">
			<Header />
			<Prism />
		</main>
	);
};

export default DashPage;
