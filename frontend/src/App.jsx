import { useEffect, useState } from "react";
import viteLogo from "/vite.svg";
import "./App.css";

function App() {
	const [count, setCount] = useState(0);

	useEffect(() => {
		const fetchData = async () => {
			const response = await fetch(import.meta.env.VITE_API_URL);
			const data = await response.json();
			console.log(data);
		};
		fetchData();
	}, []);
	return (
		<>
			<div>
				<a
					href="https://vite.dev"
					target="_blank">
					<img
						src={viteLogo}
						className="logo"
						alt="Vite logo"
					/>
				</a>
			</div>
			<h1>Vite + React</h1>
			<div className="card">
				<button onClick={() => setCount((count) => count + 1)}>
					count is {count}
				</button>
				<p>
					Edit <code>src/App.jsx</code> and save to test HMR
				</p>
			</div>
			<p className="read-the-docs">
				Click on the Vite and React logos to learn more
			</p>
		</>
	);
}

export default App;
