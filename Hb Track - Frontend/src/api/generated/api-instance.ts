import axios from 'axios';
import {
  AthletesApi,
  Configuration,
  TrainingSessionsApi,
  UsersApi,
  WellnessPostApi,
  WellnessPreApi
} from './generated';

// 1. Configuração base do Contrato
const apiConfig = new Configuration({
  basePath: "http://localhost:8000", // URL do seu FastAPI
  withCredentials: true,             // Necessário para persistência de cookies (CSRF/Auth)
});

// 2. Instância do Axios com Interceptores
const axiosInstance = axios.create({
  baseURL: apiConfig.basePath,
  withCredentials: true,
});

axiosInstance.interceptors.request.use((config) => {
  // 1. Rastreabilidade
  config.headers['X-Request-ID'] = crypto.randomUUID();
  
  // 2. TOKEN DE AUTENTICAÇÃO (O que está faltando para resolver o 401)
  // Ajuste o nome da chave ('token' ou 'access_token') conforme o seu login
  const token = localStorage.getItem('access_token'); 
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }

  // 3. Contexto da Organização
  const orgId = localStorage.getItem('active_organization_id');
  if (orgId) {
    config.headers['X-Organization-ID'] = orgId;
  }

  // 4. Segurança CSRF (para métodos de escrita)
  if (config.method !== 'get') {
    const csrfToken = document.cookie
      .split('; ')
      .find(row => row.startsWith('csrftoken='))
      ?.split('=')[1];
    
    if (csrfToken) {
      config.headers['X-CSRF-Token'] = csrfToken;
    }
  }

  return config;
});

// 

// 3. Interceptor de Requisição: Adiciona os headers obrigatórios
axiosInstance.interceptors.request.use((config) => {
  // Rastreabilidade: Gera um Request-ID único por chamada
  config.headers['X-Request-ID'] = crypto.randomUUID();
  
  // Contexto: Recupera a organização ativa (ex: do localStorage ou estado global)
  const orgId = localStorage.getItem('active_organization_id');
  if (orgId) {
    config.headers['X-Organization-ID'] = orgId;
  }

  // Segurança: Sincroniza o Token CSRF para métodos de escrita (POST, PUT, DELETE, PATCH)
  if (config.method !== 'get') {
    const csrfToken = document.cookie
      .split('; ')
      .find(row => row.startsWith('csrftoken='))
      ?.split('=')[1];
    
    if (csrfToken) {
      config.headers['X-CSRF-Token'] = csrfToken;
    }
  }

  return config;
});

// 4. Exportação dos Serviços Tipados
// Injetamos a instância do axios configurada dentro das classes geradas pelo OpenAPI
export const wellnessApi = new WellnessPreApi(apiConfig, apiConfig.basePath, axiosInstance);
export const wellnessPostApi = new WellnessPostApi(apiConfig, apiConfig.basePath, axiosInstance);
export const athletesApi = new AthletesApi(apiConfig, apiConfig.basePath, axiosInstance);
export const trainingApi = new TrainingSessionsApi(apiConfig, apiConfig.basePath, axiosInstance);
export const usersApi = new UsersApi(apiConfig, apiConfig.basePath, axiosInstance);

export default axiosInstance;

