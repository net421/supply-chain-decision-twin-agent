from src.utils import get_connection, read_sql_file

VALIDATION_FILES = [
    "sql/validation/validate_kpi_ranges.sql",
    "sql/validation/validate_inventory_rules.sql",
    "sql/validation/validate_recommendations.sql",
]

def run_validations():
    conn = get_connection()
    failures = {}

    for file_path in VALIDATION_FILES:
        query = read_sql_file(file_path)
        rows = conn.execute(query).fetchall()
        failures[file_path] = rows

    conn.close()
    return failures

if __name__ == "__main__":
    failures = run_validations()
    for name, rows in failures.items():
        status = "PASS" if len(rows) == 0 else "FAIL"
        print(f"{name}: {status} ({len(rows)} rows)")
