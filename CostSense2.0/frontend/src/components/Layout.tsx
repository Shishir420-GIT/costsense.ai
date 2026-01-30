import { Outlet } from 'react-router-dom'
import { DollarSign } from 'lucide-react'

export default function Layout() {
  return (
    <div className="min-h-screen bg-ey-black">
      <nav className="bg-ey-grey-dark border-b border-ey-yellow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <DollarSign className="h-8 w-8 text-ey-yellow" />
              <span className="ml-2 text-xl font-bold text-white">
                CostSense AI
              </span>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-400">
                Multi-Cloud Cost Intelligence
              </span>
            </div>
          </div>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>
    </div>
  )
}
