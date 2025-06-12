CREATE TABLE IF NOT EXISTS inventory_db.computers_analytics
(
    computer_id           UInt32,
    building              String,
    room_number           String,
    department            LowCardinality(String),
    responsible           String,
    inventory_number      String,
    serial_number         String,
    ip_address            IPv4,
    mac_address           String,
    kaspersky_installed   Bool,
    kaspersky_in_network  Bool,
    processor_type        LowCardinality(String),
    processor_frequency   Float32,
    ram_total_gb          UInt16,
    disk_total_gb         UInt32,
    video_adapter         LowCardinality(String),
    video_memory_gb       UInt16,
    monitor_model         String,
    monitor_resolution    String,
    has_ups               Bool,
    comment               String,
    load_date             DateTime
)
ENGINE = MergeTree
ORDER BY (department, building, room_number, computer_id);