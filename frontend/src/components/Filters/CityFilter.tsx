/**
 * Filtre par ville
 */

interface CityFilterProps {
  value: string | null;
  onChange: (city: string | null) => void;
  cities: { name: string; job_count: number }[];
  isLoading?: boolean;
}

export function CityFilter({
  value,
  onChange,
  cities,
  isLoading,
}: CityFilterProps) {
  return (
    <div className="flex flex-col space-y-2">
      <label className="text-sm font-medium text-gray-700">Ville</label>
      {isLoading ? (
        <div className="text-sm text-gray-500">Chargement...</div>
      ) : (
        <select
          value={value || ''}
          onChange={(e) => onChange(e.target.value || null)}
          className="block w-full px-3 py-2 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-sm"
        >
          <option value="">Toutes les villes</option>
          {cities.map((city) => (
            <option key={city.name} value={city.name}>
              {city.name} ({city.job_count.toLocaleString()} offres)
            </option>
          ))}
        </select>
      )}
    </div>
  );
}
