import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';

export default function ConversationDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [conversation, setConversation] = useState(null);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [closing, setClosing] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchConversation();
    const interval = setInterval(fetchConversation, 5000);
    return () => clearInterval(interval);
  }, [id]);

  const fetchConversation = async () => {
    try {
      const res = await api.get(`/conversations/${id}`);
      setConversation(res.data);
      setError('');
    } catch (error) {
      console.error('Error:', error);
      setError('Error al cargar la conversación');
    } finally {
      setLoading(false);
    }
  };

  const takeControl = async () => {
    try {
      await api.post(`/conversations/${id}/take-control`);
      fetchConversation();
    } catch (error) {
      console.error('Error al tomar control:', error);
      setError('No se pudo tomar el control');
    }
  };

  const closeConversation = async () => {
    if (!window.confirm('¿Estás seguro de cerrar esta conversación?')) return;
    setClosing(true);
    try {
      await api.post(`/conversations/${id}/close`);
      fetchConversation();
    } catch (error) {
      console.error('Error al cerrar conversación:', error);
      setError('No se pudo cerrar la conversación');
    } finally {
      setClosing(false);
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim() || sending) return;
    setSending(true);
    setError('');
    try {
      await api.post(`/conversations/${id}/messages`, {
        content: newMessage,
        sender: 'human'
      });
      setNewMessage('');
      fetchConversation(); // recargar mensajes
    } catch (error) {
      console.error('Error enviando mensaje:', error);
      setError('No se pudo enviar el mensaje. Intenta de nuevo.');
    } finally {
      setSending(false);
    }
  };

  if (loading) return <div className="text-center p-8">Cargando...</div>;
  if (!conversation) return <div className="text-center p-8">Conversación no encontrada</div>;

  const isActive = conversation.status !== 'ended';
  const isHuman = conversation.status === 'human';
  const isBot = conversation.status === 'bot';

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold">Asistente Inteligente</h1>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-4xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="bg-white shadow overflow-hidden sm:rounded-lg">
          <div className="px-4 py-5 sm:px-6 flex justify-between items-center">
            <div>
              <h2 className="text-lg leading-6 font-medium text-gray-900">
                Conversación con {conversation.customer?.phone_number || `Cliente #${conversation.customer_id}`}
              </h2>
              <p className="mt-1 max-w-2xl text-sm text-gray-500">
                Estado: {conversation.status === 'bot' ? 'Bot' : conversation.status === 'human' ? 'Humano' : 'Cerrada'}
              </p>
            </div>
            <div className="space-x-2">
              {isBot && (
                <button
                  onClick={takeControl}
                  className="bg-yellow-500 text-white px-4 py-2 rounded hover:bg-yellow-600"
                >
                  Tomar control
                </button>
              )}
              {isActive && (
                <button
                  onClick={closeConversation}
                  disabled={closing}
                  className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600 disabled:bg-red-300"
                >
                  {closing ? 'Cerrando...' : 'Cerrar conversación'}
                </button>
              )}
              <button
                onClick={() => navigate('/dashboard')}
                className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
              >
                Volver
              </button>
            </div>
          </div>

          {error && (
            <div className="px-4 py-2 bg-red-100 text-red-700 border-l-4 border-red-500">
              {error}
            </div>
          )}

          <div className="border-t border-gray-200">
            <div className="p-4 h-96 overflow-y-auto bg-gray-50">
              {conversation.messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`mb-3 flex ${
                    msg.sender === 'customer' ? 'justify-start' : 'justify-end'
                  }`}
                >
                  <div
                    className={`max-w-xs md:max-w-md px-4 py-2 rounded-lg ${
                      msg.sender === 'customer'
                        ? 'bg-white border'
                        : msg.sender === 'bot'
                        ? 'bg-blue-100'
                        : 'bg-green-100'
                    }`}
                  >
                    <p className="text-xs text-gray-500 mb-1">
                      {msg.sender === 'customer' ? 'Cliente' : msg.sender === 'bot' ? 'Bot' : 'Agente'}
                    </p>
                    <p>{msg.content}</p>
                    <p className="text-xs text-gray-400 mt-1">
                      {new Date(msg.created_at).toLocaleString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>

            {isActive ? (
              <form onSubmit={sendMessage} className="p-4 border-t flex space-x-2">
                <input
                  type="text"
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  placeholder={isHuman ? "Escribe tu mensaje como agente..." : "Conversación en modo bot, toma el control para responder"}
                  className="flex-1 border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  disabled={!isHuman || sending}
                />
                <button
                  type="submit"
                  disabled={!isHuman || sending}
                  className="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 disabled:bg-gray-400"
                >
                  {sending ? 'Enviando...' : 'Enviar'}
                </button>
              </form>
            ) : (
              <div className="p-4 border-t bg-gray-100 text-center text-gray-500">
                Esta conversación está cerrada.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}