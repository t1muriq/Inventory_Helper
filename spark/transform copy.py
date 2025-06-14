from pyspark.sql import SparkSession
from pyspark.sql.functions import col,split, lit, expr, regexp_extract, sum as spark_sum, when, current_timestamp,from_utc_timestamp, concat_ws, coalesce, upper, lower, regexp_replace, collect_list, concat_ws 
from datetime import timezone, timedelta, datetime
import pytz 


spark = SparkSession.builder \
    .appName("PostgresToClickhouseETL") \
    .config("spark.jars", 
        "file:///C:/Users/Timur/PycharmProjects/Inventory_Helper/Inventory_Helper/spark/libs/postgresql-42.2.18.jar,"
        "file:///C:/Users/Timur/PycharmProjects/Inventory_Helper/Inventory_Helper/spark/libs/clickhouse-jdbc-0.6.5.jar,"
        "file:///C:/Users/Timur/PycharmProjects/Inventory_Helper/Inventory_Helper/spark/libs/httpclient5-5.2.1.jar,"
        "file:///C:/Users/Timur/PycharmProjects/Inventory_Helper/Inventory_Helper/spark/libs/httpcore5-5.2.1.jar,"
        "file:///C:/Users/Timur/PycharmProjects/Inventory_Helper/Inventory_Helper/spark/libs/httpcore5-h2-5.2.1.jar") \
    .getOrCreate()

# Параметры подключения к PostgreSQL
pg_url = "jdbc:postgresql://localhost:5435/inventory_db?session_timezone=Europe/Moscow"
pg_properties = {
    "user": "postgres",
    "password": "123",
    "driver": "org.postgresql.Driver"
}

ch_url = "jdbc:clickhouse://localhost:8123/inventory_db"
ch_properties = {
    "driver": "com.clickhouse.jdbc.ClickHouseDriver",
    "user": "username",
    "password": "password"
}

# Извлекаем последнее время из click
latest_timestamp_df = spark.read \
    .format("jdbc") \
    .option("url", ch_url) \
    .option("dbtable", "computers_analytics") \
    .option("user", ch_properties["user"]) \
    .option("password", ch_properties["password"]) \
    .option("driver", ch_properties["driver"]) \
    .load() \
    .selectExpr("max(load_date) as max_load_date")

max_load_date = latest_timestamp_df.collect()[0]["max_load_date"]

if max_load_date is not None:
    max_load_date = max_load_date + timedelta(hours=3)
    print("max_load_date (с учетом смещения):", max_load_date)
else:
    print("max_load_date не найден, будет загружена вся таблица computers")



def read_table(table_name):
    return spark.read.jdbc(url=pg_url, table=table_name, properties=pg_properties)

def read_table_filtered(table_name, date_column, last_timestamp):
    query = f"(SELECT * FROM {table_name} WHERE {date_column} > '{last_timestamp}') AS tmp"
    return spark.read.jdbc(url=pg_url, table=query, properties=pg_properties)

# Чтение всех таблиц
buildings_df = read_table("buildings")
rooms_df = read_table("rooms")

if max_load_date is None:
    computers_df = read_table("computers")
else:
    computers_df = read_table_filtered("computers", "load_date", max_load_date)
    
memory_modules_df = read_table("memory_modules")
processors_df = read_table("processors")
motherboards_df = read_table("motherboards")
disks_df = read_table("disks")
video_adapters_df = read_table("video_adapters")
monitors_df = read_table("monitors")
upss_df = read_table("upss")

computers_df.select("load_date").show(truncate=False)

# Трансформация данных
# 1. Объединяем таблицы для получения полной информации о компьютерах
computers_joined = computers_df \
    .join(rooms_df, computers_df.room_id == rooms_df.id, "left") \
    .join(buildings_df, rooms_df.building_id == buildings_df.id, "left") \
    .select(
        computers_df.id.alias("computer_id"),
        buildings_df.name.alias("building"),
        rooms_df.room_number.alias("room_number"),
        computers_df.department,
        computers_df.responsible,
        computers_df.inventory_number,
        computers_df.serial_number,
        computers_df.ip_address,
        computers_df.mac_address,
        computers_df.kaspersky_attempted,
        computers_df.kaspersky_network,
        computers_df.comment
    )

# 2. Агрегируем информацию о процессорах
processors_agg = processors_df \
    .groupBy("computer_id") \
    .agg(
        concat_ws(", ", collect_list("type")).alias("processor_type"),
        concat_ws(", ", collect_list("frequency")).alias("processor_frequency")
    )

# 3. Агрегируем информацию о памяти
memory_agg = memory_modules_df \
    .groupBy("computer_id") \
    .agg(
        concat_ws(", ", collect_list("name")).alias("memory_modules"),
        concat_ws(", ", collect_list("description")).alias("memory_description")
    )

