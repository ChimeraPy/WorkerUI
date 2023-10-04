export interface WorkerConfig {
	name: string;
	wport: number;
	delete_temp: boolean;
	id: string | undefined;
	zeroconf: boolean;
	ip: string | undefined;
	port: number | undefined;
	timeout: number | undefined;
}
