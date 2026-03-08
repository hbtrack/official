import axios from 'axios';
import {
  AiCoachApi,
  AthletesApi,
  AthleteTrainingApi,
  AttendanceApi,
  Configuration,
  ExerciseFavoritesApi,
  ExercisesApi,
  ExerciseTagsApi,
  SessionTemplatesApi,
  TrainingAlertsSuggestionsApi,
  TrainingCyclesApi,
  TrainingMicrocyclesApi,
  TrainingSessionsApi,
  UsersApi,
  WellnessPostApi,
  WellnessPreApi
} from '.';


// 1. Configuração base do Contrato
const apiConfig = new Configuration({
  basePath: "http://localhost:8000", // URL do seu FastAPI
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



// 4. Exportação dos Serviços Tipados
// Injetamos a instância do axios configurada dentro das classes geradas pelo OpenAPI
export const wellnessApi = new WellnessPreApi(apiConfig, apiConfig.basePath, axiosInstance);
export const wellnessPostApi = new WellnessPostApi(apiConfig, apiConfig.basePath, axiosInstance);
export const athletesApi = new AthletesApi(apiConfig, apiConfig.basePath, axiosInstance);
export const trainingApi = new TrainingSessionsApi(apiConfig, apiConfig.basePath, axiosInstance);
export const usersApi = new UsersApi(apiConfig, apiConfig.basePath, axiosInstance);
export const cyclesApi = new TrainingCyclesApi(apiConfig, apiConfig.basePath, axiosInstance);
export const microcyclesApi = new TrainingMicrocyclesApi(apiConfig, apiConfig.basePath, axiosInstance);
export const sessionTemplatesApi = new SessionTemplatesApi(apiConfig, apiConfig.basePath, axiosInstance);
export const exercisesApi = new ExercisesApi(apiConfig, apiConfig.basePath, axiosInstance);
export const exerciseTagsApi = new ExerciseTagsApi(apiConfig, apiConfig.basePath, axiosInstance);
export const exerciseFavoritesApi = new ExerciseFavoritesApi(apiConfig, apiConfig.basePath, axiosInstance);
export const athleteTrainingApi = new AthleteTrainingApi(apiConfig, apiConfig.basePath, axiosInstance);
export const aiCoachApi = new AiCoachApi(apiConfig, apiConfig.basePath, axiosInstance);
export const attendanceApi = new AttendanceApi(apiConfig, apiConfig.basePath, axiosInstance);
export const trainingAlertsSuggestionsApi = new TrainingAlertsSuggestionsApi(apiConfig, apiConfig.basePath, axiosInstance);

export default axiosInstance;

