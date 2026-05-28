#!/usr/bin/env python3
"""Export data from MySQL database to Excel and JSON.

Environment variables:
    MYSQL_HOST - MySQL host (default: localhost)
    MYSQL_PORT - MySQL port (default: 3306)
    MYSQL_USER - MySQL user (default: root)
    MYSQL_PASSWORD - MySQL password (required)
    MYSQL_DATABASE - MySQL database name (default: neuron)
    EXPORT_PATH - Export output directory (default: ./data/exports)
"""

import json
import os
import sys
from pathlib import Path

import mysql.connector
import openpyxl
from openpyxl import Workbook


def get_config():
    config = {
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD"),
        "database": os.getenv("MYSQL_DATABASE", "neuron"),
        "charset": "utf8mb4",
    }
    if not config["password"]:
        print("Error: MYSQL_PASSWORD environment variable is required", file=sys.stderr)
        sys.exit(1)
    return config


def get_export_path():
    export_path = Path(os.getenv("EXPORT_PATH", "./data/exports"))
    export_path.mkdir(parents=True, exist_ok=True)
    return export_path


QUERY = """
SELECT 
    tr.id as report_id,
    tr.report_cd,
    tr.work_symptom,
    tr.work_detail,
    trp.product_name as device,
    trp.error_cd as error_code,
    tr.total_fee
FROM t_tech_reports tr 
LEFT JOIN t_tech_report_products trp ON trp.t_tech_report_id = tr.id
"""

HEADERS = ["report_id", "report_cd", "work_symptom", "work_detail", "device", "error_code", "total_fee"]


def export_to_json(rows, export_path: Path):
    data = []
    for row in rows:
        data.append({
            "report_id": row[0],
            "report_cd": row[1],
            "work_symptom": row[2] or "",
            "work_detail": row[3] or "",
            "device": row[4] or "",
            "error_code": row[5] or "",
            "total_fee": row[6],
        })

    json_path = export_path / "tech_reports_export.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"JSON saved to: {json_path}")
    return json_path


def export_to_excel(rows, export_path: Path):
    wb = Workbook()
    ws = wb.active
    ws.title = "Tech Reports"
    ws.append(HEADERS)

    for row in rows:
        ws.append(list(row))

    excel_path = export_path / "tech_reports_export.xlsx"
    wb.save(excel_path)
    print(f"Excel saved to: {excel_path}")
    return excel_path


def main():
    config = get_config()
    export_path = get_export_path()

    print(f"Connecting to MySQL: {config['host']}:{config['port']}/{config['database']}")
    conn = mysql.connector.connect(**config)

    print("Executing query...")
    cursor = conn.cursor()
    cursor.execute(QUERY)
    rows = cursor.fetchall()
    print(f"Fetched {len(rows)} rows")

    export_to_json(rows, export_path)
    export_to_excel(rows, export_path)

    cursor.close()
    conn.close()
    print("Done!")


if __name__ == "__main__":
    main()
