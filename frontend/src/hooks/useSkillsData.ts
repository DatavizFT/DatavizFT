/**
 * Custom hooks pour les données du dashboard
 */

import { useQuery } from '@tanstack/react-query';
import { getSkillsEvolution, getTopCities, getSources } from '../services/api';
import type { Filters } from '../types';

/**
 * Hook pour récupérer l'évolution des compétences
 */
export function useSkillsEvolution(filters: Filters) {
  return useQuery({
    queryKey: ['skillsEvolution', filters],
    queryFn: () =>
      getSkillsEvolution({
        source: filters.source,
        city: filters.city,
        top_n: 10,
      }),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Hook pour récupérer les top villes
 */
export function useTopCities(limit: number = 5) {
  return useQuery({
    queryKey: ['topCities', limit],
    queryFn: () => getTopCities(limit),
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}

/**
 * Hook pour récupérer les sources
 */
export function useSources() {
  return useQuery({
    queryKey: ['sources'],
    queryFn: getSources,
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}
