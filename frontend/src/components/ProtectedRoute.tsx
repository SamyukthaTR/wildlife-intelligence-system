"use client";

import { useAuth, RoleEnum } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { useEffect, ReactNode } from 'react';

interface ProtectedRouteProps {
  children: ReactNode;
  allowedRoles?: RoleEnum[];
}

export default function ProtectedRoute({ children, allowedRoles }: ProtectedRouteProps) {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading) {
      if (!user) {
        router.push('/login');
      } else if (allowedRoles && !allowedRoles.includes(user.role)) {
        // Explicitly check role to prevent URL tampering
        const dashboardRoutes: Record<RoleEnum, string> = {
          'Wildlife Researcher': '/dashboards/researcher',
          'Conservation Officer': '/dashboards/conservation-officer',
          'Forest Department Officer': '/dashboards/forest-officer',
          'Administrator': '/dashboards/admin',
        };
        router.push(dashboardRoutes[user.role]);
      }
    }
  }, [user, loading, router, allowedRoles]);

  if (loading || !user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-green-600"></div>
      </div>
    );
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return null; // Prevents flashing content before redirect
  }

  return <>{children}</>;
}
