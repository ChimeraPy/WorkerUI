<script lang="ts">
	import { onMount } from 'svelte';
	import { workerClient } from '$lib/services';
	import type { WorkerConfig } from '../lib/models';
	import { isValidWorkerCreationConfig } from '$lib/Utils';
	import Alert from '$lib/Modal/Alert.svelte';
	import {
		Table,
		TableBody,
		TableBodyCell,
		TableBodyRow,
		TableHead,
		TableHeadCell
	} from 'flowbite-svelte';

	let errorDisplay;
	let canCreateWorker: boolean = false;
	let workerConfig: WorkerConfig = {
		name: '',
		wport: 0,
		delete_temp: true,
		id: undefined,
		zeroconf: true,
		port: 0,
		ip: '',
		timeout: 20
	};

	let connecting: boolean = false;
	let connected: boolean = false;

	let workerState = {};

	onMount(async () => {
		(await workerClient.getWorkerState())
			.map((state) => {
				workerState = state;
				connected = state.name !== undefined;
			})
			.mapError((e) => {
				// Display error
				errorDisplay.display({
					title: 'Error Getting Worker State',
					content: e
				});
			});
	});

	async function handleStartAndConnect() {
		connecting = true;
		(await workerClient.connect(workerConfig))
			.map((state) => {
				workerState = state;
				connecting = false;
				connected = true;
			})
			.mapError((e) => {
				// Display error
				errorDisplay.display({
					title: 'Error Starting and Connecting Worker',
					content: e
				});
				connecting = false;
			});
	}

	async function handleShutdown() {
		(await workerClient.shutdown())
			.map((state) => {
				workerState = state;
				connected = false;
			})
			.mapError((e) => {
				// Display error
				errorDisplay.display({
					title: 'Error Shutting down Worker',
					content: e
				});
			});
	}

	$: {
		canCreateWorker = isValidWorkerCreationConfig(workerConfig);
	}

	function getNodes(workerState) {
		if (workerState.nodes === undefined) {
			return 'Unknown';
		}
		return Object.values(workerState.nodes)
			.map((node) => `${node.name}(${node.fsm})`)
			.join(', ');
	}
</script>

<div class="flex flex-col min-h-screen">
	<!-- Header -->
	<header class="bg-gray-600 text-white p-4 text-3xl">ChimeraPy Worker</header>

	<!-- Main Content -->
	<main class="flex-grow flex">
		<div class="w-1/2 p-4">
			{#if connected}
				<h2 class="text-2xl mb-4">Worker Connected</h2>
				<Table hoverable={true} class="mb-4">
					<TableHead>
						<TableHeadCell>Name</TableHeadCell>
						<TableBodyCell>ID</TableBodyCell>
						<TableHeadCell>URL</TableHeadCell>
						<TableHeadCell>Nodes</TableHeadCell>
					</TableHead>
					<TableBody class="divide-y">
						<TableBodyRow>
							<TableBodyCell>{workerState.name}</TableBodyCell>
							<TableBodyCell>{workerState.id}</TableBodyCell>
							<TableBodyCell>{`http://${workerState.ip}:${workerState.port}`}</TableBodyCell>
							<TableBodyCell tdClass="px-6 py-4 font-medium">{getNodes(workerState)}</TableBodyCell>
						</TableBodyRow>
					</TableBody>
				</Table>
				<div class="flex justify-center">
					<button
						type="button"
						class="bg-blue-500
                           hover:bg-blue-700
                           disabled:opacity-50
                           disabled:cursor-not-allowed
                           text-white
                           font-bold
                           py-2
                           px-4
                           rounded
                           mr-4"
						on:click={handleShutdown}>{'shutdown'}</button
					>
				</div>
			{:else}
				<h2 class="text-2xl mb-4">Connect Worker</h2>
				<!-- Form -->
				<form>
					<div class="mb-4">
						<label class="block text-gray-700 text-sm font-bold mb-2" for="name"> Name </label>
						<input
							class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
							id="name"
							type="text"
							placeholder="Name"
							bind:value={workerConfig.name}
							required
						/>
					</div>
					<div class="mb-4">
						<label class="block text-gray-700 text-sm font-bold mb-2" for="id"> ID </label>
						<input
							class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
							id="id"
							type="text"
							placeholder="ID"
							bind:value={workerConfig.id}
						/>
					</div>
					<div class="mb-4">
						<label class="block text-gray-700 text-sm font-bold mb-2" for="wport"> Port </label>
						<input
							class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
							id="wport"
							type="text"
							placeholder="wport"
							bind:value={workerConfig.wport}
						/>
					</div>
					{#if !workerConfig.zeroconf}
						<div class="mb-4">
							<label class="block text-gray-700 text-sm font-bold mb-2" for="managerIp">
								Manager IP
							</label>
							<input
								class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
								id="managerIp"
								type="text"
								placeholder="IP"
								bind:value={workerConfig.ip}
								required
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
								bind:value={workerConfig.port}
								required
							/>
						</div>
					{/if}
					<div class="mb-4">
						<label class="block text-gray-700 text-sm font-bold mb-2" for="timeout">
							Timeout ({workerConfig.timeout} seconds)
						</label>
						<input
							type="range"
							min="5"
							max="100"
							id="timeout"
							class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-500"
							bind:value={workerConfig.timeout}
						/>
					</div>
					<div class="mb-4">
						<input id="zeroconf" type="checkbox" bind:checked={workerConfig.zeroconf} />
						<label class="ml-2" for="zeroconf">ZeroConf</label>
						<input
							class="ml-4"
							id="deletetemp"
							type="checkbox"
							bind:checked={workerConfig.delete_temp}
						/>
						<label class="ml-2" for="deletetemp">Delete Temporary</label>
					</div>
					<div>
						<button
							type="button"
							class="bg-blue-500
							   hover:bg-blue-700
							   disabled:opacity-50
							   disabled:cursor-not-allowed
							   text-white
							   font-bold
							   py-2
							   px-4
							   rounded
							   mr-4"
							on:click={handleStartAndConnect}
							disabled={!canCreateWorker || connecting || connected}
							>{connecting ? 'Connecting' : 'Start and Connect'}
						</button>
					</div>
				</form>
			{/if}
		</div>
		<div class="w-1/2 bg-gray-200 p-4">
			<h2 class="text-2xl mb-4">Worker State</h2>
			<!-- JSON Viewer -->
			<pre>{JSON.stringify(workerState, null, 2)}</pre>
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
<Alert bind:this={errorDisplay} />
