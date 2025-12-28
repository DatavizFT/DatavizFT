/**
 * Panneau de filtres du dashboard
 */

import { SourceFilter } from './SourceFilter';
import { CityFilter } from './CityFilter';
import type { Filters, CityResponse, SourceResponse } from '../../types';

interface FiltersPanelProps {
  filters: Filters;
  onFiltersChange: (filters: Filters) => void;
  cities: CityResponse[];
  sources: SourceResponse[];
  isLoadingCities?: boolean;
  isLoadingSources?: boolean;
}

export function FiltersPanel({
  filters,
  onFiltersChange,
  cities,
  sources,
  isLoadingCities,
  isLoadingSources,
}: FiltersPanelProps) {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Filtres</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <SourceFilter
          value={filters.source}
          onChange={(source) => onFiltersChange({ ...filters, source })}
          sources={sources}
          isLoading={isLoadingSources}
        />
        <CityFilter
          value={filters.city}
          onChange={(city) => onFiltersChange({ ...filters, city })}
          cities={cities}
          isLoading={isLoadingCities}
        />
      </div>
    </div>
  );
}

export { SourceFilter } from './SourceFilter';
export { CityFilter } from './CityFilter';
