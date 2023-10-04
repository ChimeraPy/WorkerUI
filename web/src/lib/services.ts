import { dev } from '$app/environment';
import { WorkerClient } from './Client';

const URL = dev ? '/api' : '';

export const workerClient = new WorkerClient(URL);
