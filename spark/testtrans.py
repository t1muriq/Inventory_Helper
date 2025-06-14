from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, regexp_extract, sum as spark_sum, when, current_timestamp, concat_ws, coalesce, upper, lower, regexp_replace, collect_list, concat_ws 


spark = SparkSession.builder \
    .appName("PostgresToClickhouseETL") \
    .config("spark.jars", "file:///C:/Users/Timur/PycharmProjects/Inventory_Helper/Inventory_Helper/spark/libs/postgresql-42.2.18.jar") \
    .getOrCreate()

# Параметры подключения к PostgreSQL
pg_url = "jdbc:postgresql://localhost:5435/inventory_db"
pg_properties = {
    "user": "postgres",
    "password": "123",
    "driver": "org.postgresql.Driver"
}

def read_table(table_name):
    return spark.read.jdbc(url=pg_url, table=table_name, properties=pg_properties)

# Чтение всех таблиц
buildings_df = read_table("buildings")
rooms_df = read_table("rooms")
computers_df = read_table("computers")
memory_modules_df = read_table("memory_modules")
processors_df = read_table("processors")
motherboards_df = read_table("motherboards")
disks_df = read_table("disks")
video_adapters_df = read_table("video_adapters")
monitors_df = read_table("monitors")
upss_df = read_table("upss")

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

final_df = final_df \
    .withColumn("kaspersky_installed", when(lower(col("kaspersky_attemted")) == 'да',True).otherwise(False)) \
    .withColumn("kaspersky_in_network", when(lower(col("kaspersky_network")) == "ru",True).otherwise(False))