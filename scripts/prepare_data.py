import json
import os


def prepare_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_file = os.path.join(base_dir, "tech_reports_export.json")
    output_file = os.path.join(base_dir, "data", "tech_reports_rag.json")

    print(f"Loading data from {input_file}...")

    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"Loaded {len(data)} records")

    rag_data = []
    for idx, record in enumerate(data):
        device_info = record.get("device", "") or ""
        error_code_info = record.get("error_code", "") or ""

        text_for_search = record.get("work_symptom", "") or ""
        if device_info:
            text_for_search = f"{text_for_search} [Device: {device_info}]"
        if error_code_info:
            text_for_search = f"{text_for_search} [Error: {error_code_info}]"

        rag_record = {
            "id": idx,
            "text": text_for_search,
            "metadata": {
                "report_id": record.get("report_id"),
                "report_cd": record.get("report_cd"),
                "work_symptom": record.get("work_symptom", ""),
                "work_detail": record.get("work_detail", ""),
                "device": device_info,
                "error_code": error_code_info,
                "total_fee": record.get("total_fee"),
            },
        }
        rag_data.append(rag_record)

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(rag_data, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(rag_data)} records to {output_file}")


if __name__ == "__main__":
    prepare_data()
