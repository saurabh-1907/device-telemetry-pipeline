REQUIRED_COLUMNS = {
    "timestamp": "TIMESTAMP",
    "device_id": "VARCHAR",
    "device_model": "VARCHAR",
    "os_build": "VARCHAR",
    "metric": "VARCHAR",
    "value": "DOUBLE",
    "unit": "VARCHAR",
}

ALLOWED_UNITS = {
    "cpu_percent": "%",
    "memory_percent": "%",
    "battery_level": "%",
    "battery_temperature_c": "C",
    "battery_current_ma": "mA",
    "battery_voltage_mv": "mV",
    "disk_read_mb_s": "MB/s",
    "disk_write_mb_s": "MB/s",
}
