import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';

export default function Dashboard() {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const { logout } = useAuth();

  useEffect(() => {
    const fetchConversations = async () => {
      try {
        const res = await api.get('/conversations/');
        setConversations(res.data);
      } catch (error) {
        console.error('Error fetching conversations:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchConversations();
  }, []);

  if (loading) return <div className="text-center p-8">Cargando...</div>;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navbar simple */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center space-x-8">
              <h1 className="text-xl font-semibold text-gray-900">
                Asistente Inteligente
              </h1>
              <div className="flex space-x-4">
                <Link
                  to="/dashboard"
                  className="text-gray-700 hover:text-indigo-600 px-3 py-2 rounded-md text-sm font-medium"
                >
                  Conversaciones
                </Link>
                <Link
                  to="/stats"
                  className="text-gray-700 hover:text-indigo-600 px-3 py-2 rounded-md text-sm font-medium"
                >
                  Estadísticas
                </Link>
              </div>
            </div>
            <div className="flex items-center">
              <button
                onClick={logout}
                className="text-gray-500 hover:text-gray-700 text-sm"
              >
                Cerrar sesión
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Contenido principal */}
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <h2 className="text-2xl font-bold mb-6">Conversaciones activas</h2>
          <div className="space-y-4">
            {conversations.map((conv) => (
              <Link
                key={conv.id}
                to={`/conversations/${conv.id}`}
                className="block p-4 border rounded-lg hover:shadow-md transition bg-white"
              >
                <div className="flex justify-between items-center">
                  <div>
                    <p className="font-semibold">
                      {conv.customer_phone || `Cliente #${conv.customer_id}`}
                    </p>
                    <p className="text-sm text-gray-600">
                      Último mensaje: {conv.last_message || 'Sin mensajes'}
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      conv.status === 'human' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-blue-100 text-blue-800'
                    }`}>
                      {conv.status === 'human' ? 'Humano' : 'Bot'}
                    </span>
                    <span className="text-xs text-gray-500">
                      {conv.last_message_time ? new Date(conv.last_message_time).toLocaleString() : ''}
                    </span>
                  </div>
                </div>
              </Link>
            ))}
            {conversations.length === 0 && (
              <p className="text-gray-500">No hay conversaciones aún.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}