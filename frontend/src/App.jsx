import { BrowserRouter, Routes, Route, Navigate, Link } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import ConversationDetail from './pages/ConversationDetail';
import Stats from './pages/Stats';

function PrivateRoute({ children }) {
  const { token, loading } = useAuth();
  if (loading) return <div className="text-center p-8">Cargando...</div>;
  return token ? children : <Navigate to="/login" />;
}

function NavBar() {
  const { logout } = useAuth();
  return (
    <nav className="bg-indigo-600 text-white p-4">
      <div className="container mx-auto flex justify-between items-center">
        <div className="space-x-4">
          <Link to="/dashboard" className="hover:underline">Conversaciones</Link>
          <Link to="/stats" className="hover:underline">Estadísticas</Link>
        </div>
        <button onClick={logout} className="bg-indigo-700 px-3 py-1 rounded hover:bg-indigo-800">
          Cerrar sesión
        </button>
      </div>
    </nav>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/dashboard"
          element={
            <PrivateRoute>
              <>
                <NavBar />
                <Dashboard />
              </>
            </PrivateRoute>
          }
        />
        <Route
          path="/stats"
          element={
            <PrivateRoute>
              <>
                <NavBar />
                <Stats />
              </>
            </PrivateRoute>
          }
        />
        <Route
          path="/conversations/:id"
          element={
            <PrivateRoute>
              <>
                <NavBar />
                <ConversationDetail />
              </>
            </PrivateRoute>
          }
        />
        <Route path="/" element={<Navigate to="/dashboard" />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;