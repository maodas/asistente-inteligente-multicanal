import { useEffect, useState } from 'react';
import api from '../services/api';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

export default function Dashboard() {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all'); // 'all', 'bot', 'human'
  const { logout } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    fetchConversations();
  }, [filter]);

  const fetchConversations = async () => {
    try {
      const params = filter !== 'all' ? { status: filter } : {};
      const res = await api.get('/conversations/', { params });
      setConversations(res.data);
    } catch (error) {
      console.error('Error fetching conversations:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (loading) return <div className="text-center p-8">Cargando...</div>;

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold">Asistente Inteligente</h1>
            </div>
            <div className="flex items-center space-x-4">
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
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold">Conversaciones activas</h2>
            <div className="flex space-x-2">
              <select
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                className="border rounded px-3 py-2"
              >
                <option value="all">Todas</option>
                <option value="bot">Bot</option>
                <option value="human">Humano</option>
              </select>
            </div>
          </div>

          <div className="space-y-4">
            {conversations.length === 0 ? (
              <p className="text-gray-500">No hay conversaciones.</p>
            ) : (
              conversations.map((conv) => (
                <Link
                  key={conv.id}
                  to={`/conversations/${conv.id}`}
                  className="block p-4 border rounded-lg bg-white hover:shadow-md transition"
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
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}