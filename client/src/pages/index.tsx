import HomePage from "@/components/home/home";
import Head from "next/head";

export default function Home() {
	return (
		<main className="min-h-screen bg-custom-background w-full grid place-content-center">
			<HomePage />
		</main>
	);
}
