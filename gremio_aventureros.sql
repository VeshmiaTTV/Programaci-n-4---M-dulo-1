-- =====================================================
-- Base de datos: Gremio de aventureros
-- Materia: Programación de Computadoras 4
-- Motor: SQLite
-- =====================================================

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS misiones_monstruos;
DROP TABLE IF EXISTS misiones_heroes;
DROP TABLE IF EXISTS monstruos;
DROP TABLE IF EXISTS misiones;
DROP TABLE IF EXISTS heroes;

-- ---------- Entidades principales ----------

CREATE TABLE heroes (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre            TEXT    NOT NULL,
    clase             TEXT    NOT NULL
                      CHECK (clase IN ('Guerrero','Mago','Arquero','Clérigo','Pícaro','Paladín')),
    nivel_experiencia INTEGER NOT NULL DEFAULT 1
                      CHECK (nivel_experiencia >= 1)
);

CREATE TABLE misiones (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre         TEXT    NOT NULL,
    dificultad     INTEGER NOT NULL CHECK (dificultad BETWEEN 1 AND 10),
    localizacion   TEXT    NOT NULL,
    recompensa_oro INTEGER NOT NULL DEFAULT 0 CHECK (recompensa_oro >= 0)
);

CREATE TABLE monstruos (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre        TEXT    NOT NULL,
    tipo          TEXT    NOT NULL
                  CHECK (tipo IN ('Dragón','Goblin','No-muerto','Orco','Demonio','Bestia')),
    nivel_amenaza INTEGER NOT NULL CHECK (nivel_amenaza BETWEEN 1 AND 10)
);

-- ---------- Tablas puente (relaciones muchos-a-muchos) ----------

CREATE TABLE misiones_heroes (
    mision_id INTEGER NOT NULL,
    heroe_id  INTEGER NOT NULL,
    PRIMARY KEY (mision_id, heroe_id),
    FOREIGN KEY (mision_id) REFERENCES misiones(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (heroe_id)  REFERENCES heroes(id)   ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE misiones_monstruos (
    mision_id   INTEGER NOT NULL,
    monstruo_id INTEGER NOT NULL,
    PRIMARY KEY (mision_id, monstruo_id),
    FOREIGN KEY (mision_id)   REFERENCES misiones(id)   ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (monstruo_id) REFERENCES monstruos(id)  ON DELETE CASCADE ON UPDATE CASCADE
);

-- ---------- Datos de ejemplo ----------

INSERT INTO heroes (nombre, clase, nivel_experiencia) VALUES
    ('Aragorn',  'Guerrero', 15),
    ('Gandalf',  'Mago',     30),
    ('Legolas',  'Arquero',  20),
    ('Elowen',   'Clérigo',  12),
    ('Shadow',   'Pícaro',    8);

INSERT INTO misiones (nombre, dificultad, localizacion, recompensa_oro) VALUES
    ('Cueva de los Goblins',      2, 'Bosque Sombrío',       150),
    ('Cripta Maldita',            5, 'Cementerio Antiguo',   500),
    ('El Nido del Dragón Rojo',   9, 'Montaña de Fuego',    5000),
    ('Asalto al Fuerte Orco',     6, 'Llanuras del Norte',   800);

INSERT INTO monstruos (nombre, tipo, nivel_amenaza) VALUES
    ('Goblin Explorador', 'Goblin',    2),
    ('Rey Goblin',        'Goblin',    4),
    ('Esqueleto Guerrero','No-muerto', 5),
    ('Liche Menor',       'No-muerto', 7),
    ('Dragón Rojo Ignis', 'Dragón',   10),
    ('Jefe Orco Grukk',   'Orco',      6);

INSERT INTO misiones_heroes (mision_id, heroe_id) VALUES
    (1, 1), (1, 5),
    (2, 2), (2, 4), (2, 1),
    (3, 1), (3, 2), (3, 3), (3, 4),
    (4, 1), (4, 3), (4, 5);

INSERT INTO misiones_monstruos (mision_id, monstruo_id) VALUES
    (1, 1), (1, 2),
    (2, 3), (2, 4),
    (3, 5),
    (4, 6), (4, 1);

-- ---------- Consultas de ejemplo ----------

-- 1) Héroes que participaron en cada misión
SELECT m.nombre AS mision, h.nombre AS heroe, h.clase
FROM misiones m
JOIN misiones_heroes mh ON mh.mision_id = m.id
JOIN heroes h           ON h.id = mh.heroe_id
ORDER BY m.nombre;

-- 2) Monstruos enfrentados en cada misión
SELECT m.nombre AS mision, mo.nombre AS monstruo, mo.tipo, mo.nivel_amenaza
FROM misiones m
JOIN misiones_monstruos mm ON mm.mision_id = m.id
JOIN monstruos mo          ON mo.id = mm.monstruo_id
ORDER BY m.nombre;

-- 3) Cantidad de misiones por héroe
SELECT h.nombre, COUNT(mh.mision_id) AS total_misiones
FROM heroes h
LEFT JOIN misiones_heroes mh ON mh.heroe_id = h.id
GROUP BY h.id
ORDER BY total_misiones DESC;

-- 4) Oro total ganado por cada héroe (sin dividir la recompensa)
SELECT h.nombre, COALESCE(SUM(m.recompensa_oro), 0) AS oro_total
FROM heroes h
LEFT JOIN misiones_heroes mh ON mh.heroe_id = h.id
LEFT JOIN misiones m         ON m.id = mh.mision_id
GROUP BY h.id
ORDER BY oro_total DESC;
