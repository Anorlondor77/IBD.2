"""
HW2 NYC Taxi - EDA Queries

Este script responde preguntas analíticas obligatorias usando:
- PySpark DataFrame API
- Spark SQL

Entrada obligatoria:
- data/processed/taxi_clean_features.parquet
"""

from pyspark.sql import SparkSession
from pyspark.sql import functions as F


# =========================
# Utilidades
# =========================
def _resolve_col(df, candidates, required=True):
    """Devuelve la primera columna existente según una lista de candidatos."""
    lower_to_real = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand.lower() in lower_to_real:
            return lower_to_real[cand.lower()]
    if required:
        raise ValueError(f"No se encontró ninguna columna de {candidates}. Columnas disponibles: {df.columns}")
    return None


def print_query(title, sdf, n=20):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)
    sdf.show(n, truncate=False)


def main():
    # 1) Crear SparkSession
    spark = (
        SparkSession.builder
        .appName("HW2_NYC_Taxi_EDA_Queries")
        .getOrCreate()
    )

    # 2) Leer parquet limpio con features
    input_path = "data/processed/taxi_clean_features.parquet"
    df = spark.read.parquet(input_path)

    # Resolver nombres de columnas esperadas (variantes comunes)
    pickup_hour_col = _resolve_col(df, ["pickup_hour", "hour", "pickupHour"])
    pickup_dow_col = _resolve_col(df, ["pickup_dayofweek", "pickup_day_of_week", "day_of_week", "pickup_dow", "weekday"])
    pickup_zone_col = _resolve_col(df, ["pickup_zone", "PULocationID", "pu_location_id", "pickup_location_id"])
    dropoff_zone_col = _resolve_col(df, ["dropoff_zone", "DOLocationID", "do_location_id", "dropoff_location_id"])
    fare_col = _resolve_col(df, ["fare_amount", "fare", "trip_fare"])
    total_amount_col = _resolve_col(df, ["total_amount", "total_fare", "amount_total"])
    trip_distance_col = _resolve_col(df, ["trip_distance", "distance", "distance_km"])
    trip_duration_col = _resolve_col(df, ["trip_duration_min", "duration_min", "trip_duration_minutes", "duration_minutes"])
    speed_col = _resolve_col(df, ["avg_speed_kmh", "average_speed_kmh", "speed_kmh", "avg_speed"])
    payment_type_col = _resolve_col(df, ["payment_type", "payment_method", "payment"])
    pickup_ts_col = _resolve_col(df, ["tpep_pickup_datetime", "pickup_datetime", "pickup_ts", "pickup_timestamp"])

    # 3) Crear vista temporal
    df.createOrReplaceTempView("taxi_trips")

    # 4) Consultas analíticas obligatorias

    # (A) Spark DataFrame API
    # Horas con más recogidas
    q1 = (
        df.groupBy(pickup_hour_col)
        .agg(F.count(F.lit(1)).alias("num_pickups"))
        .orderBy(F.desc("num_pickups"))
    )
    print_query("1) Horas con más recogidas", q1, n=24)

    # Zonas de recogida más activas
    q2 = (
        df.groupBy(pickup_zone_col)
        .agg(F.count(F.lit(1)).alias("num_trips"))
        .orderBy(F.desc("num_trips"))
    )
    print_query("2) Zonas de recogida más activas", q2, n=20)

    # Zonas de destino más activas
    q3 = (
        df.groupBy(dropoff_zone_col)
        .agg(F.count(F.lit(1)).alias("num_trips"))
        .orderBy(F.desc("num_trips"))
    )
    print_query("3) Zonas de destino más activas", q3, n=20)

    # Demanda por día de la semana
    q4 = (
        df.groupBy(pickup_dow_col)
        .agg(F.count(F.lit(1)).alias("num_trips"))
        .orderBy(F.asc(pickup_dow_col))
    )
    print_query("4) Demanda por día de la semana", q4, n=10)

    # Zonas que generan más ingresos totales
    q5 = (
        df.groupBy(pickup_zone_col)
        .agg(F.sum(F.col(total_amount_col)).alias("total_revenue"))
        .orderBy(F.desc("total_revenue"))
    )
    print_query("5) Zonas que generan más ingresos totales", q5, n=20)

    # Distancia media de trayecto por hora
    q6 = (
        df.groupBy(pickup_hour_col)
        .agg(F.avg(F.col(trip_distance_col)).alias("avg_trip_distance"))
        .orderBy(F.asc(pickup_hour_col))
    )
    print_query("6) Distancia media de trayecto por hora", q6, n=24)

    # Tarifa media por día de la semana
    q7 = (
        df.groupBy(pickup_dow_col)
        .agg(F.avg(F.col(fare_col)).alias("avg_fare"))
        .orderBy(F.asc(pickup_dow_col))
    )
    print_query("7) Tarifa media por día de la semana", q7, n=10)

    # Tipo de pago más frecuente
    q8 = (
        df.groupBy(payment_type_col)
        .agg(F.count(F.lit(1)).alias("num_trips"))
        .orderBy(F.desc("num_trips"))
    )
    print_query("8) Tipo de pago más frecuente", q8, n=10)

    # (B) Spark SQL
    # Zonas con mayor duración media de viaje
    q9 = spark.sql(f"""
        SELECT {pickup_zone_col} AS pickup_zone,
               AVG({trip_duration_col}) AS avg_duration_min,
               COUNT(*) AS num_trips
        FROM taxi_trips
        GROUP BY {pickup_zone_col}
        HAVING COUNT(*) >= 50
        ORDER BY avg_duration_min DESC
        LIMIT 20
    """)
    print_query("9) Zonas con mayor duración media de viaje", q9, n=20)

    # Zonas con trayectos cortos pero muy frecuentes
    q10 = spark.sql(f"""
        SELECT {pickup_zone_col} AS pickup_zone,
               COUNT(*) AS num_short_trips,
               AVG({trip_distance_col}) AS avg_short_distance
        FROM taxi_trips
        WHERE {trip_distance_col} > 0 AND {trip_distance_col} <= 2
        GROUP BY {pickup_zone_col}
        ORDER BY num_short_trips DESC
        LIMIT 20
    """)
    print_query("10) Zonas con trayectos cortos pero muy frecuentes", q10, n=20)

    # Trayectos con velocidad media irreal
    q11 = spark.sql(f"""
        SELECT {pickup_ts_col} AS pickup_datetime,
               {pickup_zone_col} AS pickup_zone,
               {dropoff_zone_col} AS dropoff_zone,
               {trip_distance_col} AS trip_distance,
               {trip_duration_col} AS trip_duration_min,
               {speed_col} AS avg_speed_kmh,
               {fare_col} AS fare_amount,
               {total_amount_col} AS total_amount
        FROM taxi_trips
        WHERE {speed_col} > 120 OR {speed_col} <= 1
        ORDER BY {speed_col} DESC
        LIMIT 50
    """)
    print_query("11) Trayectos con velocidad media irreal", q11, n=50)

    # Registros con tarifa sospechosamente alta para distancia corta
    q12 = spark.sql(f"""
        SELECT {pickup_ts_col} AS pickup_datetime,
               {pickup_zone_col} AS pickup_zone,
               {dropoff_zone_col} AS dropoff_zone,
               {trip_distance_col} AS trip_distance,
               {fare_col} AS fare_amount,
               {total_amount_col} AS total_amount
        FROM taxi_trips
        WHERE {trip_distance_col} > 0
          AND {trip_distance_col} <= 2
          AND {fare_col} >= 50
        ORDER BY {fare_col} DESC
        LIMIT 50
    """)
    print_query("12) Registros con tarifa sospechosamente alta para distancia corta", q12, n=50)

    # Comparación de trayectos de día frente a noche
    q13 = spark.sql(f"""
        SELECT CASE WHEN {pickup_hour_col} BETWEEN 6 AND 17 THEN 'DAY' ELSE 'NIGHT' END AS period,
               COUNT(*) AS num_trips,
               AVG({trip_distance_col}) AS avg_distance,
               AVG({trip_duration_col}) AS avg_duration_min,
               AVG({fare_col}) AS avg_fare
        FROM taxi_trips
        GROUP BY CASE WHEN {pickup_hour_col} BETWEEN 6 AND 17 THEN 'DAY' ELSE 'NIGHT' END
        ORDER BY period
    """)
    print_query("13) Comparación de trayectos de día frente a noche", q13, n=10)

    # Patrones de concentración de demanda a lo largo del tiempo
    q14 = spark.sql(f"""
        SELECT DATE_TRUNC('day', {pickup_ts_col}) AS day,
               COUNT(*) AS num_trips,
               ROUND(COUNT(*) / SUM(COUNT(*)) OVER (), 6) AS demand_share
        FROM taxi_trips
        GROUP BY DATE_TRUNC('day', {pickup_ts_col})
        ORDER BY num_trips DESC
        LIMIT 30
    """)
    print_query("14) Patrones de concentración de demanda a lo largo del tiempo", q14, n=30)

    spark.stop()


if __name__ == "__main__":
    main()
