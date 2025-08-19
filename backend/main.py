from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn
import json
from datetime import datetime

from database import get_db, engine
from models import Base, User, Robot, Simulation, TrainingLog
from schemas import (
    UserCreate, UserResponse, RobotCreate, RobotResponse, 
    SimulationCreate, SimulationResponse, TrainingLogResponse,
    LoginRequest
)
from auth import get_current_user, create_access_token, verify_password, get_password_hash

# Crear tablas
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Robot Training Platform API",
    description="API para plataforma SaaS de entrenamiento de robots",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# Endpoints de autenticación
@app.post("/auth/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Registrar un nuevo usuario"""
    # Verificar si el usuario ya existe
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email ya registrado"
        )
    
    # Crear nuevo usuario con hash bcrypt
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@app.post("/auth/login")
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """Iniciar sesión de usuario"""
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )
    
    # Verificar contraseña
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )
    
    # Si la contraseña está en texto plano, convertirla a hash bcrypt
    if not user.password_hash.startswith('$2b$'):
        user.password_hash = get_password_hash(credentials.password)
        db.commit()
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# Endpoints de usuarios
@app.get("/users/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Obtener información del usuario actual"""
    return current_user

# Endpoints de robots
@app.post("/robots/", response_model=RobotResponse)
def create_robot(
    robot: RobotCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crear un nuevo robot"""
    db_robot = Robot(
        **robot.dict(),
        user_id=current_user.id
    )
    db.add(db_robot)
    db.commit()
    db.refresh(db_robot)
    return db_robot

@app.get("/robots/", response_model=List[RobotResponse])
def get_robots(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener lista de robots del usuario"""
    robots = db.query(Robot).filter(Robot.user_id == current_user.id).all()
    return robots

@app.get("/robots/{robot_id}", response_model=RobotResponse)
def get_robot(
    robot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener un robot específico"""
    robot = db.query(Robot).filter(
        Robot.id == robot_id,
        Robot.user_id == current_user.id
    ).first()
    
    if not robot:
        raise HTTPException(status_code=404, detail="Robot no encontrado")
    
    return robot

@app.put("/robots/{robot_id}", response_model=RobotResponse)
def update_robot(
    robot_id: int,
    robot_update: RobotCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualizar un robot"""
    db_robot = db.query(Robot).filter(
        Robot.id == robot_id,
        Robot.user_id == current_user.id
    ).first()
    
    if not db_robot:
        raise HTTPException(status_code=404, detail="Robot no encontrado")
    
    for field, value in robot_update.dict().items():
        setattr(db_robot, field, value)
    
    db_robot.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_robot)
    return db_robot

@app.delete("/robots/{robot_id}")
def delete_robot(
    robot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Eliminar un robot"""
    robot = db.query(Robot).filter(
        Robot.id == robot_id,
        Robot.user_id == current_user.id
    ).first()
    
    if not robot:
        raise HTTPException(status_code=404, detail="Robot no encontrado")
    
    db.delete(robot)
    db.commit()
    return {"message": "Robot eliminado"}

# Endpoints de simulaciones
@app.post("/simulations/", response_model=SimulationResponse)
def create_simulation(
    simulation: SimulationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crear una nueva simulación"""
    # Verificar que el robot pertenece al usuario
    robot = db.query(Robot).filter(
        Robot.id == simulation.robot_id,
        Robot.user_id == current_user.id
    ).first()
    
    if not robot:
        raise HTTPException(status_code=404, detail="Robot no encontrado")
    
    db_simulation = Simulation(
        **simulation.dict(),
        user_id=current_user.id
    )
    db.add(db_simulation)
    db.commit()
    db.refresh(db_simulation)
    return db_simulation

@app.get("/simulations/", response_model=List[SimulationResponse])
def get_simulations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener lista de simulaciones del usuario"""
    simulations = db.query(Simulation).filter(
        Simulation.user_id == current_user.id
    ).all()
    return simulations

@app.get("/simulations/{simulation_id}", response_model=SimulationResponse)
def get_simulation(
    simulation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener una simulación específica"""
    simulation = db.query(Simulation).filter(
        Simulation.id == simulation_id,
        Simulation.user_id == current_user.id
    ).first()
    
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulación no encontrada")
    
    return simulation

@app.put("/simulations/{simulation_id}/start")
def start_simulation(
    simulation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Iniciar una simulación"""
    simulation = db.query(Simulation).filter(
        Simulation.id == simulation_id,
        Simulation.user_id == current_user.id
    ).first()
    
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulación no encontrada")
    
    if simulation.status != "pending":
        raise HTTPException(status_code=400, detail="La simulación no está pendiente")
    
    simulation.status = "running"
    simulation.started_at = datetime.utcnow()
    simulation.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Simulación iniciada", "simulation_id": simulation_id}

@app.put("/simulations/{simulation_id}/complete")
def complete_simulation(
    simulation_id: int,
    results: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Completar una simulación con resultados"""
    simulation = db.query(Simulation).filter(
        Simulation.id == simulation_id,
        Simulation.user_id == current_user.id
    ).first()
    
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulación no encontrada")
    
    simulation.status = "completed"
    simulation.results = json.dumps(results)
    simulation.completed_at = datetime.utcnow()
    simulation.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Simulación completada", "simulation_id": simulation_id}

# Endpoints de logs
@app.get("/simulations/{simulation_id}/logs", response_model=List[TrainingLogResponse])
def get_simulation_logs(
    simulation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener logs de una simulación"""
    # Verificar que la simulación pertenece al usuario
    simulation = db.query(Simulation).filter(
        Simulation.id == simulation_id,
        Simulation.user_id == current_user.id
    ).first()
    
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulación no encontrada")
    
    logs = db.query(TrainingLog).filter(
        TrainingLog.simulation_id == simulation_id
    ).order_by(TrainingLog.timestamp.desc()).all()
    
    return logs

# Endpoint de health check
@app.get("/health")
def health_check():
    """Verificar estado del servicio"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# Endpoint raíz
@app.get("/")
def root():
    """Endpoint raíz con información de la API"""
    return {
        "message": "Robot Training Platform API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
