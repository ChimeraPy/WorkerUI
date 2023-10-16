<script lang="ts">
	import {
		Table,
		TableHead,
		TableHeadCell,
		TableBodyCell,
		TableBody,
		TableBodyRow
	} from 'flowbite-svelte';
	import { onMount } from 'svelte';
	import { workerClient } from '$lib/services';
	import { getStore } from '$lib/stores';
	import Alert from '$lib/Modal/Alert.svelte';

	const workerStateStore = getStore('worker');
	let errorDisplay;
	let workerConfig = {
		name: '',
		id: '',
		wport: 0,
		delete_temp: false,
		zeroconf: true,
		port: 0,
		timeout: 20,
		ip: ''
	};
	let connected = false;
	let connecting = false;
	let disconnecting = false;

	onMount(async function () {
		(await workerClient.getWorkerState())
			.map((state) => {
				connected = state.connected_to_manager;
			})
			.mapError((err) => {
				errorDisplay.display({
					title: 'Error getting worker state',
					message: err.message
				});
			});
	});

	function getNodes(workerState) {
		if (workerState.nodes === undefined) {
			return 'Unknown';
		}
		return Object.values(workerState.nodes)
			.map((node) => `${node.name}(${node.fsm})`)
			.join(', ');
	}

	async function handleShutdown() {
		(await workerClient.shutdown()).mapError((err) => {
			errorDisplay.display({
				title: 'Error shutting down worker',
				content: err
			});
		});
	}

	async function toggleConnection() {
		if (connected) {
			// Disconnect
			disconnecting = true;
			await disconnect();
			disconnecting = false;
		} else {
			connecting = true;
			await connect();
			connecting = false;
		}
	}

	async function connect() {
		(await workerClient.connect(workerConfig)).mapError((err) => {
			errorDisplay.display({
				title: 'Error connecting to manager',
				content: err
			});
		});
	}

	async function disconnect() {
		(await workerClient.disconnect()).mapError((err) => {
			errorDisplay.display({
				title: 'Error disconnecting from manager',
				content: err
			});
		});
	}

	$: {
		connected = $workerStateStore?.connected_to_manager;
		workerConfig.name = $workerStateStore?.name;
		workerConfig.id = $workerStateStore?.id;
		workerConfig.wport = $workerStateStore?.port;
	}
</script>

<h2 class="text-2xl mb-4">Worker {connected ? 'Connected' : 'Started'}</h2>
<Table hoverable={true} class="mb-4">
	<TableHead>
		<TableHeadCell>Name</TableHeadCell>
		<TableBodyCell>ID</TableBodyCell>
		<TableHeadCell>URL</TableHeadCell>
		<TableHeadCell>Nodes</TableHeadCell>
	</TableHead>
	<TableBody class="divide-y">
		<TableBodyRow>
			<TableBodyCell>{$workerStateStore?.name}</TableBodyCell>
			<TableBodyCell>{$workerStateStore?.id}</TableBodyCell>
			<TableBodyCell>{`http://${$workerStateStore?.ip}:${$workerStateStore?.port}`}</TableBodyCell>
			<TableBodyCell tdClass="px-6 py-4 font-medium"
				>{getNodes($workerStateStore || {})}</TableBodyCell
			>
		</TableBodyRow>
	</TableBody>
</Table>

{#if !connected}
	{#if !workerConfig.zeroconf}
		<div class="mb-4">
			<label class="block text-gray-700 text-sm font-bold mb-2" for="managerIp"> Manager IP </label>
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
	</div>
{/if}

<div class="flex justify-center">
	{#if !connected}
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
			disabled={connecting}
			on:click={toggleConnection}
			>{connecting ? 'Connecting' : 'Connect'}
		</button>
	{:else}
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
			disabled={disconnecting}
			on:click={toggleConnection}
			>{disconnecting ? 'Disconnecting' : 'Disconnect'}
		</button>
	{/if}

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
		on:click={handleShutdown}
		>{'shutdown'}
	</button>
</div>

<Alert bind:this={errorDisplay} />
