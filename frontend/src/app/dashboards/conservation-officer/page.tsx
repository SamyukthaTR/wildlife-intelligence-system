"use client";

import { useState, useEffect } from 'react';
import ProtectedRoute from '@/components/ProtectedRoute';
import { useAuth } from '@/contexts/AuthContext';
import api from '@/lib/api';

// Types
type Site = { id: number, location_name: string, latitude: number, longitude: number, habitat_type: string, protected_area: string };
type Survey = { id: number, site_id: number, survey_date: string, status: string };
type Device = { id: number, site_id: number, device_type: string, serial: string };
type Observation = { id: number, survey_id: number, file_type: string, uploaded_at: string, processing_status: string };

export default function ConservationOfficerDashboard() {
  const { user, logout } = useAuth();
  
  // Data State
  const [sites, setSites] = useState<Site[]>([]);
  const [surveys, setSurveys] = useState<Survey[]>([]);
  const [devices, setDevices] = useState<Device[]>([]);
  const [observations, setObservations] = useState<Observation[]>([]);
  const [loading, setLoading] = useState(true);
  const [viewingFileUrl, setViewingFileUrl] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      const [sitesRes, surveysRes, devicesRes, obsRes] = await Promise.all([
        api.get('/monitoring/sites'),
        api.get('/monitoring/surveys'),
        api.get('/monitoring/devices'),
        api.get('/observations')
      ]);
      setSites(sitesRes.data);
      setSurveys(surveysRes.data);
      setDevices(devicesRes.data);
      setObservations(obsRes.data);
    } catch (err) {
      console.error("Failed to load dashboard data", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleViewFile = async (obsId: number, fileType: string) => {
    try {
      const response = await api.get(`/observations/${obsId}/file`, {
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      
      // If it's an image, we can show it in a simple modal overlay
      if (fileType === 'image') {
        setViewingFileUrl(url);
      } else {
        // For audio, just trigger a download for simplicity
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `observation_${obsId}.mp3`);
        document.body.appendChild(link);
        link.click();
        link.parentNode?.removeChild(link);
      }
    } catch (err) {
      console.error("Failed to download file", err);
      alert("Failed to access file. You may not have permission.");
    }
  };

  // Helper to find device info for an observation
  const getDeviceInfo = (surveyId: number) => {
    const survey = surveys.find(s => s.id === surveyId);
    if (!survey) return { type: 'N/A', serial: 'N/A' };
    const device = devices.find(d => d.site_id === survey.site_id);
    if (!device) return { type: 'N/A', serial: 'N/A' };
    return { type: device.device_type, serial: device.serial };
  };

  return (
    <ProtectedRoute allowedRoles={['Conservation Officer']}>
      <div className="min-h-screen bg-slate-50 p-8 font-sans">
        
        {/* Simple Modal for Images */}
        {viewingFileUrl && (
          <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
            <div className="relative bg-white p-4 rounded-xl max-w-4xl max-h-screen">
              <button onClick={() => setViewingFileUrl(null)} className="absolute -top-4 -right-4 bg-rose-500 text-white rounded-full p-2 hover:bg-rose-600 font-bold">
                Close
              </button>
              <img src={viewingFileUrl} alt="Observation" className="max-w-full max-h-[80vh] rounded-lg" />
            </div>
          </div>
        )}

        <div className="max-w-7xl mx-auto space-y-8">
          
          {/* Header */}
          <div className="flex justify-between items-center bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
            <div>
              <h1 className="text-3xl font-extrabold text-slate-800 tracking-tight">Global Park Overview</h1>
              <p className="text-slate-500 mt-1">Conservation Officer: {user?.name}</p>
            </div>
            <button onClick={logout} className="px-5 py-2.5 bg-rose-50 text-rose-600 hover:bg-rose-100 rounded-xl font-medium transition-colors">
              Sign Out
            </button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            
            {/* Sites Overview */}
            <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
              <h2 className="text-xl font-bold text-slate-800 mb-6">Active Monitoring Sites</h2>
              {loading ? (
                <div className="text-slate-500">Loading sites...</div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left border-collapse">
                    <thead>
                      <tr className="bg-slate-50 border-y border-slate-200 text-slate-600 text-sm">
                        <th className="py-3 px-4 font-medium">Location</th>
                        <th className="py-3 px-4 font-medium">Coordinates</th>
                      </tr>
                    </thead>
                    <tbody>
                      {sites.map(site => (
                        <tr key={site.id} className="border-b border-slate-100 hover:bg-slate-50/50">
                          <td className="py-3 px-4 text-slate-900 font-medium">{site.location_name}</td>
                          <td className="py-3 px-4 text-slate-600 text-sm">{site.latitude.toString()}, {site.longitude.toString()}</td>
                        </tr>
                      ))}
                      {sites.length === 0 && (
                        <tr>
                          <td colSpan={2} className="py-8 text-center text-slate-500">No monitoring sites created yet.</td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              )}
            </div>

            {/* Observations Summary */}
            <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
              <h2 className="text-xl font-bold text-slate-800 mb-6">Recent Observations Pipeline</h2>
              {loading ? (
                <div className="text-slate-500">Loading observations...</div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left border-collapse">
                    <thead>
                      <tr className="bg-slate-50 border-y border-slate-200 text-slate-600 text-sm">
                        <th className="py-3 px-4 font-medium">Survey</th>
                        <th className="py-3 px-4 font-medium">File Type</th>
                        <th className="py-3 px-4 font-medium">Device (Serial)</th>
                        <th className="py-3 px-4 font-medium">Status</th>
                        <th className="py-3 px-4 font-medium">Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {observations.map(obs => {
                        const deviceInfo = getDeviceInfo(obs.survey_id);
                        return (
                          <tr key={obs.id} className="border-b border-slate-100 hover:bg-slate-50/50">
                            <td className="py-3 px-4 text-slate-600 text-sm">Survey #{obs.survey_id}</td>
                            <td className="py-3 px-4 text-slate-600 text-sm capitalize">{obs.file_type}</td>
                            <td className="py-3 px-4 text-slate-600 text-sm">
                              <span className="capitalize block">{deviceInfo.type.replace('_', ' ')}</span>
                              <span className="text-xs text-slate-400 font-mono">{deviceInfo.serial}</span>
                            </td>
                            <td className="py-3 px-4">
                              <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${obs.processing_status === 'pending' ? 'bg-amber-100 text-amber-700' : 'bg-emerald-100 text-emerald-700'}`}>
                                {obs.processing_status}
                              </span>
                            </td>
                            <td className="py-3 px-4">
                              <button onClick={() => handleViewFile(obs.id, obs.file_type)} className="text-indigo-600 hover:text-indigo-800 font-medium text-sm px-3 py-1 bg-indigo-50 hover:bg-indigo-100 rounded-lg transition-colors whitespace-nowrap">
                                View File
                              </button>
                            </td>
                          </tr>
                        );
                      })}
                      {observations.length === 0 && (
                        <tr>
                          <td colSpan={5} className="py-8 text-center text-slate-500">No observations uploaded yet.</td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              )}
            </div>

          </div>

        </div>
      </div>
    </ProtectedRoute>
  );
}
