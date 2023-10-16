// This can be false if you're using a fallback (i.e. SPA mode)
export const ssr = false;
export const prerender = true;
import type { LayoutLoad } from './$types';
import { populateStores } from '$lib/stores';

export const load: LayoutLoad = ({ fetch }) => {
	populateStores();
	return {};
};
