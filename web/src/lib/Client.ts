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

	async connect(config: WorkerConfig) {
		const response = await this._fetch('/connect', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(config)
		});
		return await response.json() as WorkerConfig;
	}

	async _fetch(path: string, init?: RequestInit): Promise<Response> {
		const response = await fetch(`${this.url}${path}`, init);
		if (!response.ok) {
			throw new Error(response.statusText);
		}
		return response;
	}
}
