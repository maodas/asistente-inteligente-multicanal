import { useEffect, useState } from 'react';
import api from '../services/api';
import { Link } from 'react-router-dom';

export default function Dashboard() {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);

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
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Conversaciones activas</h1>
      <div className="space-y-4">
        {conversations.map((conv) => (
          <Link
            key={conv.id}
            to={`/conversations/${conv.id}`}
            className="block p-4 border rounded-lg hover:shadow-md transition"
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
                  {new Date(conv.last_message_time).toLocaleString()}
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
  );
}