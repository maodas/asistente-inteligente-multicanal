import { useEffect, useState } from 'react';
import api from '../services/api';
import { Link } from 'react-router-dom';
import Layout from '../components/Layout';

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

  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleString('es-GT', {
      hour: '2-digit',
      minute: '2-digit',
      day: '2-digit',
      month: '2-digit',
    });
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="pb-5 border-b border-gray-200 sm:flex sm:items-center sm:justify-between">
        <h1 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl">
          Conversaciones activas
        </h1>
        <div className="mt-3 sm:mt-0 sm:ml-4">
          <span className="text-sm text-gray-500">
            Total: {conversations.length}
          </span>
        </div>
      </div>

      <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {conversations.map((conv) => (
          <Link
            key={conv.id}
            to={`/conversations/${conv.id}`}
            className="block bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200 overflow-hidden border border-gray-200"
          >
            <div className="p-5">
              <div className="flex justify-between items-start">
                <div className="truncate">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {conv.customer_phone || `Cliente #${conv.customer_id}`}
                  </p>
                  <p className="mt-1 text-xs text-gray-500">
                    {conv.last_message_time ? formatDate(conv.last_message_time) : 'Sin actividad'}
                  </p>
                </div>
                <span
                  className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    conv.status === 'human'
                      ? 'bg-green-100 text-green-800'
                      : 'bg-blue-100 text-blue-800'
                  }`}
                >
                  {conv.status === 'human' ? 'Humano' : 'Bot'}
                </span>
              </div>
              <p className="mt-2 text-sm text-gray-600 line-clamp-2">
                {conv.last_message || 'Sin mensajes'}
              </p>
            </div>
          </Link>
        ))}
      </div>

      {conversations.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500">No hay conversaciones aún.</p>
        </div>
      )}
    </Layout>
  );
}