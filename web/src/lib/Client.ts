import type { WorkerConfig } from './models';

export class WorkerClient {
	private url: string;

	constructor(url: string) {
		this.url = url;
	}

	async getWorkerState() {
		const response = await this._fetch('/state', {
			method: 'GET'
		});

		return await response.json();
	}

	async connectWorker(config: WorkerConfig) {
		return await this._fetch('/connect', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(config)
		});
	}

	async _fetch(path: string, init?: RequestInit) {
		const response = await fetch(`${this.url}${path}`, init);
		if (!response.ok) {
			throw new Error(response.statusText);
		}
		return response;
	}
}
