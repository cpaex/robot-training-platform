# Robot Training Platform - PoC SaaS

Una plataforma SaaS completa para entrenamiento de robots con FastAPI, SQLite, Docker Compose y un runner de simulaciones dummy.

## 🚀 Características

- **Backend FastAPI**: API REST completa con autenticación JWT
- **Base de datos SQLite**: Persistencia de datos con SQLAlchemy ORM
- **Runner de simulaciones**: Servicio que procesa simulaciones pendientes
- **Frontend React**: Interfaz web simple y moderna
- **Docker Compose**: Orquestación completa de servicios
- **Autenticación segura**: Sistema de usuarios con JWT
- **Gestión de robots**: CRUD completo para robots
- **Simulaciones**: Creación y seguimiento de entrenamientos
- **Logs en tiempo real**: Seguimiento del progreso de simulaciones

## 🏗️ Arquitectura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (SQLite)      │
│   Port: 3000    │    │   Port: 8000    │    │   Port: 5432    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                ▲
                                │
                       ┌─────────────────┐
                       │ Simulation      │
                       │ Runner          │
                       │ (Dummy)         │
                       └─────────────────┘
```

## 📋 Prerrequisitos

- Docker
- Docker Compose
- Git

## 🚀 Instalación y Ejecución

### 1. Clonar el repositorio
```bash
git clone <repository-url>
cd robot-training-cloud
```

### 2. Ejecutar con Docker Compose
```bash
docker-compose up --build
```

### 3. Acceder a los servicios
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Documentación API**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🔧 Configuración

### Variables de Entorno
Las siguientes variables se pueden configurar en el archivo `docker-compose.yml`:

- `SECRET_KEY`: Clave secreta para JWT (cambiar en producción)
- `DATABASE_URL`: URL de la base de datos SQLite
- `BACKEND_URL`: URL del backend para el runner

### Base de Datos
La base de datos se inicializa automáticamente con:
- Usuario demo: `demo@example.com` / `demo_password_hash`
- Robot demo preconfigurado
- Tablas para usuarios, robots, simulaciones y logs

## 📱 Uso de la Plataforma

### 1. Registro/Login
- Usar las credenciales demo o registrar un nuevo usuario
- El sistema genera un token JWT para autenticación

### 2. Gestión de Robots
- Crear robots con nombre, tipo y configuración
- Ver lista de robots del usuario
- Actualizar y eliminar robots

### 3. Crear Simulaciones
- Seleccionar un robot para entrenar
- Configurar parámetros de la simulación
- Iniciar el proceso de entrenamiento

### 4. Seguimiento
- Monitorear estado de simulaciones en tiempo real
- Ver logs de entrenamiento
- Revisar resultados finales

## 🔌 API Endpoints

### Autenticación
- `POST /auth/register` - Registrar usuario
- `POST /auth/login` - Iniciar sesión

### Usuarios
- `GET /users/me` - Información del usuario actual

### Robots
- `POST /robots/` - Crear robot
- `GET /robots/` - Listar robots del usuario
- `GET /robots/{id}` - Obtener robot específico
- `PUT /robots/{id}` - Actualizar robot
- `DELETE /robots/{id}` - Eliminar robot

### Simulaciones
- `POST /simulations/` - Crear simulación
- `GET /simulations/` - Listar simulaciones del usuario
- `GET /simulations/{id}` - Obtener simulación específica
- `PUT /simulations/{id}/start` - Iniciar simulación
- `PUT /simulations/{id}/complete` - Completar simulación
- `GET /simulations/{id}/logs` - Obtener logs de simulación

## 🧪 Runner de Simulaciones

El servicio `simulation-runner` es un worker que:
- Monitorea simulaciones pendientes en la base de datos
- Simula el proceso de entrenamiento paso a paso
- Actualiza el estado y resultados de las simulaciones
- Genera logs detallados del proceso
- Maneja errores y fallos de manera robusta

### Proceso de Simulación
1. **Inicialización**: Configuración del entorno
2. **Carga de modelo**: Preparación del robot
3. **Configuración**: Ajuste de sensores y actuadores
4. **Entrenamiento**: Ejecución de algoritmos
5. **Validación**: Verificación de resultados
6. **Finalización**: Generación de reportes

## 🛠️ Desarrollo

### Estructura del Proyecto
```
robot-training-cloud/
├── backend/                 # Backend FastAPI
│   ├── main.py             # Aplicación principal
│   ├── models.py           # Modelos SQLAlchemy
│   ├── schemas.py          # Esquemas Pydantic
│   ├── auth.py             # Sistema de autenticación
│   ├── database.py         # Configuración de BD
│   ├── requirements.txt    # Dependencias Python
│   └── Dockerfile          # Imagen Docker
├── simulation-runner/       # Servicio de simulaciones
│   ├── simulation_runner.py # Lógica del runner
│   ├── requirements.txt    # Dependencias Python
│   └── Dockerfile          # Imagen Docker
├── frontend/               # Frontend React
│   ├── pages/              # Páginas de la aplicación
│   ├── package.json        # Dependencias Node.js
│   └── Dockerfile          # Imagen Docker
├── data/                   # Volumen de datos (SQLite)
├── docker-compose.yml      # Orquestación de servicios
├── init_db.sh             # Script de inicialización de BD
└── README.md              # Este archivo
```

### Comandos de Desarrollo

#### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

#### Runner
```bash
cd simulation-runner
pip install -r requirements.txt
python simulation_runner.py
```

## 🔒 Seguridad

- **JWT Tokens**: Autenticación stateless segura
- **Hash de contraseñas**: Bcrypt para almacenamiento seguro
- **Validación de datos**: Pydantic para validación de entrada
- **CORS configurado**: Para desarrollo y producción
- **Isolación de usuarios**: Cada usuario solo ve sus datos

## 📊 Monitoreo

- **Health Checks**: Endpoint `/health` para verificar estado
- **Logs estructurados**: Logging detallado en todos los servicios
- **Métricas de simulaciones**: Seguimiento de rendimiento
- **Estado en tiempo real**: Actualizaciones automáticas de estado

## 🚀 Escalabilidad

La arquitectura está diseñada para escalar:
- **Microservicios**: Separación clara de responsabilidades
- **Base de datos**: Fácil migración a PostgreSQL/MySQL
- **Runner distribuido**: Múltiples instancias del runner
- **Load balancing**: Fácil agregar más instancias del backend
- **Cache**: Preparado para implementar Redis

## 🐛 Troubleshooting

### Problemas Comunes

1. **Puertos ocupados**: Verificar que los puertos 3000, 8000 y 5432 estén libres
2. **Permisos de base de datos**: El directorio `data/` debe ser escribible
3. **Dependencias**: Ejecutar `docker-compose build --no-cache` si hay problemas de dependencias

### Logs
```bash
# Ver logs de todos los servicios
docker-compose logs

# Ver logs de un servicio específico
docker-compose logs backend
docker-compose logs simulation-runner
docker-compose logs frontend
```

### Reiniciar servicios
```bash
# Reiniciar un servicio específico
docker-compose restart backend

# Reiniciar todos los servicios
docker-compose restart
```

## 📈 Próximos Pasos

- [ ] Implementar base de datos PostgreSQL
- [ ] Agregar sistema de notificaciones
- [ ] Implementar métricas y analytics
- [ ] Agregar más tipos de robots
- [ ] Implementar algoritmos reales de entrenamiento
- [ ] Agregar sistema de facturación
- [ ] Implementar multi-tenancy
- [ ] Agregar tests automatizados
- [ ] Implementar CI/CD pipeline

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 📞 Soporte

Para soporte técnico o preguntas:
- Crear un issue en el repositorio
- Contactar al equipo de desarrollo
- Revisar la documentación de la API en `/docs`

---

**Nota**: Este es un PoC (Proof of Concept) y no está listo para producción. Implementar medidas de seguridad adicionales antes de usar en un entorno de producción.
