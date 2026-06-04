const normalizeUrl = (value: string) => value.trim().replace(/\/+$/, '');

export const getApiBaseUrl = (): string => {
  const raw = import.meta.env.VITE_API_URL?.trim();

  if (!raw) {
    return '/api';
  }

  const normalized = normalizeUrl(raw);

  if (normalized.startsWith('/')) {
    return normalized;
  }

  if (normalized.endsWith('/api')) {
    return normalized;
  }

  return `${normalized}/api`;
};

export const getApiOrigin = (): string => {
  const baseUrl = getApiBaseUrl();

  if (baseUrl.startsWith('/')) {
    return '';
  }

  return baseUrl.replace(/\/api$/, '');
};
