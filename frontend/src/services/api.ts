/**
 * Client API pour le backend DatavizFT
 */

import axios from 'axios';
import type {
  SkillEvolutionResponse,
  CityResponse,
  SourceResponse,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Récupère l'évolution des compétences
 */
export async function getSkillsEvolution(params: {
  source?: string | null;
  city?: string | null;
  start_date?: string;
  end_date?: string;
  top_n?: number;
}): Promise<SkillEvolutionResponse> {
  const cleanParams: Record<string, string | number> = {};

  if (params.source) cleanParams.source = params.source;
  if (params.city) cleanParams.city = params.city;
  if (params.start_date) cleanParams.start_date = params.start_date;
  if (params.end_date) cleanParams.end_date = params.end_date;
  if (params.top_n) cleanParams.top_n = params.top_n;

  const response = await apiClient.get<SkillEvolutionResponse>(
    '/api/skills/evolution',
    { params: cleanParams }
  );
  return response.data;
}

/**
 * Récupère les top villes
 */
export async function getTopCities(limit: number = 5): Promise<CityResponse[]> {
  const response = await apiClient.get<CityResponse[]>('/api/filters/cities', {
    params: { limit },
  });
  return response.data;
}

/**
 * Récupère les sources disponibles
 */
export async function getSources(): Promise<SourceResponse[]> {
  const response = await apiClient.get<SourceResponse[]>('/api/filters/sources');
  return response.data;
}
