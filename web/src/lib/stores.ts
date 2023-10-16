import type { WorkerState } from './models';
import readableWebSocketStore from './ReadableWebSocketStore';
import { dev } from '$app/environment';

const stores = new Map<string, any>();
export function populateStores() {
	const workerStateStore = readableWebSocketStore<WorkerState>(
		dev ? '/api/updates' : '/updates',
		null,
		(payload) => payload.data
	);
	stores.set('worker', workerStateStore);
}

export function getStore<T>(name: string): T {
	return stores.get(name);
}
