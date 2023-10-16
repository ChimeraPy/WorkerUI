<script lang="ts">
	import { workerClient } from '$lib/services';
	import Alert from '$lib/Modal/Alert.svelte';
	import { isValidWorkerCreationConfig } from '$lib/Utils';

	let errorDisplay: Alert;

	let name: string = '';
	let id: string = '';
	let port: number = 0;
	let delete_temp: boolean = true;

	let starting = false;

	let canStartWorker: boolean = false;

	async function startWorker() {
		starting = true;
		(await workerClient.start({ name, id, port, delete_temp })).mapError((error) => {
			errorDisplay.display(error);
		});
		starting = false;
	}

	$: canStartWorker = isValidWorkerCreationConfig({ name, id, port, delete_temp });
</script>

<h2 class="text-2xl mb-4">Start Worker</h2>
<form>
	<div class="mb-4">
		<label class="block text-gray-700 text-sm font-bold mb-2" for="name"> Name </label>
		<input
			class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
			id="name"
			type="text"
			placeholder="Name"
			bind:value={name}
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
			bind:value={port}
		/>
	</div>
	<div class="mb-4">
		<input id="deletetemp" type="checkbox" bind:checked={delete_temp} />
		<label class="ml-2" for="deletetemp">Delete Temporary</label>
	</div>
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
		on:click={startWorker}
		disabled={!canStartWorker || starting}
		>{starting ? 'Starting' : 'Start'}
	</button>
</form>

<Alert bind:this={errorDisplay} />
