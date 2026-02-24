import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';

export default function ConversationDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [conversation, setConversation] = useState(null);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchConversation();
  }, [id]);

  const fetchConversation = async () => {
    try {
      const res = await api.get(`/conversations/${id}`);
      setConversation(res.data);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const takeControl = async () => {
    try {
      await api.post(`/conversations/${id}/take-control`);
      fetchConversation(); // recargar para ver el cambio de estado
    } catch (error) {
      console.error('Error al tomar control:', error);
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim()) return;
    try {
      await api.post(`/conversations/${id}/messages`, {
        content: newMessage,
        sender: 'human'
      });
      setNewMessage('');
      fetchConversation(); // recargar mensajes
    } catch (error) {
      console.error('Error enviando mensaje:', error);
    }
  };

  if (loading) return <div className="text-center p-8">Cargando...</div>;
  if (!conversation) return <div className="text-center p-8">Conversación no encontrada</div>;

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">
          Conversación con {conversation.customer?.phone_number || `Cliente #${conversation.customer_id}`}
        </h1>
        <div className="space-x-2">
          {conversation.status === 'bot' && (
            <button
              onClick={takeControl}
              className="bg-yellow-500 text-white px-4 py-2 rounded hover:bg-yellow-600"
            >
              Tomar control
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

      <div className="border rounded-lg p-4 h-96 overflow-y-auto mb-4 bg-gray-50">
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
                {new Date(msg.created_at).toLocaleTimeString()}
              </p>
            </div>
          </div>
        ))}
      </div>

      <form onSubmit={sendMessage} className="flex space-x-2">
        <input
          type="text"
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          placeholder="Escribe tu mensaje como agente..."
          className="flex-1 border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          disabled={conversation.status === 'bot'}
        />
        <button
          type="submit"
          disabled={conversation.status === 'bot'}
          className="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 disabled:bg-gray-400"
        >
          Enviar
        </button>
      </form>
      {conversation.status === 'bot' && (
        <p className="text-sm text-yellow-600 mt-2">
          Esta conversación está en modo bot. Toma el control para responder como humano.
        </p>
      )}
    </div>
  );
}