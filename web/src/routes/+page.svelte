<script lang="ts">
	import { onMount } from 'svelte';
	import { workerClient } from '$lib/services';
	import type { WorkerConfig } from '../lib/models';
	import { isValidWorkerCreationConfig, isValidWorkerConnectionConfig } from '$lib/Utils';
	import Alert from '$lib/Modal/Alert.svelte';
	import { getStore } from '../lib/stores';

	import WorkerStarter from './Components/WorkerStarter.svelte';
	import WorkerDetails from './Components/WorkerDetails.svelte';

	let errorDisplay;
	let canCreateWorker: boolean = false;
	let canConnectWorker: boolean = false;
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
	let workerState = {};
	let started: boolean = false;

	const workerStateStore = getStore('worker');

	onMount(async () => {
		// Get worker state
		(await workerClient.getWorkerState()).map((state) => {
			workerState = state;
		});
	});

	$: {
		started = $workerStateStore?.name !== undefined;
	}
</script>

<div class="flex flex-col min-h-screen">
	<!-- Header -->
	<header class="bg-gray-600 text-white p-4 text-3xl">ChimeraPy Worker</header>

	<!-- Main Content -->
	<main class="flex-grow flex">
		<div class="w-1/2 p-4">
			{#if !started}
				<WorkerStarter />
			{:else}
				<WorkerDetails />
			{/if}
		</div>
		<div class="w-1/2 bg-gray-200 p-4">
			<h2 class="text-2xl mb-4">Worker State</h2>
			<!-- JSON Viewer -->
			<pre>{JSON.stringify($workerStateStore || workerState, null, 2)}</pre>
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
