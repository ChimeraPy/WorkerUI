import { readableWebSocketStore } from './ReadableWebSocketStore';
import type {WorkerState} from "./models";

const stores = new Map<string, any>();

export function populateStores() {
    const updateStore = readableWebSocketStore<string>('/updates', null, (payload) => payload.data);
    stores.set('updates', updateStore);
}

export function getStore<T>(name: string): T|null {
    return stores.get(name);
}
