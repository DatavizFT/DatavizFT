/**
 * Types TypeScript pour le Dashboard DatavizFT
 */

export interface SkillEvolutionPoint {
  date: string;
  skill: string;
  count: number;
}

export interface SkillEvolutionResponse {
  data: SkillEvolutionPoint[];
  total_jobs: number;
  period_start: string;
  period_end: string;
  filters: {
    source: string | null;
    city: string | null;
  };
}

export interface CityResponse {
  name: string;
  job_count: number;
}

export interface SourceResponse {
  name: string;
  job_count: number;
}

export interface Filters {
  source: string | null;
  city: string | null;
}
