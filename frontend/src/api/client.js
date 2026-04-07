import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api",
});

const protectedPrefixes = ["/ingest", "/query", "/repos"];

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("auth_token");
  const requestUrl = config.url || "";

  const isProtected = protectedPrefixes.some((prefix) =>
    requestUrl.startsWith(prefix)
  );

  if (isProtected && token) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

export default api;
