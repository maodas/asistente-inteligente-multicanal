import { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import Layout from '../components/Layout';

export default function ConversationDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [conversation, setConversation] = useState(null);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    fetchConversation();
  }, [id]);

  useEffect(() => {
    scrollToBottom();
  }, [conversation?.messages]);

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
      fetchConversation();
    } catch (error) {
      console.error('Error al tomar control:', error);
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim() || sending) return;
    setSending(true);
    try {
      await api.post(`/conversations/${id}/messages`, {
        content: newMessage,
        sender: 'human'
      });
      setNewMessage('');
      fetchConversation();
    } catch (error) {
      console.error('Error enviando mensaje:', error);
    } finally {
      setSending(false);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
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

  if (!conversation) {
    return (
      <Layout>
        <div className="text-center py-12">
          <p className="text-gray-500">Conversación no encontrada</p>
        </div>
      </Layout>
    );
  }

  const customerInfo = conversation.customer?.phone_number || `Cliente #${conversation.customer_id}`;

  return (
    <Layout>
      <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{customerInfo}</h1>
          <p className="text-sm text-gray-500">
            Estado: {conversation.status === 'human' ? 'Atendido por humano' : 'Atendido por bot'}
          </p>
        </div>
        <div className="flex gap-2">
          {conversation.status === 'bot' && (
            <button
              onClick={takeControl}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-amber-600 hover:bg-amber-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-amber-500"
            >
              Tomar control
            </button>
          )}
          <button
            onClick={() => navigate('/dashboard')}
            className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Volver
          </button>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="h-96 overflow-y-auto p-4 space-y-4" id="message-container">
          {conversation.messages.map((msg) => {
            const isCustomer = msg.sender === 'customer';
            const isBot = msg.sender === 'bot';
            const isHuman = msg.sender === 'human';

            return (
              <div
                key={msg.id}
                className={`flex ${isCustomer ? 'justify-start' : 'justify-end'}`}
              >
                <div
                  className={`max-w-xs md:max-w-md lg:max-w-lg xl:max-w-xl px-4 py-2 rounded-lg ${
                    isCustomer
                      ? 'bg-gray-100 text-gray-800'
                      : isBot
                      ? 'bg-blue-50 text-gray-800'
                      : 'bg-green-50 text-gray-800'
                  }`}
                >
                  <p className="text-xs font-medium mb-1 text-gray-500">
                    {isCustomer ? 'Cliente' : isBot ? 'Bot' : 'Agente'}
                  </p>
                  <p className="text-sm whitespace-pre-wrap break-words">{msg.content}</p>
                  <p className="text-xs text-gray-400 mt-1 text-right">
                    {new Date(msg.created_at).toLocaleTimeString('es-GT', {
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </p>
                </div>
              </div>
            );
          })}
          <div ref={messagesEndRef} />
        </div>

        <div className="border-t border-gray-200 p-4">
          <form onSubmit={sendMessage} className="flex gap-2">
            <input
              type="text"
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              placeholder={conversation.status === 'bot' 
                ? "Toma el control para responder..." 
                : "Escribe tu mensaje como agente..."
              }
              disabled={conversation.status === 'bot' || sending}
              className="flex-1 rounded-md border border-gray-300 px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:text-gray-400"
            />
            <button
              type="submit"
              disabled={conversation.status === 'bot' || sending || !newMessage.trim()}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-blue-300 disabled:cursor-not-allowed"
            >
              {sending ? 'Enviando...' : 'Enviar'}
            </button>
          </form>
          {conversation.status === 'bot' && (
            <p className="mt-2 text-sm text-amber-600">
              Esta conversación está siendo atendida por el bot. Toma el control para responder como humano.
            </p>
          )}
        </div>
      </div>
    </Layout>
  );
}