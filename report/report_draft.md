# HW2: Analítica de Big Data con PySpark sobre NYC Taxi

## 1) Resumen del proyecto
Este proyecto implementa una tubería de analítica de datos a escala utilizando **PySpark** sobre registros de movilidad urbana de taxi en Nueva York.

El objetivo general es:
- cargar y unificar datos mensuales,
- limpiar registros problemáticos,
- crear variables derivadas útiles para análisis,
- responder preguntas analíticas de negocio,
- aplicar funciones de ventana,
- evaluar y optimizar rendimiento,
- y desarrollar una tarea avanzada de detección de anomalías.

El dataset principal utilizado es **NYC TLC Yellow Taxi Trip Records**, complementado con la **Taxi Zone Lookup Table**.

---

## 2) Miembros del grupo y contribución

### Data Engineer
- Nombre: [PENDIENTE: completar]
- Contribución principal: ingestión, revisión de esquema, limpieza y almacenamiento.
- Evidencias de contribución: [PENDIENTE: completar]

### Analytics Engineer
- Nombre: [PENDIENTE: completar]
- Contribución principal: consultas con Spark DataFrames/Spark SQL, análisis exploratorio y visualizaciones/resúmenes.
- Evidencias de contribución: [PENDIENTE: completar]

### ML/Performance Engineer
- Nombre: [PENDIENTE: completar]
- Contribución principal: ingeniería de características, funciones de ventana, tarea avanzada y optimización de rendimiento.
- Evidencias de contribución: [PENDIENTE: completar]

---

## 3) Meses seleccionados y justificación
Archivos seleccionados:
- `yellow_tripdata_2024-01.parquet`
- `yellow_tripdata_2024-02.parquet`
- `yellow_tripdata_2024-03.parquet`

Justificación:
- Se seleccionaron **3 meses del mismo año (2024)** para cumplir el requisito mínimo de la práctica.
- Este tamaño permite un equilibrio entre representatividad temporal y viabilidad de ejecución en entorno con recursos limitados.
- [PENDIENTE: insertar justificación final del grupo según entorno real y tiempos observados]

---

## 4) Dataset utilizado
- Dataset principal: **NYC TLC Yellow Taxi Trip Records**.
- Tabla auxiliar: **Taxi Zone Lookup Table**.
- Formatos:
  - viajes: Parquet,
  - lookup de zonas: CSV.

[PENDIENTE: insertar fuente exacta/URL oficial usada en la descarga]

---

## 5) Comprensión de los datos

### 5.1 Esquema
[PENDIENTE: insertar esquema real del DataFrame limpio (`printSchema`)].

### 5.2 Tamaño
- Número de filas: [PENDIENTE: insertar resultado real]
- Número de columnas: [PENDIENTE: insertar resultado real]
- Tamaño aproximado en almacenamiento/memoria: [PENDIENTE: insertar resultado real]

### 5.3 Atributos clave
Atributos relevantes para el análisis:
- timestamp de recogida,
- zona de recogida,
- zona de destino,
- distancia del trayecto,
- importe total,
- tipo de pago,
- variables derivadas de tiempo y eficiencia.

[PENDIENTE: insertar listado final exacto de columnas usadas]

---

## 6) Limpieza de datos
Se aplicaron reglas de calidad sobre registros problemáticos:

1. **Nulos en campos clave**
   - Regla aplicada: [PENDIENTE: insertar regla exacta]
   - Justificación: evitar agregaciones sesgadas o errores en joins/agrupaciones.

2. **Distancia <= 0**
   - Regla aplicada: [PENDIENTE: insertar regla exacta]
   - Justificación: trayectos no válidos para análisis de movilidad y eficiencia.

3. **Duración <= 0**
   - Regla aplicada: [PENDIENTE: insertar regla exacta]
   - Justificación: inconsistencia temporal del viaje.

4. **Tarifas <= 0**
   - Regla aplicada: [PENDIENTE: insertar regla exacta]
   - Justificación: registros que distorsionan métricas económicas.

5. **Pasajeros inválidos**
   - Regla aplicada: [PENDIENTE: insertar regla exacta]
   - Justificación: valores irreales afectan análisis de demanda.

