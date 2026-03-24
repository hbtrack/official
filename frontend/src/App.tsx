function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold tracking-tight text-gray-900">
            HB Track
          </h1>
        </div>
      </header>
      <main>
        <div className="mx-auto max-w-7xl py-6 sm:px-6 lg:px-8">
          <div className="px-4 py-6 sm:px-0">
            <div className="rounded-lg border-4 border-dashed border-gray-200 bg-white p-6">
              <h2 className="text-lg font-medium text-gray-900">
                Welcome to HB Track - Phase 5 Frontend
              </h2>
              <p className="mt-2 text-sm text-gray-600">
                React + TypeScript + Vite frontend development in progress.
              </p>
              <p className="mt-4 text-sm text-gray-600">
                <strong>Modules to implement:</strong>
              </p>
              <ul className="mt-2 list-inside list-disc space-y-1 text-sm text-gray-600">
                <li>Authentication & Authorization</li>
                <li>User Management</li>
                <li>Team Management</li>
                <li>Season Management</li>
                <li>Training Management</li>
              </ul>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default App
