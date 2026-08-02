"use client";

import ProtectedRoute from '@/components/ProtectedRoute';
import { useAuth } from '@/contexts/AuthContext';

export default function ResearcherDashboard() {
  const { user, logout } = useAuth();
  return (
    <ProtectedRoute allowedRoles={['Wildlife Researcher']}>
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex justify-between items-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900">Researcher Dashboard</h1>
            <button onClick={logout} className="text-sm font-medium text-red-600 hover:text-red-500">
              Sign Out
            </button>
          </div>
          <p className="text-gray-600">Welcome back, {user?.name}!</p>
          {/* Dashboard content for researcher */}
        </div>
      </div>
    </ProtectedRoute>
  );
}
