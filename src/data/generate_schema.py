"""Generate a PostgreSQL schema from CSV files using only Python standard library."""

import argparse
import csv
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Dict, List, Optional


INTEGER_PATTERN = re.compile(r"^[+-]?\d+$")
DECIMAL_PATTERN = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)$")

TEXT_IDENTIFIER_TOKENS = (
    "code",
    "number",
    "phone",
    "postal",
    "cpf",
    "cnpj",
    "tax",
    "registration",
    "sku",
    "barcode",
    "key",
    "series",
)


def quote_identifier(identifier: str) -> str:
    """Safely quote PostgreSQL identifiers."""
    return '"{}"'.format(identifier.replace('"', '""'))


def should_preserve_as_text(column_name: str) -> bool:
    """Identify business identifiers that should not be converted to numbers."""
    normalized = column_name.strip().lower()

    if normalized == "id":
        return False

    if any(token in normalized for token in TEXT_IDENTIFIER_TOKENS):
        return True

    if normalized.endswith("_id"):
        return False

    return False


def infer_scalar_type(value: str, column_name: str) -> Optional[str]:
    """Infer the PostgreSQL type represented by a CSV value."""
    value = value.strip()

    if not value:
        return None

    # Codes and business identifiers may contain leading zeros.
    if should_preserve_as_text(column_name):
        return "TEXT"

    if value.lower() in {"true", "false"}:
        return "BOOLEAN"

    if INTEGER_PATTERN.fullmatch(value):
        return "BIGINT"

    if DECIMAL_PATTERN.fullmatch(value):
        try:
            Decimal(value)
            return "NUMERIC"
        except InvalidOperation:
            pass

    try:
        datetime.fromisoformat(value)
    except ValueError:
        return "TEXT"

    if " " in value or "T" in value:
        return "TIMESTAMP"

    return "DATE"


def merge_types(
    current_type: Optional[str],
    detected_type: Optional[str],
) -> Optional[str]:
    """Combine observed types into one safe PostgreSQL type."""
    if detected_type is None:
        return current_type

    if current_type is None or current_type == detected_type:
        return detected_type

    observed_types = {current_type, detected_type}

    if observed_types <= {"BIGINT", "NUMERIC"}:
        return "NUMERIC"

    if observed_types <= {"DATE", "TIMESTAMP"}:
        return "TIMESTAMP"

    # Mixed incompatible values are conservatively stored as text.
    return "TEXT"


def infer_csv_schema(csv_path: Path) -> Dict[str, str]:
    """Read a CSV file and infer a PostgreSQL type for every column."""
    with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.reader(file)

        try:
            header = next(reader)
        except StopIteration:
            raise ValueError(f"Empty CSV file: {csv_path}")

        if not header or any(not column.strip() for column in header):
            raise ValueError(f"Invalid header in file: {csv_path}")

        if len(header) != len(set(header)):
            raise ValueError(f"Duplicate columns found in file: {csv_path}")

        inferred_types: Dict[str, Optional[str]] = {
            column: None for column in header
        }

        for line_number, row in enumerate(reader, start=2):
            if len(row) != len(header):
                raise ValueError(
                    f"Invalid number of fields at line {line_number} "
                    f"in {csv_path.name}: expected {len(header)}, got {len(row)}"
                )

            for column, value in zip(header, row):
                detected_type = infer_scalar_type(value, column)

                inferred_types[column] = merge_types(
                    inferred_types[column],
                    detected_type,
                )

    # Columns containing only empty values are conservatively defined as TEXT.
    return {
        column: data_type or "TEXT"
        for column, data_type in inferred_types.items()
    }


def render_create_table(
    table_name: str,
    columns: Dict[str, str],
) -> str:
    """Create a PostgreSQL CREATE TABLE statement."""
    definitions = [
        f"    {quote_identifier(column)} {data_type}"
        for column, data_type in columns.items()
    ]

    return (
        f"CREATE TABLE IF NOT EXISTS {quote_identifier(table_name)} (\n"
        + ",\n".join(definitions)
        + "\n);"
    )


def generate_schema(input_dir: Path, output_file: Path) -> None:
    """Generate one SQL schema containing a table for every CSV file."""
    csv_files = sorted(input_dir.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(
            f"No CSV files found in directory: {input_dir}"
        )

    statements: List[str] = []

    for csv_path in csv_files:
        table_name = csv_path.stem
        columns = infer_csv_schema(csv_path)

        statements.append(
            render_create_table(table_name, columns)
        )

    output_file.parent.mkdir(parents=True, exist_ok=True)

    schema_content = (
        "-- Auto-generated PostgreSQL schema.\n"
        "-- Source: LH Nautical CSV files.\n\n"
        + "\n\n".join(statements)
        + "\n"
    )

    output_file.write_text(
        schema_content,
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Generate PostgreSQL CREATE TABLE statements "
            "from CSV files."
        )
    )

    parser.add_argument(
        "--input-dir",
        type=Path,
        required=True,
        help="Directory containing the source CSV files.",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("schema.sql"),
        help="Generated SQL file path. Default: schema.sql",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    generate_schema(
        input_dir=args.input_dir,
        output_file=args.output,
    )

    print(f"Schema generated successfully: {args.output}")


if __name__ == "__main__":
    main()