6. **Tiempos inconsistentes (pickup/dropoff)**
   - Regla aplicada: [PENDIENTE: insertar regla exacta]
   - Justificación: preserva coherencia cronológica del viaje.

Resumen de impacto de limpieza:
- Filas eliminadas/ajustadas: [PENDIENTE: insertar resultado real]
- Porcentaje de registros afectados: [PENDIENTE: insertar resultado real]

---

## 7) Ingeniería de características
Variables derivadas incluidas:
- `trip_duration_min`
- `pickup_hour`
- `pickup_dayofweek`
- `pickup_month`
- `avg_speed_kmh`
- `fare_per_km`
- `is_day_trip`

Para cada variable:
- definición formal: [PENDIENTE: insertar fórmula real],
- motivación analítica: [PENDIENTE: completar],
- validación básica de valores: [PENDIENTE: insertar verificación real].

---

## 8) Análisis exploratorio

### 8.1 Horas con más recogidas
- Método: [PENDIENTE: DataFrame API/SQL]
- Resultado: [PENDIENTE: insertar resultado real]
- Interpretación breve: [PENDIENTE: completar]

### 8.2 Zonas de recogida más activas
- Resultado: [PENDIENTE: insertar resultado real]
- Interpretación: [PENDIENTE: completar]

### 8.3 Zonas de destino más activas
- Resultado: [PENDIENTE: insertar resultado real]
- Interpretación: [PENDIENTE: completar]

### 8.4 Demanda por día de la semana
- Resultado: [PENDIENTE: insertar resultado real]
- Interpretación: [PENDIENTE: completar]

### 8.5 Zonas con más ingresos
- Resultado: [PENDIENTE: insertar resultado real]
- Interpretación: [PENDIENTE: completar]

### 8.6 Distancia media por hora
- Resultado: [PENDIENTE: insertar resultado real]
- Interpretación: [PENDIENTE: completar]

### 8.7 Tarifa media por día
- Resultado: [PENDIENTE: insertar resultado real]
- Interpretación: [PENDIENTE: completar]

### 8.8 Tipo de pago más frecuente
- Resultado: [PENDIENTE: insertar resultado real]
- Interpretación: [PENDIENTE: completar]

### 8.9 Zonas con mayor duración media
- Resultado: [PENDIENTE: insertar resultado real]
- Interpretación: [PENDIENTE: completar]

### 8.10 Trayectos cortos frecuentes
- Resultado: [PENDIENTE: insertar resultado real]
- Interpretación: [PENDIENTE: completar]

### 8.11 Velocidad irreal
- Resultado: [PENDIENTE: insertar resultado real]
- Interpretación: [PENDIENTE: completar]

### 8.12 Tarifa alta para distancia corta
- Resultado: [PENDIENTE: insertar resultado real]
- Interpretación: [PENDIENTE: completar]

### 8.13 Día frente a noche
- Resultado: [PENDIENTE: insertar resultado real]
- Interpretación: [PENDIENTE: completar]

### 8.14 Concentración temporal de demanda
- Resultado: [PENDIENTE: insertar resultado real]
- Interpretación: [PENDIENTE: completar]

---

## 9) Funciones de ventana

### 9.1 Ranking de zonas de recogida por mes
- Diseño de ventana: partición por `pickup_month`, orden por número de trayectos descendente.
- Resultado top 10 mensual: [PENDIENTE: insertar resultado real]
- Interpretación: [PENDIENTE: completar]

### 9.2 Ranking de ingresos por mes
- Diseño de ventana: partición por `pickup_month`, orden por ingreso total descendente.
- Resultado top 10 mensual: [PENDIENTE: insertar resultado real]
- Interpretación: [PENDIENTE: completar]

### 9.3 Media móvil de viajes diarios (si se implementó)
- Diseño de ventana: orden temporal diario con marco móvil de 7 días.
- Resultado: [PENDIENTE: insertar resultado real]
- Interpretación: [PENDIENTE: completar]

---

## 10) Rendimiento y optimización
Para cada operación se documenta: consulta base, `explain()`, tiempo antes, optimización aplicada, `explain()` optimizado, tiempo después e interpretación.

