import type { WorkerConfig, ResponseError, WorkerState } from './models';
import { Err, Ok } from 'ts-monads';
import type { Result } from 'ts-monads';

export class WorkerClient {
	private url: string;

	constructor(url: string) {
		this.url = url;
	}

	async getWorkerState(): Promise<Result<WorkerState, ResponseError>> {
		const response = await this._fetch('/state', {
			method: 'GET'
		});

		return response;
	}

	async start(config: WorkerConfig): Promise<Result<WorkerState, ResponseError>> {
		const response = await this._fetch<WorkerState>('/start', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(config)
		});

		return response;
	}

	async connect(config: WorkerConfig): Promise<Result<WorkerState, ResponseError>> {
		const response = await this._fetch<WorkerState>('/connect', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(config)
		});
		return response;
	}

	async shutdown(): Promise<Result<WorkerState, ResponseError>> {
		const response = await this._fetch<WorkerState>('/shutdown', {
			method: 'POST'
		});
		return response;
	}

	async disconnect(): Promise<Result<WorkerState, ResponseError>> {
		const response = await this._fetch<WorkerState>('/disconnect', {
			method: 'POST'
		});
		return response;
	}

	async _fetch<T>(prefix: string, options: RequestInit): Promise<Result<T, ResponseError>> {
		const res = await fetch(this.url + prefix, options);
		if (res.ok) {
			return new Ok<T>(await res.json());
		} else {
			if (res.status < 500) {
				return new Err({
					message: res.statusText,
					code: res.status,
					serverMessage: await res.json()
				});
			} else {
				return new Err({
					message: res.statusText,
					code: res.status,
					serverMessage: await res.text()
				});
			}
		}
	}
}
