from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime

# Schemas de Usuario
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Schemas de Robot
class RobotBase(BaseModel):
    name: str
    robot_type: str
    configuration: Optional[Dict[str, Any]] = None

class RobotCreate(RobotBase):
    pass

class RobotResponse(RobotBase):
    id: int
    user_id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Schemas de Simulación
class SimulationBase(BaseModel):
    name: str
    robot_id: int
    parameters: Optional[Dict[str, Any]] = None

class SimulationCreate(SimulationBase):
    pass

class SimulationResponse(SimulationBase):
    id: int
    user_id: int
    status: str
    results: Optional[Dict[str, Any]] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Schemas de Log de Entrenamiento
class TrainingLogBase(BaseModel):
    log_level: str = "INFO"
    message: str

class TrainingLogCreate(TrainingLogBase):
    simulation_id: int
    robot_id: int
    user_id: int

class TrainingLogResponse(TrainingLogBase):
    id: int
    simulation_id: int
    robot_id: int
    user_id: int
    timestamp: datetime

    class Config:
        from_attributes = True

# Schemas para actualizaciones
class RobotUpdate(BaseModel):
    name: Optional[str] = None
    robot_type: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None
    status: Optional[str] = None

class SimulationUpdate(BaseModel):
    name: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    results: Optional[Dict[str, Any]] = None

# Schemas para respuestas de API
class MessageResponse(BaseModel):
    message: str

class HealthResponse(BaseModel):
    status: str
    timestamp: str

# Schema para login
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
