import axios from "axios";

// Берём URL API из переменной окружения
const API_URL = import.meta.env.VITE_API_URL || "";

// Настраиваем глобальный baseURL
axios.defaults.baseURL = API_URL;

// Автоматически добавляем /api когда это нужно
axios.interceptors.request.use((config) => {
  // Если путь не содержит http и не начинается с /api — добавляем
  if (!config.url.startsWith("http")) {
    config.url = config.url.startsWith("/")
      ? config.url
      : "/" + config.url;
  }
  return config;
});

export default axios;
