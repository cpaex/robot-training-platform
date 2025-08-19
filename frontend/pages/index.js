import { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function Home() {
  const [user, setUser] = useState(null);
  const [robots, setRobots] = useState([]);
  const [simulations, setSimulations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [token, setToken] = useState('');

  // Estados para formularios
  const [loginForm, setLoginForm] = useState({ email: '', password: '' });
  const [robotForm, setRobotForm] = useState({ name: '', robot_type: '', configuration: '' });
  const [simulationForm, setSimulationForm] = useState({ name: '', robot_id: '', parameters: '' });

  // Configurar axios con interceptor para token
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    }
  }, [token]);

  // Función de login
  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await axios.post(`${API_BASE_URL}/auth/login`, loginForm);
      setToken(response.data.access_token);
      setUser({ email: loginForm.email });
      await fetchUserData();
    } catch (err) {
      setError('Error en login: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  // Función de logout
  const handleLogout = () => {
    setToken('');
    setUser(null);
    setRobots([]);
    setSimulations([]);
    delete axios.defaults.headers.common['Authorization'];
  };

  // Obtener datos del usuario
  const fetchUserData = async () => {
    try {
      const [robotsRes, simulationsRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/robots/`),
        axios.get(`${API_BASE_URL}/simulations/`)
      ]);
      setRobots(robotsRes.data);
      setSimulations(simulationsRes.data);
    } catch (err) {
      console.error('Error obteniendo datos:', err);
    }
  };

  // Crear robot
  const handleCreateRobot = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const robotData = {
        ...robotForm,
        configuration: robotForm.configuration ? JSON.parse(robotForm.configuration) : null
      };
      
      await axios.post(`${API_BASE_URL}/robots/`, robotData);
      setRobotForm({ name: '', robot_type: '', configuration: '' });
      await fetchUserData();
    } catch (err) {
      setError('Error creando robot: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  // Crear simulación
  const handleCreateSimulation = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const simulationData = {
        ...simulationForm,
        robot_id: parseInt(simulationForm.robot_id),
        parameters: simulationForm.parameters ? JSON.parse(simulationForm.parameters) : null
      };
      
      await axios.post(`${API_BASE_URL}/simulations/`, simulationData);
      setSimulationForm({ name: '', robot_id: '', parameters: '' });
      await fetchUserData();
    } catch (err) {
      setError('Error creando simulación: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  // Iniciar simulación
  const startSimulation = async (simulationId) => {
    try {
      await axios.put(`${API_BASE_URL}/simulations/${simulationId}/start`);
      await fetchUserData();
    } catch (err) {
      setError('Error iniciando simulación: ' + (err.response?.data?.detail || err.message));
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="max-w-md w-full space-y-8">
          <div>
            <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
              Robot Training Platform
            </h2>
            <p className="mt-2 text-center text-sm text-gray-600">
              Inicia sesión para acceder a tu plataforma
            </p>
          </div>
          <form className="mt-8 space-y-6" onSubmit={handleLogin}>
            <div className="rounded-md shadow-sm -space-y-px">
              <div>
                <input
                  type="email"
                  required
                  className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                  placeholder="Email"
                  value={loginForm.email}
                  onChange={(e) => setLoginForm({ ...loginForm, email: e.target.value })}
                />
              </div>
              <div>
                <input
                  type="password"
                  required
                  className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                  placeholder="Contraseña"
                  value={loginForm.password}
                  onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
                />
              </div>
            </div>

            {error && (
              <div className="text-red-600 text-sm text-center">{error}</div>
            )}

            <div>
              <button
                type="submit"
                disabled={loading}
                className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
              >
                {loading ? 'Iniciando...' : 'Iniciar Sesión'}
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">Robot Training Platform</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-gray-700">Bienvenido, {user.email}</span>
              <button
                onClick={handleLogout}
                className="bg-red-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-red-700"
              >
                Cerrar Sesión
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {error && (
          <div className="mb-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Sección de Robots */}
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">Mis Robots</h3>
              
              <form onSubmit={handleCreateRobot} className="mb-4 space-y-3">
                <input
                  type="text"
                  placeholder="Nombre del robot"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  value={robotForm.name}
                  onChange={(e) => setRobotForm({ ...robotForm, name: e.target.value })}
                  required
                />
                <input
                  type="text"
                  placeholder="Tipo de robot"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  value={robotForm.robot_type}
                  onChange={(e) => setRobotForm({ ...robotForm, robot_type: e.target.value })}
                  required
                />
                <textarea
                  placeholder="Configuración (JSON opcional)"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  value={robotForm.configuration}
                  onChange={(e) => setRobotForm({ ...robotForm, configuration: e.target.value })}
                  rows="2"
                />
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
                >
                  Crear Robot
                </button>
              </form>

              <div className="space-y-2">
                {robots.map((robot) => (
                  <div key={robot.id} className="border border-gray-200 rounded-md p-3">
                    <h4 className="font-medium">{robot.name}</h4>
                    <p className="text-sm text-gray-600">Tipo: {robot.robot_type}</p>
                    <p className="text-sm text-gray-600">Estado: {robot.status}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Sección de Simulaciones */}
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">Mis Simulaciones</h3>
              
              <form onSubmit={handleCreateSimulation} className="mb-4 space-y-3">
                <input
                  type="text"
                  placeholder="Nombre de la simulación"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  value={simulationForm.name}
                  onChange={(e) => setSimulationForm({ ...simulationForm, name: e.target.value })}
                  required
                />
                <select
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  value={simulationForm.robot_id}
                  onChange={(e) => setSimulationForm({ ...simulationForm, robot_id: e.target.value })}
                  required
                >
                  <option value="">Seleccionar robot</option>
                  {robots.map((robot) => (
                    <option key={robot.id} value={robot.id}>
                      {robot.name}
                    </option>
                  ))}
                </select>
                <textarea
                  placeholder="Parámetros (JSON opcional)"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  value={simulationForm.parameters}
                  onChange={(e) => setSimulationForm({ ...simulationForm, parameters: e.target.value })}
                  rows="2"
                />
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 disabled:opacity-50"
                >
                  Crear Simulación
                </button>
              </form>

              <div className="space-y-2">
                {simulations.map((simulation) => (
                  <div key={simulation.id} className="border border-gray-200 rounded-md p-3">
                    <h4 className="font-medium">{simulation.name}</h4>
                    <p className="text-sm text-gray-600">Estado: {simulation.status}</p>
                    {simulation.status === 'pending' && (
                      <button
                        onClick={() => startSimulation(simulation.id)}
                        className="mt-2 bg-yellow-600 text-white px-3 py-1 rounded text-sm hover:bg-yellow-700"
                      >
                        Iniciar
                      </button>
                    )}
                    {simulation.status === 'completed' && simulation.results && (
                      <div className="mt-2 text-sm text-gray-600">
                        <p>Accuracy: {(JSON.parse(simulation.results).accuracy * 100).toFixed(1)}%</p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
