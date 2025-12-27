/**
 * Application principale - Dashboard DatavizFT
 */

import { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Header } from './components/Header';
import { FiltersPanel } from './components/Filters';
import { SkillsEvolutionChart } from './components/Charts';
import { useSkillsEvolution, useTopCities, useSources } from './hooks/useSkillsData';
import type { Filters } from './types';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      refetchOnWindowFocus: false,
    },
  },
});

function Dashboard() {
  const [filters, setFilters] = useState<Filters>({
    source: null,
    city: null,
  });

  const { data: skillsData, isLoading: isLoadingSkills } = useSkillsEvolution(filters);
  const { data: cities = [], isLoading: isLoadingCities } = useTopCities(5);
  const { data: sources = [], isLoading: isLoadingSources } = useSources();

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <main className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
        <div className="space-y-6">
          {/* Filtres */}
          <FiltersPanel
            filters={filters}
            onFiltersChange={setFilters}
            cities={cities}
            sources={sources}
            isLoadingCities={isLoadingCities}
            isLoadingSources={isLoadingSources}
          />

          {/* Graphique principal */}
          <SkillsEvolutionChart
            data={skillsData?.data || []}
            isLoading={isLoadingSkills}
            totalJobs={skillsData?.total_jobs}
          />

          {/* Informations supplémentaires */}
          {skillsData && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
              <div className="flex flex-wrap gap-4 text-sm text-gray-600">
                <div>
                  <span className="font-medium">Période:</span>{' '}
                  {new Date(skillsData.period_start).toLocaleDateString('fr-FR')} -{' '}
                  {new Date(skillsData.period_end).toLocaleDateString('fr-FR')}
                </div>
                <div>
                  <span className="font-medium">Total offres:</span>{' '}
                  {skillsData.total_jobs.toLocaleString()}
                </div>
                {skillsData.filters.source && (
                  <div>
                    <span className="font-medium">Source:</span>{' '}
                    {skillsData.filters.source === 'francetravail'
                      ? 'France Travail'
                      : 'Adzuna'}
                  </div>
                )}
                {skillsData.filters.city && (
                  <div>
                    <span className="font-medium">Ville:</span>{' '}
                    {skillsData.filters.city}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </main>

      <footer className="mt-8 py-4 text-center text-sm text-gray-500">
        DatavizFT - Analyse du marché de l'emploi IT en France
      </footer>
    </div>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Dashboard />
    </QueryClientProvider>
  );
}

export default App;
