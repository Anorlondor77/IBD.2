"""
HW2 NYC Taxi - Análisis con funciones de ventana

Entrada obligatoria:
- data/processed/taxi_clean_features.parquet
"""

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window


def _resolve_col(df, candidates):
    """Devuelve la primera columna existente según los candidatos."""
    lower_to_real = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand.lower() in lower_to_real:
            return lower_to_real[cand.lower()]
    raise ValueError(f"No se encontró ninguna columna de {candidates}. Columnas disponibles: {df.columns}")


def print_title(title):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def main():
    # 1) Crear SparkSession
    spark = SparkSession.builder.appName("HW2_NYC_Taxi_Window_Analysis").getOrCreate()

    # 2) Leer dataset limpio con features
    input_path = "data/processed/taxi_clean_features.parquet"
    df = spark.read.parquet(input_path)

    # Resolver nombres de columnas (variantes comunes)
    pickup_month_col = _resolve_col(df, ["pickup_month", "month"])
    pickup_zone_col = _resolve_col(df, ["pickup_zone", "PULocationID", "pu_location_id", "pickup_location_id"])
    total_amount_col = _resolve_col(df, ["total_amount", "total_fare", "amount_total"])
    pickup_dt_col = _resolve_col(df, ["tpep_pickup_datetime", "pickup_datetime", "pickup_ts", "pickup_timestamp"])

    # ====================================================================================
    # ANÁLISIS 1: Ranking de las 10 principales zonas de recogida por mes
    # ====================================================================================
    print_title("ANÁLISIS 1: Top 10 zonas de recogida por mes (ranking por número de trayectos)")

    trips_by_month_zone = (
        df.groupBy(pickup_month_col, pickup_zone_col)
        .agg(F.count(F.lit(1)).alias("trip_count"))
    )

    window_month_trips = Window.partitionBy(pickup_month_col).orderBy(F.desc("trip_count"), F.asc(pickup_zone_col))

    top_pickup_zones_by_month = (
        trips_by_month_zone
        .withColumn("rank", F.row_number().over(window_month_trips))
        .filter(F.col("rank") <= 10)
        .orderBy(F.asc(pickup_month_col), F.asc("rank"))
    )

    top_pickup_zones_by_month.show(200, truncate=False)

    # ====================================================================================
    # ANÁLISIS 2: Ranking de zonas con mayor ingreso total por mes
    # ====================================================================================
    print_title("ANÁLISIS 2: Top 10 zonas por ingreso total por mes (ranking por revenue)")

    revenue_by_month_zone = (
        df.groupBy(pickup_month_col, pickup_zone_col)
        .agg(F.sum(F.col(total_amount_col)).alias("total_revenue"))
    )

    window_month_revenue = Window.partitionBy(pickup_month_col).orderBy(F.desc("total_revenue"), F.asc(pickup_zone_col))

    top_revenue_zones_by_month = (
        revenue_by_month_zone
        .withColumn("rank", F.row_number().over(window_month_revenue))
        .filter(F.col("rank") <= 10)
        .orderBy(F.asc(pickup_month_col), F.asc("rank"))
    )

    top_revenue_zones_by_month.show(200, truncate=False)

    # ====================================================================================
    # ANÁLISIS 3: Media móvil de 7 días del número de trayectos diarios
    # ====================================================================================
    print_title("ANÁLISIS 3: Media móvil de 7 días de trayectos diarios")

    daily_trips = (
        df.withColumn("pickup_date", F.to_date(F.col(pickup_dt_col)))
        .groupBy("pickup_date")
        .agg(F.count(F.lit(1)).alias("daily_trip_count"))
    )

    window_7d = Window.orderBy(F.col("pickup_date").cast("timestamp")).rowsBetween(-6, 0)

    daily_trips_with_ma = (
        daily_trips
        .withColumn("ma_7d_daily_trip_count", F.avg(F.col("daily_trip_count")).over(window_7d))
        .orderBy(F.asc("pickup_date"))
    )

    daily_trips_with_ma.show(100, truncate=False)

    spark.stop()


if __name__ == "__main__":
    main()
