"""
HW2 NYC Taxi - Tarea avanzada (Opción C): Detección de anomalías

Entrada obligatoria:
- data/processed/taxi_clean_features.parquet

Salida agregada pequeña:
- report/anomaly_summary.csv
"""

from pyspark.sql import SparkSession
from pyspark.sql import functions as F


def _resolve_col(df, candidates):
    lower_to_real = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand.lower() in lower_to_real:
            return lower_to_real[cand.lower()]
    raise ValueError(f"No se encontró ninguna columna de {candidates}. Columnas disponibles: {df.columns}")


def print_title(title):
    print("\n" + "=" * 110)
    print(title)
    print("=" * 110)


def main():
    spark = SparkSession.builder.appName("HW2_NYC_Taxi_Advanced_Anomaly_Detection").getOrCreate()

    input_path = "data/processed/taxi_clean_features.parquet"
    df = spark.read.parquet(input_path)

    # Resolver columnas esperadas
    pickup_zone_col = _resolve_col(df, ["pickup_zone", "PULocationID", "pu_location_id", "pickup_location_id"])
    pickup_ts_col = _resolve_col(df, ["tpep_pickup_datetime", "pickup_datetime", "pickup_ts", "pickup_timestamp"])
    trip_distance_col = _resolve_col(df, ["trip_distance", "distance", "distance_km"])
    duration_col = _resolve_col(df, ["trip_duration_min", "duration_min", "trip_duration_minutes", "duration_minutes"])
    total_amount_col = _resolve_col(df, ["total_amount", "total_fare", "amount_total"])
    avg_speed_col = _resolve_col(df, ["avg_speed_kmh", "average_speed_kmh", "speed_kmh", "avg_speed"])
    fare_per_km_col = _resolve_col(df, ["fare_per_km", "total_per_km", "amount_per_km"])

    # ======================================================================================
    # Reglas de anomalía
    # ======================================================================================
    # A) Velocidad media irreal (umbral fijo razonable para taxi urbano)
    high_speed_threshold = 120.0  # km/h

    # B) Tarifa alta para distancia corta
    short_distance_threshold = 2.0  # km (o unidad equivalente en el dataset)
    high_total_amount_threshold = 50.0

    # C) Duración inconsistente
    #    - Muy baja duración para distancia alta
    #    - Muy alta duración para distancia baja
    high_distance_threshold = 20.0
    very_short_duration_threshold = 10.0  # minutos
    low_distance_threshold = 2.0
    very_long_duration_threshold = 60.0  # minutos

    # D) Fare_per_km extremo (percentil aproximado)
    #    Se usa approxQuantile para definir umbral robusto por cola superior.
    fare_per_km_q95 = df.approxQuantile(fare_per_km_col, [0.95], 0.01)[0]
    fare_per_km_q99 = df.approxQuantile(fare_per_km_col, [0.99], 0.01)[0]
    extreme_fare_per_km_threshold = fare_per_km_q99

    print_title("Umbrales de anomalía")
    print(f"A) high_speed_threshold (km/h): {high_speed_threshold}")
    print(f"B) short_distance_threshold: {short_distance_threshold}, high_total_amount_threshold: {high_total_amount_threshold}")
    print(
        "C) duration_inconsistent thresholds -> "
        f"high_distance>{high_distance_threshold} & duration<{very_short_duration_threshold} OR "
        f"distance<{low_distance_threshold} & duration>{very_long_duration_threshold}"
    )
    print(f"D) fare_per_km q95: {fare_per_km_q95}, q99: {fare_per_km_q99}, threshold usado: {extreme_fare_per_km_threshold}")

    anomalies_df = (
        df
        .withColumn("anomaly_high_speed", F.col(avg_speed_col) > F.lit(high_speed_threshold))
        .withColumn(
            "anomaly_short_distance_high_fare",
            (F.col(trip_distance_col) > 0)
            & (F.col(trip_distance_col) <= F.lit(short_distance_threshold))
            & (F.col(total_amount_col) >= F.lit(high_total_amount_threshold))
        )
        .withColumn(
            "anomaly_duration_inconsistent",
            ((F.col(trip_distance_col) >= F.lit(high_distance_threshold)) & (F.col(duration_col) <= F.lit(very_short_duration_threshold)))
            |
            ((F.col(trip_distance_col) <= F.lit(low_distance_threshold)) & (F.col(duration_col) >= F.lit(very_long_duration_threshold)))
        )
        .withColumn("anomaly_high_fare_per_km", F.col(fare_per_km_col) >= F.lit(extreme_fare_per_km_threshold))
        .withColumn(
            "is_anomaly",
            F.col("anomaly_high_speed")
            | F.col("anomaly_short_distance_high_fare")
            | F.col("anomaly_duration_inconsistent")
            | F.col("anomaly_high_fare_per_km")
        )
        .withColumn(
            "anomaly_score",
            F.col("anomaly_high_speed").cast("int")
            + F.col("anomaly_short_distance_high_fare").cast("int")
            + F.col("anomaly_duration_inconsistent").cast("int")
            + F.col("anomaly_high_fare_per_km").cast("int")
        )
    )

    # ======================================================================================
    # Resumen por consola
    # ======================================================================================
    print_title("Resumen global de anomalías")
    total_records = anomalies_df.count()
    total_anomalies = anomalies_df.filter(F.col("is_anomaly")).count()
    anomaly_pct = (total_anomalies / total_records * 100.0) if total_records > 0 else 0.0

    print(f"Número total de registros: {total_records}")
    print(f"Número total de anomalías: {total_anomalies}")
    print(f"Porcentaje de anomalías: {anomaly_pct:.4f}%")

    print_title("Anomalías por tipo")
    by_type = anomalies_df.select(
        F.sum(F.col("anomaly_high_speed").cast("int")).alias("anomaly_high_speed"),
        F.sum(F.col("anomaly_short_distance_high_fare").cast("int")).alias("anomaly_short_distance_high_fare"),
        F.sum(F.col("anomaly_duration_inconsistent").cast("int")).alias("anomaly_duration_inconsistent"),
        F.sum(F.col("anomaly_high_fare_per_km").cast("int")).alias("anomaly_high_fare_per_km"),
    )
    by_type.show(truncate=False)

    print_title("Zonas con más anomalías")
    zones_with_anomalies = (
        anomalies_df.filter(F.col("is_anomaly"))
        .groupBy(pickup_zone_col)
        .agg(F.count(F.lit(1)).alias("num_anomalies"))
        .orderBy(F.desc("num_anomalies"))
    )
    zones_with_anomalies.show(20, truncate=False)

    print_title("Ejemplos de anomalías (ordenadas por severidad)")
    anomaly_examples = (
        anomalies_df.filter(F.col("is_anomaly"))
        .select(
            pickup_ts_col,
            pickup_zone_col,
            trip_distance_col,
            duration_col,
            avg_speed_col,
            total_amount_col,
            fare_per_km_col,
            "anomaly_high_speed",
            "anomaly_short_distance_high_fare",
            "anomaly_duration_inconsistent",
            "anomaly_high_fare_per_km",
            "anomaly_score",
        )
        .orderBy(F.desc("anomaly_score"), F.desc(total_amount_col), F.desc(avg_speed_col))
    )
    anomaly_examples.show(50, truncate=False)

    # ======================================================================================
    # Guardado de resumen agregado pequeño (NO dataset completo)
    # ======================================================================================
    print_title("Guardado de resumen agregado")

    summary_df = anomalies_df.agg(
        F.count(F.lit(1)).alias("total_records"),
        F.sum(F.col("is_anomaly").cast("int")).alias("total_anomalies"),
        F.sum(F.col("anomaly_high_speed").cast("int")).alias("anomaly_high_speed"),
        F.sum(F.col("anomaly_short_distance_high_fare").cast("int")).alias("anomaly_short_distance_high_fare"),
        F.sum(F.col("anomaly_duration_inconsistent").cast("int")).alias("anomaly_duration_inconsistent"),
        F.sum(F.col("anomaly_high_fare_per_km").cast("int")).alias("anomaly_high_fare_per_km"),
    ).withColumn(
        "anomaly_percentage",
        F.when(F.col("total_records") > 0, F.col("total_anomalies") / F.col("total_records") * 100.0).otherwise(F.lit(0.0))
    )

    output_path = "report/anomaly_summary.csv"
    summary_df.coalesce(1).write.mode("overwrite").option("header", True).csv(output_path)

    print(f"Resumen agregado guardado en: {output_path}")
    summary_df.show(truncate=False)

    spark.stop()


if __name__ == "__main__":
    main()
