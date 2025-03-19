import CustomButton from "@/components/custom/button";
import Head from "next/head";
import Link from "next/link";

export default function Home() {
	return (
		<>
			<Head>
				<title>Prism | Let your data talk.</title>
				<meta
					name="description"
					content="
        Prism is a data visualization tool that helps you understand your data better.
        "
				/>
				<link rel="icon" href="/favicon.ico" />
			</Head>

			<main className="min-h-screen bg-custom-background grid place-content-center">
				<CustomButton variant={"custom"} className="select-none">
					<Link href={"/dash"}>Take me the dashboard.</Link>
				</CustomButton>
			</main>
		</>
	);
}