### 10.1 Operación 1
- Operación analizada: [PENDIENTE: describir]
- Plan `explain()` (antes): [PENDIENTE: insertar extracto]
- Tiempo antes: [PENDIENTE: insertar resultado real]
- Optimización aplicada: [PENDIENTE: completar]
- Plan `explain()` (después): [PENDIENTE: insertar extracto]
- Tiempo después: [PENDIENTE: insertar resultado real]
- Interpretación: [PENDIENTE: completar]

### 10.2 Operación 2
- Operación analizada: [PENDIENTE: describir]
- Plan `explain()` (antes): [PENDIENTE: insertar extracto]
- Tiempo antes: [PENDIENTE: insertar resultado real]
- Optimización aplicada: [PENDIENTE: completar]
- Plan `explain()` (después): [PENDIENTE: insertar extracto]
- Tiempo después: [PENDIENTE: insertar resultado real]
- Interpretación: [PENDIENTE: completar]

### 10.3 Operación 3
- Operación analizada: [PENDIENTE: describir]
- Plan `explain()` (antes): [PENDIENTE: insertar extracto]
- Tiempo antes: [PENDIENTE: insertar resultado real]
- Optimización aplicada: [PENDIENTE: completar]
- Plan `explain()` (después): [PENDIENTE: insertar extracto]
- Tiempo después: [PENDIENTE: insertar resultado real]
- Interpretación: [PENDIENTE: completar]

Nota metodológica:
- Las mejoras de tiempo **dependen del entorno** (recursos, particionado, presión de memoria, caché efectiva).
- [PENDIENTE: insertar observación real del entorno de ejecución]

---

## 11) Tarea avanzada: detección de anomalías

### 11.1 Metodología
Se aplicó enfoque de reglas explicables sobre variables derivadas y umbrales razonables.

### 11.2 Reglas usadas
- Velocidad media irreal.
- Tarifa alta para distancia corta.
- Duración inconsistente con distancia.
- `fare_per_km` extremo mediante percentiles aproximados.

[PENDIENTE: insertar umbrales reales utilizados]

### 11.3 Resultados
- Total de registros analizados: [PENDIENTE: insertar resultado real]
- Total de anomalías detectadas: [PENDIENTE: insertar resultado real]
- Porcentaje de anomalías: [PENDIENTE: insertar resultado real]
- Anomalías por tipo: [PENDIENTE: insertar resultado real]

### 11.4 Zonas con más anomalías
- Resultado: [PENDIENTE: insertar resultado real]

### 11.5 Interpretación
[PENDIENTE: redactar interpretación basada en resultados reales, sin extrapolaciones no sustentadas]

---

## 12) Reflexión final (8–12 líneas)
[PENDIENTE: redactar bloque final real de 8–12 líneas que cubra los cuatro puntos solicitados]

Guía mínima a cubrir:
1. Paso más costoso computacionalmente y por qué.
2. Optimización de Spark más útil y en qué caso.
3. Dificultades encontradas con datos grandes/distribuidos.
4. Conclusiones sobre movilidad urbana observables en los datos.

---

## 13) Uso de IA generativa
Se utilizaron herramientas de IA generativa como apoyo para estructurar el trabajo, revisar redacción y depurar código; no obstante, el grupo comprende y puede explicar técnicamente toda la solución implementada.

---

## 14) Conclusiones
[PENDIENTE: insertar conclusiones finales sustentadas únicamente en resultados reales del proyecto]

---

## 15) Instrucciones de ejecución

### 15.1 Orden de scripts
1. `scripts/01_load_clean_features.py`
2. `scripts/02_eda_queries.py`
3. `scripts/03_window_analysis.py`
4. `scripts/04_performance_optimization.py`
5. `scripts/05_advanced_anomaly_detection.py`

### 15.2 Rutas esperadas
- Entrada principal: `data/processed/taxi_clean_features.parquet`
- Salida agregada de anomalías: `report/anomaly_summary.csv`

### 15.3 Datos necesarios
- `yellow_tripdata_2024-01.parquet`
- `yellow_tripdata_2024-02.parquet`
- `yellow_tripdata_2024-03.parquet`
- `taxi_zone_lookup.csv`

### 15.4 Comandos de referencia
[PENDIENTE: insertar comandos reales de ejecución en el entorno final, p. ej. `spark-submit ...` o ejecución en notebook]
