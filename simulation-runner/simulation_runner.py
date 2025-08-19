#!/usr/bin/env python3
"""
Runner de simulaciones dummy para la plataforma de entrenamiento de robots.
Este servicio procesa simulaciones pendientes y simula el entrenamiento.
"""

import time
import json
import random
import requests
import sqlite3
import os
from datetime import datetime
from typing import Dict, Any, Optional
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimulationRunner:
    def __init__(self):
        self.database_path = os.getenv("DATABASE_URL", "sqlite:///app/data/robot_training.db")
        self.backend_url = os.getenv("BACKEND_URL", "http://backend:8000")
        self.running = True
        
        # Convertir URL de SQLite a path de archivo
        if self.database_path.startswith("sqlite:///"):
            self.db_file = self.database_path.replace("sqlite:///", "")
        else:
            self.db_file = "/data/robot_training.db"
        
        logger.info(f"Simulation Runner iniciado")
        logger.info(f"Base de datos: {self.db_file}")
        logger.info(f"Backend URL: {self.backend_url}")
    
    def get_db_connection(self):
        """Obtener conexión a la base de datos SQLite"""
        try:
            conn = sqlite3.connect(self.db_file)
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            logger.error(f"Error conectando a la base de datos: {e}")
            return None
    
    def get_pending_simulations(self) -> list:
        """Obtener simulaciones pendientes de la base de datos"""
        conn = self.get_db_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.*, r.name as robot_name, u.username
                FROM simulations s
                JOIN robots r ON s.robot_id = r.id
                JOIN users u ON s.user_id = u.id
                WHERE s.status = 'pending'
                ORDER BY s.created_at ASC
            """)
            
            simulations = cursor.fetchall()
            return [dict(sim) for sim in simulations]
        except Exception as e:
            logger.error(f"Error obteniendo simulaciones pendientes: {e}")
            return []
        finally:
            conn.close()
    
    def update_simulation_status(self, simulation_id: int, status: str, **kwargs):
        """Actualizar estado de una simulación en la base de datos"""
        conn = self.get_db_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            
            # Construir query de actualización
            update_fields = ["status = ?", "updated_at = ?"]
            params = [status, datetime.utcnow().isoformat()]
            
            if "started_at" in kwargs:
                update_fields.append("started_at = ?")
                params.append(kwargs["started_at"])
            
            if "completed_at" in kwargs:
                update_fields.append("completed_at = ?")
                params.append(kwargs["completed_at"])
            
            if "results" in kwargs:
                update_fields.append("results = ?")
                params.append(json.dumps(kwargs["results"]))
            
            query = f"UPDATE simulations SET {', '.join(update_fields)} WHERE id = ?"
            params.append(simulation_id)
            
            cursor.execute(query, params)
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error actualizando simulación {simulation_id}: {e}")
            return False
        finally:
            conn.close()
    
    def add_training_log(self, simulation_id: int, robot_id: int, user_id: int, message: str, level: str = "INFO"):
        """Agregar log de entrenamiento a la base de datos"""
        conn = self.get_db_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO training_logs (simulation_id, robot_id, user_id, log_level, message, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (simulation_id, robot_id, user_id, level, message, datetime.utcnow().isoformat()))
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error agregando log: {e}")
            return False
        finally:
            conn.close()
    
    def simulate_training(self, simulation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simular proceso de entrenamiento de robot.
        En un entorno real, aquí se ejecutaría el algoritmo de entrenamiento.
        """
        simulation_id = simulation["id"]
        robot_name = simulation["robot_name"]
        username = simulation["username"]
        
        logger.info(f"Iniciando simulación {simulation_id} para robot {robot_name} (usuario: {username})")
        
        # Marcar simulación como en ejecución
        self.update_simulation_status(simulation_id, "running", started_at=datetime.utcnow().isoformat())
        
        # Simular diferentes etapas del entrenamiento
        training_stages = [
            "Inicializando entorno de simulación...",
            "Cargando modelo del robot...",
            "Configurando sensores y actuadores...",
            "Ejecutando algoritmo de navegación...",
            "Entrenando modelo de reconocimiento...",
            "Optimizando parámetros de control...",
            "Validando resultados del entrenamiento...",
            "Generando reporte final..."
        ]
        
        # Simular progreso del entrenamiento
        for i, stage in enumerate(training_stages):
            # Simular tiempo de procesamiento
            processing_time = random.uniform(2, 8)
            time.sleep(processing_time)
            
            # Agregar log de progreso
            progress = int((i + 1) / len(training_stages) * 100)
            log_message = f"[{progress}%] {stage}"
            self.add_training_log(
                simulation_id, 
                simulation["robot_id"], 
                simulation["user_id"], 
                log_message
            )
            
            logger.info(f"Simulación {simulation_id}: {log_message}")
            
            # Simular posibles errores (10% de probabilidad)
            if random.random() < 0.1:
                error_message = f"Error simulado en etapa: {stage}"
                self.add_training_log(
                    simulation_id, 
                    simulation["robot_id"], 
                    simulation["user_id"], 
                    error_message, 
                    "ERROR"
                )
                logger.warning(f"Simulación {simulation_id}: {error_message}")
        
        # Generar resultados simulados
        results = {
            "training_duration": random.uniform(30, 120),
            "accuracy": random.uniform(0.75, 0.98),
            "loss": random.uniform(0.01, 0.25),
            "iterations": random.randint(100, 1000),
            "success_rate": random.uniform(0.85, 0.99),
            "metrics": {
                "precision": random.uniform(0.80, 0.95),
                "recall": random.uniform(0.75, 0.90),
                "f1_score": random.uniform(0.80, 0.92)
            }
        }
        
        # Marcar simulación como completada
        self.update_simulation_status(
            simulation_id, 
            "completed", 
            completed_at=datetime.utcnow().isoformat(),
            results=results
        )
        
        # Agregar log final
        final_message = f"Simulación completada exitosamente. Accuracy: {results['accuracy']:.2%}"
        self.add_training_log(
            simulation_id, 
            simulation["robot_id"], 
            simulation["user_id"], 
            final_message, 
            "INFO"
        )
        
        logger.info(f"Simulación {simulation_id} completada exitosamente")
        return results
    
    def run(self):
        """Ejecutar el loop principal del runner"""
        logger.info("Iniciando loop principal del Simulation Runner")
        
        while self.running:
            try:
                # Obtener simulaciones pendientes
                pending_simulations = self.get_pending_simulations()
                
                if pending_simulations:
                    logger.info(f"Procesando {len(pending_simulations)} simulaciones pendientes")
                    
                    for simulation in pending_simulations:
                        try:
                            # Procesar simulación
                            results = self.simulate_training(simulation)
                            logger.info(f"Simulación {simulation['id']} procesada con resultados: {results}")
                            
                        except Exception as e:
                            logger.error(f"Error procesando simulación {simulation['id']}: {e}")
                            
                            # Marcar simulación como fallida
                            self.update_simulation_status(simulation['id'], "failed")
                            
                            # Agregar log de error
                            self.add_training_log(
                                simulation['id'],
                                simulation['robot_id'],
                                simulation['user_id'],
                                f"Error en simulación: {str(e)}",
                                "ERROR"
                            )
                else:
                    logger.debug("No hay simulaciones pendientes")
                
                # Esperar antes de la siguiente iteración
                time.sleep(10)
                
            except KeyboardInterrupt:
                logger.info("Recibida señal de interrupción, deteniendo runner...")
                self.running = False
                break
            except Exception as e:
                logger.error(f"Error en loop principal: {e}")
                time.sleep(30)  # Esperar más tiempo en caso de error
        
        logger.info("Simulation Runner detenido")

def main():
    """Función principal"""
    runner = SimulationRunner()
    runner.run()

if __name__ == "__main__":
    main()
