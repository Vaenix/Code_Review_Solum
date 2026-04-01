const DEFAULT_API_BASE_URL = 'http://127.0.0.1:8000/api';

function normalizeBaseUrl(value) {
    if (!value) {
        return DEFAULT_API_BASE_URL;
    }

    return value.endsWith('/') ? value.slice(0, -1) : value;
}

const BASE_URL = normalizeBaseUrl(import.meta.env.VITE_API_BASE_URL);

function buildQuery(params = {}) {
    const search = new URLSearchParams();

    Object.entries(params).forEach(([key, value]) => {
        if (value !== '' && value !== null && value !== undefined) {
            search.append(key, value);
        }
    });

    return search.toString() ? `?${search.toString()}` : '';
}

function getErrorMessage(error) {
    if (error instanceof Error && error.message) {
        return error.message;
    }

    return 'Unknown request error';
}

async function request(path, params = {}) {
    let response;

    try {
        response = await fetch(`${BASE_URL}${path}${buildQuery(params)}`);
    } catch (error) {
        throw new Error(`Unable to reach API at ${BASE_URL}. ${getErrorMessage(error)}`);
    }

    let payload = null;

    try {
        payload = await response.json();
    } catch (error) {
        if (response.ok) {
            throw new Error(`API returned invalid JSON for ${path}.`);
        }
    }

    if (!response.ok) {
        const detail = payload?.detail
            ? ` ${typeof payload.detail === 'string' ? payload.detail : JSON.stringify(payload.detail)}`
            : '';
        throw new Error(`Request failed (${response.status}).${detail}`);
    }

    if (payload === null || typeof payload !== 'object') {
        throw new Error(`API returned an unexpected payload for ${path}.`);
    }

    return payload;
}

export async function fetchFilters() {
    return request('/filters');
}

export async function fetchSummary(filters) {
    return request('/summary', filters);
}

export async function fetchTable(filters) {
    return request('/table', filters);
}

export async function fetchAnalysis(filters) {
    return request('/analysis', filters);
}
