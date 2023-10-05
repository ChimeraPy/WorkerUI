export interface ResponseError {
	message: string;
	code: number;
}

export interface WorkerConfig {
	name: string;
	wport: number;
	delete_temp: boolean;
	id: string | undefined;
	zeroconf: boolean;
	port: number | undefined;
	timeout: number | undefined;
	ip: string | undefined;
}

export interface RegisteredMethod {
	name: string;
	style: string;
	params: { [key: string]: string };
}

export interface NodeDiagnostics {
	timestamp: string;
	latency: number;
	payload_size: number;
	memory_usage: number;
	cpu_usage: number;
	num_of_steps: number;
}

export interface NodeState {
	id: string;
	name: string;
	port: number;
	fsm:
		| 'NULL'
		| 'INITIALIZED'
		| 'CONNECTED'
		| 'READY'
		| 'PREVIEWING'
		| 'RECORDING'
		| 'STOPPED'
		| 'SAVED'
		| 'SHUTDOWN';
	registered_methods: { [key: string]: RegisteredMethod };
	logdir: string;
	diagonostics: NodeDiagnostics;
}

export interface WorkerState {
	id: string;
	name: string;
	nodes: { [key: string]: NodeState };
	ip: string;
	port: number;
	tempfolder: string;
}
