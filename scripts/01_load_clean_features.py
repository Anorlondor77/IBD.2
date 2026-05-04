"""
HW2 NYC Taxi - 01 Load, Clean & Feature Engineering

Lee datos locales desde data/raw/, limpia registros, crea variables derivadas,
y guarda el resultado en data/processed/taxi_clean_features.parquet.
"""

from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql import functions as F


RAW_DIR = Path("data/raw")
PROCESSED_PATH = "data/processed/taxi_clean_features.parquet"
PARQUET_FILES = [
    RAW_DIR / "yellow_tripdata_2024-01.parquet",
    RAW_DIR / "yellow_tripdata_2024-02.parquet",
    RAW_DIR / "yellow_tripdata_2024-03.parquet",
]
LOOKUP_FILE = RAW_DIR / "taxi_zone_lookup.csv"


def _resolve_col(df, candidates):
    lower_to_real = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand.lower() in lower_to_real:
            return lower_to_real[cand.lower()]
    return None


def _require_columns(df, required_columns):
    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas requeridas en el dataset unificado: {missing}")


def main():
    spark = SparkSession.builder.appName("HW2_NYC_Taxi_Load_Clean_Features").getOrCreate()

    try:
        # 1-2) Comprobar existencia de archivos locales
        missing_parquets = [str(p) for p in PARQUET_FILES if not p.exists()]
        if missing_parquets:
            print("Faltan archivos Parquet en data/raw/. Descárgalos desde NYC TLC o colócalos manualmente en esa carpeta.")
            print("Archivos faltantes:")
            for f in missing_parquets:
                print(f"- {f}")
            spark.stop()
            return

        if not LOOKUP_FILE.exists():
            raise FileNotFoundError(
                "Falta data/raw/taxi_zone_lookup.csv. Debe estar localmente en data/raw/."
            )

        # 3-4) Leer y unificar 3 parquet mensuales
        monthly_dfs = [spark.read.parquet(str(p)) for p in PARQUET_FILES]
        trips_df = monthly_dfs[0]
        for mdf in monthly_dfs[1:]:
            trips_df = trips_df.unionByName(mdf, allowMissingColumns=True)

        # 5) Leer taxi_zone_lookup.csv
        lookup_df = spark.read.csv(str(LOOKUP_FILE), header=True, inferSchema=True)

        # 6) Esquema y conteo inicial
        print("\n=== Esquema inicial ===")
        trips_df.printSchema()

        initial_count = trips_df.count()
        print(f"\nConteo inicial: {initial_count}")

        # 7) Seleccionar columnas requeridas (si existen)
        desired_columns = [
            "tpep_pickup_datetime",
            "tpep_dropoff_datetime",
            "PULocationID",
            "DOLocationID",
            "passenger_count",
            "trip_distance",
            "fare_amount",
            "total_amount",
            "payment_type",
        ]
        existing_desired = [c for c in desired_columns if c in trips_df.columns]
        trips_df = trips_df.select(*existing_desired)

        # Verificación de columnas clave para limpieza/features
        key_required = [
            "tpep_pickup_datetime",
            "tpep_dropoff_datetime",
            "PULocationID",
            "DOLocationID",
            "passenger_count",
            "trip_distance",
            "fare_amount",
            "total_amount",
        ]
        _require_columns(trips_df, key_required)

        # 8) Limpieza
        cleaned_df = (
            trips_df
            .withColumn("tpep_pickup_datetime", F.to_timestamp("tpep_pickup_datetime"))
            .withColumn("tpep_dropoff_datetime", F.to_timestamp("tpep_dropoff_datetime"))
            .dropna(subset=key_required)
            .filter(F.col("trip_distance") > 0)
            .filter(F.col("fare_amount") > 0)
            .filter(F.col("total_amount") > 0)
            .filter(F.col("passenger_count") > 0)
            .filter(F.col("tpep_dropoff_datetime") > F.col("tpep_pickup_datetime"))
        )

        cleaned_count = cleaned_df.count()

        # 9) Features
        featured_df = (
            cleaned_df
            .withColumn(
                "trip_duration_min",
                (F.col("tpep_dropoff_datetime").cast("long") - F.col("tpep_pickup_datetime").cast("long")) / 60.0,
            )
            .withColumn("pickup_hour", F.hour("tpep_pickup_datetime"))
            .withColumn("pickup_dayofweek", F.dayofweek("tpep_pickup_datetime"))
            .withColumn("pickup_month", F.month("tpep_pickup_datetime"))
            .withColumn(
                "avg_speed_kmh",
                F.when(F.col("trip_duration_min") > 0, F.col("trip_distance") / (F.col("trip_duration_min") / 60.0))
                .otherwise(F.lit(None)),
            )
            .withColumn(
                "fare_per_km",
                F.when(F.col("trip_distance") > 0, F.col("total_amount") / F.col("trip_distance")).otherwise(F.lit(None)),
            )
            .withColumn("is_day_trip", (F.col("pickup_hour") >= 6) & (F.col("pickup_hour") < 18))
        )

        # 10) Join doble con taxi_zone_lookup para pickup y dropoff
        loc_id_col = _resolve_col(lookup_df, ["LocationID", "locationid"])
        borough_col = _resolve_col(lookup_df, ["Borough", "borough"])
        zone_col = _resolve_col(lookup_df, ["Zone", "zone"])
        if not loc_id_col or not borough_col or not zone_col:
            raise ValueError("taxi_zone_lookup.csv no contiene columnas esperadas: LocationID, Borough, Zone")

        pickup_lookup = (
            lookup_df
            .select(
                F.col(loc_id_col).alias("pu_loc_id"),
                F.col(borough_col).alias("pickup_borough"),
                F.col(zone_col).alias("pickup_zone"),
            )
        )

        dropoff_lookup = (
            lookup_df
            .select(
                F.col(loc_id_col).alias("do_loc_id"),
                F.col(borough_col).alias("dropoff_borough"),
                F.col(zone_col).alias("dropoff_zone"),
            )
        )

        final_df = (
            featured_df
            .join(pickup_lookup, featured_df["PULocationID"] == pickup_lookup["pu_loc_id"], how="left")
            .drop("pu_loc_id")
            .join(dropoff_lookup, featured_df["DOLocationID"] == dropoff_lookup["do_loc_id"], how="left")
            .drop("do_loc_id")
        )

        # 11) Guardar parquet procesado
        final_df.write.mode("overwrite").parquet(PROCESSED_PATH)

        # 12) Conteos
        final_count = final_df.count()
        removed_count = initial_count - cleaned_count
        print("\n=== Conteos ===")
        print(f"Inicial: {initial_count}")
        print(f"Tras limpieza: {cleaned_count}")
        print(f"Final: {final_count}")
        print(f"Eliminados: {removed_count}")

    finally:
        # 13) Cerrar SparkSession
        spark.stop()


if __name__ == "__main__":
    main()
