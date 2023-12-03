import os
import platform
import psutil
import time
import clickhouse_connect
import meta_data
import sqlite3
import json
import sqls
import pyopenms as oms
from pyteomics import pepxml

# CC stands for clickhouse connect
CC_HOST = None
CC_PORT = None
CC_USERNAME = None
CC_PASSWORD = None
CC_VALIDITY: bool = False
# DATA
ProteinTurnoverData: meta_data.ProteinTurnoverDataClass = None

class ClickhouseConnection:
    def __init__(self):
        global CC_HOST
        global CC_PORT
        global CC_USERNAME
        global CC_PASSWORD
        self.host = CC_HOST
        self.port = CC_PORT
        self.username = CC_USERNAME
        self.password = CC_PASSWORD
        self.client = None

    def __enter__(self):
        self.client = clickhouse_connect.get_client(
            host=self.host, port=int(self.port), username=self.username, password=self.password
        )
        return self.client

    def __exit__(self, exc_type, exc_value, traceback):
        if self.client is not None:
            self.client.close()

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
    client = None
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
    finally:
        if client is not None:
            client.close()
    
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
            'files': [],
            'sep': os.path.sep
        }
    return {
        'status': True,
        'msg': "",
        'files': [*filter(lambda x: x.endswith('pep.xml') or x.endswith('mzML'), os.listdir(dir))],
        'sep': os.path.sep
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

def load_files_sse(file_paths: list):
    for path in file_paths:
        filename: str = os.path.basename(path)
        yield convert_sse_data_string({"data": "", "status": "process", "message": f"Start processing file '{filename}'"})
        if filename.endswith('xml'):
            yield from load_pepxml_data(path)
        elif filename.endswith('mzML'):
            yield from load_mzml_data(path)
        else:
            yield convert_sse_data_string({"data": "", "status": "error", "message": f"The file '{filename}' format is incorrect."})
            
    yield convert_sse_data_string({"data": "1", "status": "FIN"})
    
def convert_sse_data_string(json_data: dict) -> str:
    return f"data: {json.dumps(json_data)}\n\n"

def create_protein_turnover_data_table(table_name: str, sqls_gen_func):
    with ClickhouseConnection() as c:
        table_exist = c.query(sqls.make_find_table_in_system_table(table_name))
        if not table_exist.result_rows or all(not row for row in table_exist.result_rows):
            yield convert_sse_data_string({"data": "", "status": "process", "message": f"The table '{table_name}' does not exist, preparing to create it"})
        else:
            yield convert_sse_data_string({"data": "", "status": "error", "message": f"The table '{table_name}' exists, terminate the process."})
            yield convert_sse_data_string({"data": "1", "status": "FIN"})
            return
        try:
            c.command(sqls_gen_func(table_name))
            yield convert_sse_data_string({"data": "", "status": "process", "message": f"Table '{table_name}' created successfully"})
        except Exception as e:
            yield convert_sse_data_string({"data": "", "status": "error", "message": f"Table '{table_name}' created unsuccessfully"})
            yield convert_sse_data_string({"data": "1", "status": "FIN"})
    
def create_pepxml_tbl(table_name: str):
    yield from create_protein_turnover_data_table(table_name, sqls.make_pepxml_create_table_sql)
    
def create_mzml_tbl(table_name: str):
    yield from create_protein_turnover_data_table(table_name, sqls.make_mzml_create_table_sql)

def load_pepxml_data(file_path: str):
    filename: str = os.path.basename(file_path)
    table_name = filename.lower().replace(".", "_")
    yield from create_pepxml_tbl(table_name)
    data = pepxml.DataFrame(file_path)
    yield convert_sse_data_string({"data": "", "status": "process", "message": f"Load File '{filename}' successfully"})
    with ClickhouseConnection() as c:
        try:
            c.insert_df(table=sqls.get_full_table_name(table_name), df=data, database='default')
            yield convert_sse_data_string({"data": "", "status": "success", "message": f"Insert file data '{filename}' successfully"})
        except Exception as e:
            yield convert_sse_data_string({"data": "", "status": "error", "message": f"Error: {str(e)} when loading file '{filename}'"})
    
def load_mzml_data(file_path: str):
    filename: str = os.path.basename(file_path)
    table_name = filename.lower().replace(".", "_")
    yield from create_mzml_tbl(table_name)
    exp = oms.MSExperiment()
    oms.MzMLFile().load("/home/cyan/nan/data/F4_12C.mzML", exp)
    yield convert_sse_data_string({"data": "", "status": "process", "message": f"Load File '{filename}' successfully"})
    data = exp.get_df()
    with ClickhouseConnection() as c:
        try:
            c.insert_df(table=sqls.get_full_table_name(table_name), df=data, database='default')
            yield convert_sse_data_string({"data": "", "status": "success", "message": f"Insert file data '{filename}' successfully"})
        except Exception as e:
            yield convert_sse_data_string({"data": "", "status": "error", "message": f"Error: {str(e)} when loading file '{filename}'"})
        