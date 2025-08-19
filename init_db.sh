#!/bin/sh

echo "Initializing SQLite database..."

# Crear directorio de datos si no existe
mkdir -p /data

# Crear base de datos SQLite
sqlite3 /data/robot_training.db << 'EOF'
-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de robots
CREATE TABLE IF NOT EXISTS robots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    robot_type VARCHAR(50) NOT NULL,
    configuration JSON,
    status VARCHAR(20) DEFAULT 'idle',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Tabla de simulaciones
CREATE TABLE IF NOT EXISTS simulations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    robot_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    parameters JSON,
    results JSON,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (robot_id) REFERENCES robots (id),
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Tabla de logs de entrenamiento
CREATE TABLE IF NOT EXISTS training_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    simulation_id INTEGER NOT NULL,
    robot_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    log_level VARCHAR(10) DEFAULT 'INFO',
    message TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (simulation_id) REFERENCES simulations (id),
    FOREIGN KEY (robot_id) REFERENCES robots (id),
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Insertar usuario demo (password: demo123)
INSERT OR IGNORE INTO users (username, email, password_hash) 
VALUES ('demo_user', 'demo@example.com', 'demo123');

-- Insertar robot demo
INSERT OR IGNORE INTO robots (user_id, name, robot_type, configuration, status) 
VALUES (1, 'Demo Robot', 'mobile_robot', '{"sensors": ["camera", "lidar"], "actuators": ["wheels", "arm"]}', 'idle');

-- Crear índices para mejorar performance
CREATE INDEX IF NOT EXISTS idx_robots_user_id ON robots(user_id);
CREATE INDEX IF NOT EXISTS idx_simulations_robot_id ON simulations(robot_id);
CREATE INDEX IF NOT EXISTS idx_simulations_user_id ON simulations(user_id);
CREATE INDEX IF NOT EXISTS idx_training_logs_simulation_id ON training_logs(simulation_id);

EOF

echo "Database initialized successfully!"
echo "Database file: /data/robot_training.db"
