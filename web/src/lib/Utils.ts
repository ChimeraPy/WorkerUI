import type {WorkerConfig} from './models';

const isValidIP = (ip: string): boolean => {
    const ipRegex = /^(\d{1,3}\.){3}\d{1,3}$/;
    return ipRegex.test(ip) || ip === 'localhost';
}
export const isValidWorkerCreationConfig = (config: WorkerConfig): boolean => {
    const isFalsy = (value: any): boolean => value === '' || value === null || value === undefined || value === 0;
    if (isFalsy(config.name)) return false;

    if (!config.zeroconf) {
        return !isFalsy(config.port) && !isFalsy(config.ip) && isValidIP(config.ip || '');
    }

    return true;
}
