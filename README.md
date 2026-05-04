# HW2_NYC_Taxi

## 1) Objetivo del proyecto
Este proyecto implementa una tubería de analítica de Big Data con PySpark sobre datos de movilidad urbana de NYC Taxi. El objetivo es cargar, limpiar, enriquecer, analizar y optimizar consultas sobre viajes de taxi, además de incluir una tarea avanzada de detección de anomalías.

## 2) Dataset usado
Se utiliza el dataset oficial **NYC TLC Yellow Taxi Trip Records** como fuente principal, junto con la tabla de zonas de taxi para enriquecer el análisis.

## 3) Archivos esperados en `data/raw/`
En local, el proyecto espera estos archivos dentro de `data/raw/`:

- `yellow_tripdata_2024-01.parquet`
- `yellow_tripdata_2024-02.parquet`
- `yellow_tripdata_2024-03.parquet`
- `taxi_zone_lookup.csv`

> Nota importante:
> - Los ficheros `.parquet` **no se suben a GitHub** por tamaño.
> - Deben colocarse localmente en `data/raw/`.
> - `taxi_zone_lookup.csv` sí está en `data/raw/`.

## 4) Estructura de carpetas

```text
HW2_NYC_Taxi/
├── data/
│   ├── raw/
│   └── processed/
├── scripts/
├── figures/
└── report/
```

## 5) Orden de ejecución
1. `scripts/01_load_clean_features.py`
2. `scripts/02_eda_queries.py`
3. `scripts/03_window_analysis.py`
4. `scripts/04_performance_optimization.py`
5. `scripts/05_advanced_anomaly_detection.py`

## 6) Restricciones
- La lógica principal debe usar **PySpark**.
- No usar **Pandas** para procesar el dataset completo.
- **Pandas** solo se permite para pequeñas tablas agregadas finales si se necesitan figuras.
- No añadir dependencias raras.
- No descargar datos automáticamente si no se pide explícitamente.
