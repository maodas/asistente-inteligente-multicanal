import { createContext, useState, useContext, useEffect } from 'react';
import { login as apiLogin } from '../services/auth';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      // Aquí podrías verificar el token o cargar datos del usuario
      setLoading(false);
    } else {
      setLoading(false);
    }
  }, [token]);

  const login = async (username, password) => {
    const data = await apiLogin(username, password);
    localStorage.setItem('token', data.access_token);
    setToken(data.access_token);
    return data;
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);