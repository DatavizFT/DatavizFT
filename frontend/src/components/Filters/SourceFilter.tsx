/**
 * Filtre par source de données
 */

interface SourceFilterProps {
  value: string | null;
  onChange: (source: string | null) => void;
  sources: { name: string; job_count: number }[];
  isLoading?: boolean;
}

export function SourceFilter({
  value,
  onChange,
  sources,
  isLoading,
}: SourceFilterProps) {
  const allSources = [
    { name: 'global', label: 'Global', job_count: sources.reduce((acc, s) => acc + s.job_count, 0) },
    ...sources.map(s => ({ ...s, label: s.name === 'francetravail' ? 'France Travail' : 'Adzuna' })),
  ];

  return (
    <div className="flex flex-col space-y-2">
      <label className="text-sm font-medium text-gray-700">Source</label>
      <div className="flex flex-wrap gap-2">
        {isLoading ? (
          <div className="text-sm text-gray-500">Chargement...</div>
        ) : (
          allSources.map((source) => (
            <button
              key={source.name}
              onClick={() => onChange(source.name === 'global' ? null : source.name)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                (value === null && source.name === 'global') ||
                value === source.name
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {source.label}
              <span className="ml-2 text-xs opacity-75">
                ({source.job_count.toLocaleString()})
              </span>
            </button>
          ))
        )}
      </div>
    </div>
  );
}
