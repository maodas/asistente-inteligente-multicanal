import { useEffect, useState } from 'react';
import api from '../services/api';

export default function Stats() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await api.get('/stats/');
        setStats(res.data);
      } catch (error) {
        console.error('Error fetching stats:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  if (loading) return <div className="text-center p-8">Cargando estadísticas...</div>;

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Estadísticas</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-gray-500 text-sm uppercase">Total Conversaciones</h2>
          <p className="text-4xl font-bold">{stats.total_conversations}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-gray-500 text-sm uppercase">Total Mensajes</h2>
          <p className="text-4xl font-bold">{stats.total_messages}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-gray-500 text-sm uppercase">Conversaciones Humanas</h2>
          <p className="text-4xl font-bold">{stats.conversations_by_status.human}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-gray-500 text-sm uppercase mb-4">Conversaciones por estado</h2>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span>Bot</span>
              <span className="font-semibold">{stats.conversations_by_status.bot}</span>
            </div>
            <div className="flex justify-between">
              <span>Humano</span>
              <span className="font-semibold">{stats.conversations_by_status.human}</span>
            </div>
            <div className="flex justify-between">
              <span>Finalizadas</span>
              <span className="font-semibold">{stats.conversations_by_status.ended}</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-gray-500 text-sm uppercase mb-4">Mensajes por remitente</h2>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span>Cliente</span>
              <span className="font-semibold">{stats.messages_by_sender.customer}</span>
            </div>
            <div className="flex justify-between">
              <span>Bot</span>
              <span className="font-semibold">{stats.messages_by_sender.bot}</span>
            </div>
            <div className="flex justify-between">
              <span>Humano</span>
              <span className="font-semibold">{stats.messages_by_sender.human}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}