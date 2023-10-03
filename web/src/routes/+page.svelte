<script>
	import { onMount } from 'svelte';
	import { workerClient } from '$lib/services';

	let name = undefined;
	let id = undefined;
	let managerIp = undefined;
	let managerPort = undefined;
	let timeout = 20;
	let wport = 0;
	let isWorkerConnected = false;

	let isZeroConfChecked = false;
	let isDeleteTempChecked = false;
	let jsonViewerData = { name: '', id: '', isChecked: false };

	onMount(async () => {
		const state = await workerClient.getWorkerState();
		console.log(state);
	});

	function handleStartAndConnect() {
		jsonViewerData.name = name;
		jsonViewerData.id = id;
		jsonViewerData.isChecked = isChecked;
	}
</script>

<div class="flex flex-col min-h-screen">
	<!-- Header -->
	<header class="bg-gray-600 text-white p-4 text-3xl">ChimeraPy Worker</header>

	<!-- Main Content -->
	<main class="flex-grow flex">
		<div class="w-1/2 p-4">
			<h2 class="text-2xl mb-4" />
			<!-- Form -->
			<form>
				<div class="mb-4">
					<label class="block text-gray-700 text-sm font-bold mb-2" for="name"> Name </label>
					<input
						class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
						id="name"
						type="text"
						placeholder="Name"
						bind:value={name}
					/>
				</div>
				<div class="mb-4">
					<label class="block text-gray-700 text-sm font-bold mb-2" for="id"> ID </label>
					<input
						class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
						id="id"
						type="text"
						placeholder="ID"
						bind:value={id}
					/>
				</div>
				<div class="mb-4">
					<label class="block text-gray-700 text-sm font-bold mb-2" for="wport"> Port </label>
					<input
						class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
						id="wport"
						type="text"
						placeholder="wport"
						bind:value={wport}
					/>
				</div>
				{#if !isZeroConfChecked}
					<div class="mb-4">
						<label class="block text-gray-700 text-sm font-bold mb-2" for="managerIp">
							Manager IP
						</label>
						<input
							class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
							id="managerIp"
							type="text"
							placeholder="IP"
							bind:value={managerIp}
						/>
					</div>
					<div class="mb-4">
						<label class="block text-gray-700 text-sm font-bold mb-2" for="managerPort">
							Manager Port
						</label>
						<input
							class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
							id="managerPort"
							type="text"
							placeholder="Port"
							bind:value={managerPort}
						/>
					</div>
				{/if}
				<div class="mb-4">
					<label class="block text-gray-700 text-sm font-bold mb-2" for="timeout">
						Timeout ({timeout} seconds)
					</label>
					<input
						type="range"
						min="5"
						max="100"
						id="timeout"
						class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-500"
						bind:value={timeout}
					/>
				</div>
				<div class="mb-4">
					<input id="zeroconf" type="checkbox" bind:checked={isZeroConfChecked} />
					<label class="ml-2" for="zeroconf">ZeroConf</label>
					<input class="ml-4" id="deletetemp" type="checkbox" bind:checked={isDeleteTempChecked} />
					<label class="ml-2" for="deletetemp">Delete Temporary</label>
				</div>
				<div>
					<button
						type="button"
						class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded mr-4"
						on:click={handleStartAndConnect}
						>Start and Connect
					</button>
				</div>
			</form>
		</div>
		<div class="w-1/2 bg-gray-200 p-4">
			<h2 class="text-2xl mb-4">Worker State</h2>
			<!-- JSON Viewer -->
			<pre>{JSON.stringify(jsonViewerData, null, 2)}</pre>
		</div>
	</main>

	<!-- Footer -->
	<footer class="bg-gray-600 text-white text-center py-2">
		<p>
			ChimeraPy 2023 -
			<a href="https://github.com/ChimeraPy" target="_blank" class="underline">GitHub</a>
		</p>
	</footer>
</div>
