import { useEffect, useState } from 'react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

export default function Stats() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { logout } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      setLoading(true);
      const res = await api.get('/stats/');
      setStats(res.data);
    } catch (err) {
      console.error('Error fetching stats:', err);
      setError('No se pudieron cargar las estadísticas');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (loading) return <div className="text-center p-8">Cargando estadísticas...</div>;
  if (error) return <div className="text-center p-8 text-red-500">{error}</div>;
  if (!stats) return <div className="text-center p-8">No hay datos</div>;

  // Asegurar que conversations_by_status existe (por si la API no lo devuelve)
  const byStatus = stats.conversations_by_status || { bot: 0, human: 0, ended: 0 };
  const bySender = stats.messages_by_sender || { customer: 0, bot: 0, human: 0 };

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold">Estadísticas</h1>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/dashboard')}
                className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
              >
                Volver al Dashboard
              </button>
              <button
                onClick={handleLogout}
                className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
              >
                Cerrar sesión
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Tarjeta: Total conversaciones */}
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <dt className="text-sm font-medium text-gray-500 truncate">
                  Total conversaciones
                </dt>
                <dd className="mt-1 text-3xl font-semibold text-gray-900">
                  {stats.total_conversations}
                </dd>
              </div>
            </div>

            {/* Tarjeta: Conversaciones últimas 24h */}
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <dt className="text-sm font-medium text-gray-500 truncate">
                  Últimas 24 horas
                </dt>
                <dd className="mt-1 text-3xl font-semibold text-gray-900">
                  {stats.conversations_last_24h}
                </dd>
              </div>
            </div>

            {/* Tarjeta: Total mensajes */}
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <dt className="text-sm font-medium text-gray-500 truncate">
                  Total mensajes
                </dt>
                <dd className="mt-1 text-3xl font-semibold text-gray-900">
                  {stats.total_messages}
                </dd>
              </div>
            </div>

            {/* Tarjeta: Promedio mensajes por conversación */}
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <dt className="text-sm font-medium text-gray-500 truncate">
                  Promedio mensajes/conv.
                </dt>
                <dd className="mt-1 text-3xl font-semibold text-gray-900">
                  {stats.avg_messages_per_conversation}
                </dd>
              </div>
            </div>

            {/* Gráfico de estados (simulado con números) */}
            <div className="bg-white overflow-hidden shadow rounded-lg col-span-1 md:col-span-2 lg:col-span-2">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Conversaciones por estado</h3>
                <div className="space-y-3">
                  <div>
                    <div className="flex justify-between mb-1">
                      <span className="text-sm font-medium text-blue-700">Bot</span>
                      <span className="text-sm font-medium text-gray-700">{byStatus.bot}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2.5">
                      <div className="bg-blue-600 h-2.5 rounded-full" style={{ width: `${stats.total_conversations ? (byStatus.bot / stats.total_conversations) * 100 : 0}%` }}></div>
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between mb-1">
                      <span className="text-sm font-medium text-green-700">Humano</span>
                      <span className="text-sm font-medium text-gray-700">{byStatus.human}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2.5">
                      <div className="bg-green-600 h-2.5 rounded-full" style={{ width: `${stats.total_conversations ? (byStatus.human / stats.total_conversations) * 100 : 0}%` }}></div>
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between mb-1">
                      <span className="text-sm font-medium text-gray-700">Cerrada</span>
                      <span className="text-sm font-medium text-gray-700">{byStatus.ended}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2.5">
                      <div className="bg-gray-600 h-2.5 rounded-full" style={{ width: `${stats.total_conversations ? (byStatus.ended / stats.total_conversations) * 100 : 0}%` }}></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Mensajes por emisor */}
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Mensajes por emisor</h3>
                <dl className="space-y-2">
                  <div className="flex justify-between">
                    <dt className="text-sm text-gray-600">Cliente:</dt>
                    <dd className="text-sm font-medium text-gray-900">{bySender.customer}</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-sm text-gray-600">Bot:</dt>
                    <dd className="text-sm font-medium text-gray-900">{bySender.bot}</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-sm text-gray-600">Agente:</dt>
                    <dd className="text-sm font-medium text-gray-900">{bySender.human}</dd>
                  </div>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}