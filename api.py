import os
import platform
import psutil
import time
import clickhouse_connect
import meta_data
import sqlite3
import itertools

# CC stands for clickhouse connect
CC_HOST = None
CC_PORT = None
CC_USERNAME = None
CC_PASSWORD = None
CC_VALIDITY: bool = False
# DATA
ProteinTurnoverData: meta_data.ProteinTurnoverDataClass = None

def api_host_informations():
    memory = psutil.virtual_memory()
    total_memory = memory.total / (1024**3)
    used_memory = memory.used / (1024**3)
    memory_percentage = memory.percent
    print(
        f"Memory Usage: {used_memory:.2f} GB / {total_memory:.2f} GB ({memory_percentage}%)"
    )

    disk_usage = psutil.disk_usage("/")
    total_disk = disk_usage.total / (1024**3)
    used_disk = disk_usage.used / (1024**3)
    disk_percentage = disk_usage.percent
    print(f"Disk Usage: {used_disk:.2f} GB / {total_disk:.2f} GB ({disk_percentage}%)")

    uptime_seconds = time.time() - psutil.boot_time()
    uptime_hours = uptime_seconds // 3600
    uptime_minutes = (uptime_seconds % 3600) // 60
    print(f"System Uptime: {int(uptime_hours)} hours, {int(uptime_minutes)} minutes")

    # CPU Usage
    cpu_usage = psutil.cpu_percent(interval=1)
    print(f"CPU Usage: {cpu_usage}%")

    # Logged-in Users
    users = ",".join([user.name for user in psutil.users()])

    # Battery Information
    try:
        battery = psutil.sensors_battery()
        if battery:
            battery_status = f"{battery.percent}% {'charging' if battery.power_plugged else 'not charging'}"
        else:
            battery_status = "No battery"
    except AttributeError:
        battery_status = "Not available"

    return [
        {"key": "Host Name", "value": str(os.name)},
        {"key": "System Type", "value": str(platform.system())},
        {"key": "Processor", "value": str(platform.processor())},
        {"key": "Release Version", "value": str(platform.release())},
        {"key": "CPU Count", "value": str(os.cpu_count())},
        {
            "key": "Memory Usage",
            "value": f"{used_memory:.2f} GB / {total_memory:.2f} GB ({memory_percentage}%)",
        },
        {
            "key": "Disk Usage",
            "value": f"{used_disk:.2f} GB / {total_disk:.2f} GB ({disk_percentage}%)",
        },
        {
            "key": "System Uptime",
            "value": f"{int(uptime_hours)} hours, {int(uptime_minutes)} minutes",
        },
        {"key": "CPU Usage", "value": f"{cpu_usage}%"},
        {"key": "Logged-in Users", "value": users},
        {"key": "Battery Status", "value": battery_status},
    ]

def test_clickhouse_connection(host, port, username, password):
    global CC_HOST
    global CC_PORT
    global CC_USERNAME
    global CC_PASSWORD
    global CC_VALIDITY
    try:
        client = clickhouse_connect.get_client(
            host=host, port=int(port), username=username, password=password
        )
        res = client.ping()
        if res:
            CC_HOST = host
            CC_PORT = port
            CC_USERNAME = username
            CC_PASSWORD = password
            CC_VALIDITY = True
            return True
        else:
            CC_VALIDITY = False
            return False
    except Exception as e:
        return False
    
def get_clickhouse_connection_info():
    global CC_HOST
    global CC_PORT
    global CC_USERNAME
    global CC_PASSWORD
    if CC_HOST and CC_PORT and CC_USERNAME and CC_PASSWORD:
        return {
            'host': CC_HOST,
            'port': CC_PORT,
            'username': CC_USERNAME,
            'password': CC_PASSWORD,
        }
    else:
        return None

def bool_check_clickhouse_connection():
    global CC_VALIDITY
    return CC_VALIDITY
    
def find_all_mzML_pepxml_files_in_dir(dir: str):
    if not os.path.isdir(dir):
        return {
            'status': False,
            'msg': f"Directory`{dir}` does not exist.",
            'files': []
        }
    return {
        'status': True,
        'msg': "",
        'files': [*filter(lambda x: x.endswith('pep.xml') or x.endswith('mzML'), os.listdir(dir))]
    }
    
def initialize_sqlite_db():
    global ProteinTurnoverData
    ProteinTurnoverData = meta_data.ProteinTurnoverDataClass()
    
def create_clickhouse_information(data: list) -> dict:
    error_keys = []
    required_keys = ('name', 'host', 'port', 'username', 'password')
    for idx, datum in enumerate(data):
        if not datum:
            error_keys.append(required_keys[idx])
    if error_keys:
        return {
            'msg': f"The values of the following fields are empty: {','.join(error_keys)}",
            'success': False
        }
    error_msg: str = ''
    success = True
    try:
        ProteinTurnoverData.create_clickhouse_information(data)
    except sqlite3.IntegrityError as e:
        success = False
        error_msg = "The name of the Clickhouse information you added is duplicated."
    except Exception as e:
        success = False
        error_msg = str(e)
    return {
        'msg': error_msg,
        'success': success
    }
    
def read_all_clickhouse_information() -> dict:
    error_msg: str = ''
    success = True
    try:
        data = ProteinTurnoverData.read_all_clickhouse_information()
    except Exception as e:
        success = False
        error_msg = str(e)
    return {
        'msg': error_msg,
        'success': success,
        'data': data
    }
    
def delete_clickhouse_information(id) -> dict:
    error_msg: str = ''
    success = True
    try:
        ProteinTurnoverData.delete_clickhouse_information(id)
    except Exception as e:
        success = False
        error_msg = str(e)
    return {
        'msg': error_msg,
        'success': success,
    }
    
def get_all_names_of_clickhouse_information() -> list:
    error_msg: str = ''
    success = True
    data = None
    try:
        data = ProteinTurnoverData.get_all_names_of_clickhouse_information()
        data = list(map(lambda x: x[0], data))
    except Exception as e:
        success = False
        error_msg = str(e)
    return {
        'msg': error_msg,
        'success': success,
        'data': data
    }
    
def get_clickhouse_information_by_name(name) -> list:
    error_msg: str = ''
    success = True
    data = None
    try:
        data = ProteinTurnoverData.get_clickhouse_information_by_name(name)
    except Exception as e:
        success = False
        error_msg = str(e)
    return {
        'msg': error_msg,
        'success': success,
        'data': data
    }
