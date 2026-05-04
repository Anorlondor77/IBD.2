"""
HW2 NYC Taxi - Rendimiento y optimización en PySpark

Entrada obligatoria:
- data/processed/taxi_clean_features.parquet
"""

import time

from pyspark.sql import SparkSession
from pyspark.sql import functions as F


def _resolve_col(df, candidates):
    lower_to_real = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand.lower() in lower_to_real:
            return lower_to_real[cand.lower()]
    raise ValueError(f"No se encontró ninguna columna de {candidates}. Disponibles: {df.columns}")


def timed_count(label, sdf):
    """Fuerza ejecución y devuelve (resultado_count, segundos)."""
    t0 = time.time()
    result = sdf.count()
    elapsed = time.time() - t0
    print(f"{label} -> filas: {result}, tiempo: {elapsed:.4f}s")
    return result, elapsed


def print_section(title):
    print("\n" + "=" * 110)
    print(title)
    print("=" * 110)


def main():
    spark = SparkSession.builder.appName("HW2_NYC_Taxi_Performance_Optimization").getOrCreate()

    input_path = "data/processed/taxi_clean_features.parquet"
    df = spark.read.parquet(input_path)

    pickup_hour_col = _resolve_col(df, ["pickup_hour", "hour", "pickupHour"])
    pickup_zone_col = _resolve_col(df, ["pickup_zone", "PULocationID", "pu_location_id", "pickup_location_id"])
    dropoff_zone_col = _resolve_col(df, ["dropoff_zone", "DOLocationID", "do_location_id", "dropoff_location_id"])
    pickup_month_col = _resolve_col(df, ["pickup_month", "month"])
    trip_distance_col = _resolve_col(df, ["trip_distance", "distance", "distance_km"])
    total_amount_col = _resolve_col(df, ["total_amount", "total_fare", "amount_total"])
    fare_col = _resolve_col(df, ["fare_amount", "fare", "trip_fare"])

    # ==========================================================================================
    # OPERACIÓN 1: Consulta agregada por hora y zona
    # Optimización: poda de columnas + cache() del DF podado
    # ==========================================================================================
    print_section("OPERACIÓN 1 - Agregado por hora y zona (antes vs después)")

    normal_op1 = (
        df.groupBy(pickup_hour_col, pickup_zone_col)
        .agg(
            F.count(F.lit(1)).alias("num_trips"),
            F.avg(F.col(trip_distance_col)).alias("avg_distance"),
            F.avg(F.col(total_amount_col)).alias("avg_total_amount"),
        )
    )

    print("\n[OP1 - NORMAL] explain():")
    normal_op1.explain()
    _, op1_normal_time = timed_count("[OP1 - NORMAL] count()", normal_op1)

    # Optimización justificada:
    # - Seleccionamos solo columnas necesarias (poda de columnas)
    # - Cacheamos el dataset reducido porque se reutiliza para esta operación
    pruned_op1_df = df.select(pickup_hour_col, pickup_zone_col, trip_distance_col, total_amount_col).cache()
    _ = pruned_op1_df.count()  # materializar cache

    optimized_op1 = (
        pruned_op1_df.groupBy(pickup_hour_col, pickup_zone_col)
        .agg(
            F.count(F.lit(1)).alias("num_trips"),
            F.avg(F.col(trip_distance_col)).alias("avg_distance"),
            F.avg(F.col(total_amount_col)).alias("avg_total_amount"),
        )
    )

    print("\n[OP1 - OPTIMIZADA] explain():")
    optimized_op1.explain()
    _, op1_opt_time = timed_count("[OP1 - OPTIMIZADA] count()", optimized_op1)

    print(f"\nComparación OP1 -> normal: {op1_normal_time:.4f}s | optimizada: {op1_opt_time:.4f}s")
    print("Comentario OP1: La poda de columnas reduce I/O y serialización; cache() puede ayudar si el DF reducido se reutiliza.")

    # ==========================================================================================
    # OPERACIÓN 2: Análisis por zona (simulando carga tipo join por claves de zona)
    # Optimización: seleccionar columnas necesarias + filtrar antes de agrupar + cache()
    # ==========================================================================================
    print_section("OPERACIÓN 2 - Actividad por zona en trayectos relevantes (antes vs después)")

    normal_op2 = (
        df.groupBy(pickup_zone_col, dropoff_zone_col)
        .agg(
            F.count(F.lit(1)).alias("num_trips"),
            F.avg(F.col(fare_col)).alias("avg_fare"),
        )
        .orderBy(F.desc("num_trips"))
    )

    print("\n[OP2 - NORMAL] explain():")
    normal_op2.explain()
    _, op2_normal_time = timed_count("[OP2 - NORMAL] count()", normal_op2)

    # Optimización justificada:
    # - Filtramos primero trayectos válidos (distancia/tarifa positiva)
    # - Seleccionamos solo columnas necesarias
    # - Cacheamos el DF filtrado porque puede reutilizarse en más análisis de zona
    filtered_pruned_op2_df = (
        df.filter((F.col(trip_distance_col) > 0) & (F.col(fare_col) > 0))
        .select(pickup_zone_col, dropoff_zone_col, fare_col)
        .cache()
    )
    _ = filtered_pruned_op2_df.count()

    optimized_op2 = (
        filtered_pruned_op2_df.groupBy(pickup_zone_col, dropoff_zone_col)
        .agg(
            F.count(F.lit(1)).alias("num_trips"),
            F.avg(F.col(fare_col)).alias("avg_fare"),
        )
        .orderBy(F.desc("num_trips"))
    )

    print("\n[OP2 - OPTIMIZADA] explain():")
    optimized_op2.explain()
    _, op2_opt_time = timed_count("[OP2 - OPTIMIZADA] count()", optimized_op2)

    print(f"\nComparación OP2 -> normal: {op2_normal_time:.4f}s | optimizada: {op2_opt_time:.4f}s")
    print("Comentario OP2: Filtrar antes reduce datos intermedios; la poda evita cargar columnas no usadas.")

    # ==========================================================================================
    # OPERACIÓN 3: Ingresos por mes y zona
    # Optimización: filtrado previo + repartition por pickup_month + cache()
    # ==========================================================================================
    print_section("OPERACIÓN 3 - Ingresos por mes/zona (antes vs después)")

    normal_op3 = (
        df.groupBy(pickup_month_col, pickup_zone_col)
        .agg(
            F.sum(F.col(total_amount_col)).alias("total_revenue"),
            F.count(F.lit(1)).alias("num_trips"),
        )
        .orderBy(F.desc("total_revenue"))
    )

    print("\n[OP3 - NORMAL] explain():")
    normal_op3.explain()
    _, op3_normal_time = timed_count("[OP3 - NORMAL] count()", normal_op3)

    # Optimización justificada:
    # - Filtrado previo para quitar registros no útiles en ingresos
    # - Repartition por mes para alinear mejor el groupBy por pickup_month
    # - Cache en DF ya filtrado/reparticionado si se reutiliza
    optimized_base_op3 = (
        df.filter(F.col(total_amount_col) > 0)
        .select(pickup_month_col, pickup_zone_col, total_amount_col)
        .repartition(F.col(pickup_month_col))
        .cache()
    )
    _ = optimized_base_op3.count()

    optimized_op3 = (
        optimized_base_op3.groupBy(pickup_month_col, pickup_zone_col)
        .agg(
            F.sum(F.col(total_amount_col)).alias("total_revenue"),
            F.count(F.lit(1)).alias("num_trips"),
        )
        .orderBy(F.desc("total_revenue"))
    )

    print("\n[OP3 - OPTIMIZADA] explain():")
    optimized_op3.explain()
    _, op3_opt_time = timed_count("[OP3 - OPTIMIZADA] count()", optimized_op3)

    print(f"\nComparación OP3 -> normal: {op3_normal_time:.4f}s | optimizada: {op3_opt_time:.4f}s")
    print("Comentario OP3: Repartition por mes puede reducir skew/shuffle en agregados por mes; el impacto depende del entorno.")

    print_section("RESUMEN FINAL")
    print(f"OP1 -> normal: {op1_normal_time:.4f}s | optimizada: {op1_opt_time:.4f}s")
    print(f"OP2 -> normal: {op2_normal_time:.4f}s | optimizada: {op2_opt_time:.4f}s")
    print(f"OP3 -> normal: {op3_normal_time:.4f}s | optimizada: {op3_opt_time:.4f}s")
    print("Nota: No se garantiza mejora temporal en todos los entornos; depende de recursos, particionado y caché efectiva.")

    spark.stop()


if __name__ == "__main__":
    main()