# 4. Агрегируем информацию о дисках
disks_agg = disks_df \
    .groupBy("computer_id") \
    .agg(
        concat_ws(", ", collect_list("name")).alias("disk_names"),
        concat_ws(", ", collect_list("capacity")).alias("disk_capacities")
    )

# 5. Агрегируем информацию о видеоадаптерах
video_agg = video_adapters_df \
    .groupBy("computer_id") \
    .agg(
        concat_ws(", ", collect_list("name")).alias("video_adapter"),
        concat_ws(", ", collect_list("memory")).alias("video_memory")
    )

# 6. Агрегируем информацию о мониторах
monitors_agg = monitors_df \
    .groupBy("computer_id") \
    .agg(
        concat_ws(", ", collect_list("assigned_it_number")).alias("monitor_it_numbers"),
        concat_ws(", ", collect_list("model")).alias("monitor_model"),
        concat_ws(", ", collect_list("resolution")).alias("monitor_resolution")
    )

# 7. Агрегируем информацию о UPS
ups_agg = upss_df \
    .groupBy("computer_id") \
    .agg(
        concat_ws(", ", collect_list("assigned_it_number")).alias("ups_it_numbers")
    )



# 8. Объединяем все агрегированные данные
final_df = computers_joined \
    .join(processors_agg, computers_joined.computer_id == processors_agg.computer_id, "left") \
    .join(memory_agg, computers_joined.computer_id == memory_agg.computer_id, "left") \
    .join(disks_agg, computers_joined.computer_id == disks_agg.computer_id, "left") \
    .join(video_agg, computers_joined.computer_id == video_agg.computer_id, "left") \
    .join(monitors_agg, computers_joined.computer_id == monitors_agg.computer_id, "left") \
    .join(ups_agg, computers_joined.computer_id == ups_agg.computer_id, "left") \
    .select(
        computers_joined.computer_id,
        computers_joined.building,
        computers_joined.room_number,
        computers_joined.department,
        computers_joined.responsible,
        computers_joined.inventory_number,
        computers_joined.serial_number,
        computers_joined.ip_address,
        computers_joined.mac_address,
        computers_joined.kaspersky_attempted,
        computers_joined.kaspersky_network,
        processors_agg.processor_type,
        processors_agg.processor_frequency,
        memory_agg.memory_modules,
        memory_agg.memory_description,
        disks_agg.disk_names,
        disks_agg.disk_capacities,
        video_agg.video_adapter,
        video_agg.video_memory,
        monitors_agg.monitor_model,
        monitors_agg.monitor_resolution,
        ups_agg.ups_it_numbers,
        computers_joined.comment,
        current_timestamp().alias("load_date")
    )


# 9. Очистка и преобразование данных
final_df = final_df \
    .withColumn("kaspersky_installed", when(lower(col("kaspersky_attempted")) == "да", True).otherwise(False)) \
    .withColumn("kaspersky_in_network", when(lower(col("kaspersky_network")) == "ru", True).otherwise(False)) \
    .withColumn(
        "processor_frequency",
        when(
            regexp_extract(col("processor_frequency"), r"(\\d+\\.?\\d*)", 1) != "",
            regexp_extract(col("processor_frequency"), r"(\\d+\\.?\\d*)", 1).cast("float")
        ).otherwise(None)
    ) \
    .withColumn("ram_total_mb", expr("""
    aggregate(
        filter(
            transform(
                split(memory_description, ',\\s*'),
                x -> regexp_extract(x, '(\\\\d+)\\\\s*МБ', 1)
            ),
            x -> x != ''
        ),
        0,
        (acc, x) -> acc + CAST(x AS INT)
    )
""")) \
    .withColumn("disk_total_gb", expr("""
    aggregate(
        filter(
            transform(
                split(disk_capacities, ',\\s*'),
                x -> regexp_extract(x, '(\\\\d+)\\\\s*ГБ', 1)
            ),
            x -> x != ''
        ),
        0,
        (acc, x) -> acc + CAST(x AS INT)
    )
""")) \
    .withColumn(
        "video_memory_mb",
         expr("""
    aggregate(
        filter(
            transform(
                split(video_memory, ',\\s*'),
                x -> regexp_extract(x, '(\\\\d+)\\\\s*МБ', 1)
            ),
            x -> x != ''
        ),
        0,
        (acc, x) -> acc + CAST(x AS INT)
    )
""")
    ) \
    .withColumn("has_ups", when(col("ups_it_numbers").isNotNull(), True).otherwise(False)) \
    .drop("kaspersky_attempted", "kaspersky_network", "memory_modules", "memory_description", "disk_names", "disk_capacities", "video_memory", "monitor_it_numbers", "ups_it_numbers")


# Загрузка в Clickhouse
final_df.write \
    .format("jdbc") \
    .option("url", ch_url) \
    .option("dbtable", "computers_analytics") \
    .option("user", ch_properties["user"]) \
    .option("password", ch_properties["password"]) \
    .option("driver", ch_properties["driver"]) \
    .mode("append")\
    .save()

spark.stop()  
