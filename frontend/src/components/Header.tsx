/**
 * Header du Dashboard DatavizFT
 */

export function Header() {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">D</span>
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">DatavizFT</h1>
              <p className="text-sm text-gray-500">
                Dashboard des compétences IT
              </p>
            </div>
          </div>
          <div className="text-sm text-gray-500">
            Marché de l'emploi IT en France
          </div>
        </div>
      </div>
    </header>
  );
}
