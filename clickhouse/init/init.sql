CREATE TABLE IF NOT EXISTS inventory_db.computers_analytics
(
    computer_id           UInt32,
    building              String,
    room_number           String,
    department            LowCardinality(String),
    responsible           String,
    inventory_number      Nullable(String),
    serial_number         Nullable(String),
    ip_address            IPv4,
    mac_address           String,
    kaspersky_installed   Bool,
    kaspersky_in_network  Bool,
    processor_type        LowCardinality(String),
    processor_frequency   Nullable(Float32),
    ram_total_mb          UInt32,
    disk_total_gb         UInt16,
    video_adapter         LowCardinality(String),
    video_memory_mb       Nullable(UInt16),
    monitor_model         Nullable(String),
    monitor_resolution    Nullable(String),
    has_ups               Bool,
    comment               Nullable(String),
    load_date             Nullable(DateTime)
)
ENGINE = MergeTree
ORDER BY (department, building, room_number, computer_id);