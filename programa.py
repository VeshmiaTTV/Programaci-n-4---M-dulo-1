import os
import sqlite3

# ------------------------------------------------------------
# Ruta del archivo de base de datos (junto a este script)
# ------------------------------------------------------------
DIRECTORIO = os.path.dirname(os.path.abspath(__file__))
RUTA_DB = os.path.join(DIRECTORIO, "gremio.db")

# Si ya existe, se elimina para poder re-ejecutar el script
if os.path.exists(RUTA_DB):
    os.remove(RUTA_DB)

conexion = sqlite3.connect(RUTA_DB)          # crea el archivo gremio.db
conexion.execute("PRAGMA foreign_keys = ON")  # activar claves foráneas
cursor = conexion.cursor()

# ------------------------------------------------------------
# Tablas
# ------------------------------------------------------------
cursor.execute("""
CREATE TABLE heroes (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre            TEXT    NOT NULL UNIQUE,
    clase             TEXT    NOT NULL
                      CHECK (clase IN ('Guerrero', 'Mago', 'Arquero', 'Clérigo', 'Pícaro', 'Paladín', 'Bardo')),
    nivel_experiencia INTEGER NOT NULL DEFAULT 1
                      CHECK (nivel_experiencia BETWEEN 1 AND 100)
)
""")

cursor.execute("""
CREATE TABLE misiones (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre       TEXT    NOT NULL,
    descripcion  TEXT,
    dificultad   INTEGER NOT NULL CHECK (dificultad BETWEEN 1 AND 10),
    localizacion TEXT    NOT NULL,
    recompensa   INTEGER NOT NULL DEFAULT 0 CHECK (recompensa >= 0)
)
""")

cursor.execute("""
CREATE TABLE monstruos (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre        TEXT    NOT NULL UNIQUE,
    tipo          TEXT    NOT NULL
                  CHECK (tipo IN ('Dragón', 'Goblin', 'No-muerto', 'Orco', 'Demonio', 'Bestia', 'Elemental')),
    nivel_amenaza INTEGER NOT NULL CHECK (nivel_amenaza BETWEEN 1 AND 10)
)
""")

cursor.execute("""
CREATE TABLE misiones_heroes (
    mision_id INTEGER NOT NULL,
    heroe_id  INTEGER NOT NULL,
    PRIMARY KEY (mision_id, heroe_id),
    FOREIGN KEY (mision_id) REFERENCES misiones(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (heroe_id)  REFERENCES heroes(id)   ON DELETE CASCADE ON UPDATE CASCADE
)
""")

cursor.execute("""
CREATE TABLE misiones_monstruos (
    mision_id   INTEGER NOT NULL,
    monstruo_id INTEGER NOT NULL,
    cantidad    INTEGER NOT NULL DEFAULT 1 CHECK (cantidad > 0),
    PRIMARY KEY (mision_id, monstruo_id),
    FOREIGN KEY (mision_id)   REFERENCES misiones(id)  ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (monstruo_id) REFERENCES monstruos(id) ON DELETE CASCADE ON UPDATE CASCADE
)
""")

# Índices
cursor.execute("CREATE INDEX idx_mh_heroe ON misiones_heroes(heroe_id)")
cursor.execute("CREATE INDEX idx_mm_monstruo ON misiones_monstruos(monstruo_id)")

# ------------------------------------------------------------
# Datos de ejemplo
# ------------------------------------------------------------
heroes = [
    ("Aragorn", "Guerrero", 45),
    ("Gandalf", "Mago", 80),
    ("Legolas", "Arquero", 60),
    ("Elara", "Clérigo", 35),
    ("Shadow", "Pícaro", 28),
]
cursor.executemany(
    "INSERT INTO heroes (nombre, clase, nivel_experiencia) VALUES (?, ?, ?)", heroes
)

misiones = [
    ("La Cueva del Dragón", "Derrotar al dragón que aterroriza la aldea", 9, "Montañas Ceniza", 5000),
    ("Plaga de Goblins", "Eliminar el campamento goblin del bosque", 3, "Bosque Umbrío", 800),
    ("La Cripta Olvidada", "Purgar los no-muertos de la cripta antigua", 6, "Cementerio Real", 2200),
    ("Asedio Orco", "Defender el fuerte de la horda orca", 7, "Fuerte Piedranegra", 3000),
]
cursor.executemany(
    "INSERT INTO misiones (nombre, descripcion, dificultad, localizacion, recompensa) "
    "VALUES (?, ?, ?, ?, ?)",
    misiones,
)

monstruos = [
    ("Smaug Menor", "Dragón", 10),
    ("Goblin Explorador", "Goblin", 2),
    ("Rey Goblin", "Goblin", 5),
    ("Esqueleto Guerrero", "No-muerto", 4),
    ("Liche Menor", "No-muerto", 8),
    ("Orco Berserker", "Orco", 6),
]
cursor.executemany(
    "INSERT INTO monstruos (nombre, tipo, nivel_amenaza) VALUES (?, ?, ?)", monstruos
)

misiones_heroes = [
    (1, 1), (1, 2), (1, 3),
    (2, 3), (2, 5),
    (3, 2), (3, 4),
    (4, 1), (4, 3), (4, 4),
]
cursor.executemany(
    "INSERT INTO misiones_heroes (mision_id, heroe_id) VALUES (?, ?)", misiones_heroes
)

misiones_monstruos = [
    (1, 1, 1),
    (2, 2, 12), (2, 3, 1),
    (3, 4, 20), (3, 5, 1),
    (4, 6, 15),
]
cursor.executemany(
    "INSERT INTO misiones_monstruos (mision_id, monstruo_id, cantidad) VALUES (?, ?, ?)",
    misiones_monstruos,
)

conexion.commit()

# ------------------------------------------------------------
# Consultas de prueba
# ------------------------------------------------------------
print("=== Héroes por misión ===")
cursor.execute("""
    SELECT m.nombre, h.nombre, h.clase
    FROM misiones m
    JOIN misiones_heroes mh ON mh.mision_id = m.id
    JOIN heroes h           ON h.id = mh.heroe_id
    ORDER BY m.nombre
""")
for mision, heroe, clase in cursor.fetchall():
    print(f"{mision:22} | {heroe:10} | {clase}")

print("\n=== Monstruos por misión ===")
cursor.execute("""
    SELECT m.nombre, mo.nombre, mo.tipo, mm.cantidad
    FROM misiones m
    JOIN misiones_monstruos mm ON mm.mision_id = m.id
    JOIN monstruos mo          ON mo.id = mm.monstruo_id
    ORDER BY m.nombre
""")
for mision, monstruo, tipo, cantidad in cursor.fetchall():
    print(f"{mision:22} | {monstruo:20} | {tipo:10} | x{cantidad}")

print("\n=== Misiones y oro total por héroe ===")
cursor.execute("""
    SELECT h.nombre, COUNT(mh.mision_id), COALESCE(SUM(m.recompensa), 0) AS oro_total
    FROM heroes h
    LEFT JOIN misiones_heroes mh ON mh.heroe_id = h.id
    LEFT JOIN misiones m         ON m.id = mh.mision_id
    GROUP BY h.id
    ORDER BY oro_total DESC
""")
for nombre, total, oro in cursor.fetchall():
    print(f"{nombre:10} | {total} misiones | {oro} monedas de oro")

conexion.close()
print(f"\nBase de datos creada en: {RUTA_DB}")