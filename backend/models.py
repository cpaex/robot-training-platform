from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relaciones
    robots = relationship("Robot", back_populates="user", cascade="all, delete-orphan")
    simulations = relationship("Simulation", back_populates="user", cascade="all, delete-orphan")
    training_logs = relationship("TrainingLog", back_populates="user", cascade="all, delete-orphan")

class Robot(Base):
    __tablename__ = "robots"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    robot_type = Column(String(50), nullable=False)
    configuration = Column(JSON)
    status = Column(String(20), default="idle")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relaciones
    user = relationship("User", back_populates="robots")
    simulations = relationship("Simulation", back_populates="robot", cascade="all, delete-orphan")
    training_logs = relationship("TrainingLog", back_populates="robot", cascade="all, delete-orphan")

class Simulation(Base):
    __tablename__ = "simulations"

    id = Column(Integer, primary_key=True, index=True)
    robot_id = Column(Integer, ForeignKey("robots.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    status = Column(String(20), default="pending")  # pending, running, completed, failed
    parameters = Column(JSON)
    results = Column(JSON)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relaciones
    robot = relationship("Robot", back_populates="simulations")
    user = relationship("User", back_populates="simulations")
    training_logs = relationship("TrainingLog", back_populates="simulation", cascade="all, delete-orphan")

class TrainingLog(Base):
    __tablename__ = "training_logs"

    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(Integer, ForeignKey("simulations.id"), nullable=False)
    robot_id = Column(Integer, ForeignKey("robots.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    log_level = Column(String(10), default="INFO")  # DEBUG, INFO, WARNING, ERROR
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    simulation = relationship("Simulation", back_populates="training_logs")
    robot = relationship("Robot", back_populates="training_logs")
    user = relationship("User", back_populates="training_logs")
