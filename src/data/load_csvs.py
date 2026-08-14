"""Load CSV source files into PostgreSQL tables without transforming the data."""

import argparse
import csv
import os
from pathlib import Path
from typing import List

import psycopg
from psycopg import sql


def get_connection() -> psycopg.Connection:
    """Create a PostgreSQL connection from environment variables."""
    required_variables = (
        "POSTGRES_HOST",
        "POSTGRES_PORT",
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
    )

    missing_variables = [
        variable
        for variable in required_variables
        if not os.getenv(variable)
    ]

    if missing_variables:
        raise EnvironmentError(
            "Missing required environment variables: "
            + ", ".join(missing_variables)
        )

    return psycopg.connect(
        host=os.environ["POSTGRES_HOST"],
        port=os.environ["POSTGRES_PORT"],
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )


def get_csv_header(csv_path: Path) -> List[str]:
    """Return the header columns from a CSV file."""
    with csv_path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.reader(file)

        try:
            header = next(reader)
        except StopIteration:
            raise ValueError(f"Empty CSV file: {csv_path}")

    if not header or any(not column.strip() for column in header):
        raise ValueError(f"Invalid header in file: {csv_path}")

    return header


def count_csv_rows(csv_path: Path) -> int:
    """Count data rows in a CSV file, excluding the header."""
    with csv_path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.reader(file)

        try:
            next(reader)
        except StopIteration:
            return 0

        return sum(1 for _ in reader)


def get_table_columns(
    connection: psycopg.Connection,
    table_name: str,
    pg_schema: str,
) -> List[str]:
    """Return PostgreSQL table columns in their defined order."""
    query = """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = %s
          AND table_name = %s
        ORDER BY ordinal_position;
    """

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (pg_schema, table_name),
        )

        return [row[0] for row in cursor.fetchall()]


def validate_columns(
    csv_columns: List[str],
    table_columns: List[str],
    table_name: str,
) -> None:
    """Ensure the CSV structure matches the target PostgreSQL table."""
    if not table_columns:
        raise ValueError(
            f"Target table does not exist: {table_name}"
        )

    if csv_columns != table_columns:
        raise ValueError(
            f"Column mismatch for table '{table_name}'.\n"
            f"CSV columns: {csv_columns}\n"
            f"Table columns: {table_columns}"
        )


def table_has_data(
    connection: psycopg.Connection,
    table_name: str,
    pg_schema: str,
) -> bool:
    """Check whether a target table already contains rows."""
    query = sql.SQL(
        "SELECT EXISTS (SELECT 1 FROM {}.{} LIMIT 1);"
    ).format(
        sql.Identifier(pg_schema),
        sql.Identifier(table_name),
    )

    with connection.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchone()[0]


def load_csv(
    connection: psycopg.Connection,
    csv_path: Path,
    pg_schema: str,
) -> int:
    """Load one CSV file into its corresponding PostgreSQL table."""
    table_name = csv_path.stem
    csv_columns = get_csv_header(csv_path)

    table_columns = get_table_columns(
        connection=connection,
        table_name=table_name,
        pg_schema=pg_schema,
    )

    validate_columns(
        csv_columns=csv_columns,
        table_columns=table_columns,
        table_name=table_name,
    )

    if table_has_data(
        connection=connection,
        table_name=table_name,
        pg_schema=pg_schema,
    ):
        raise RuntimeError(
            f"Table '{table_name}' already contains data. "
            "Load aborted to prevent duplicate records."
        )

    copy_query = sql.SQL(
        """
        COPY {}.{} ({})
        FROM STDIN
        WITH (
            FORMAT CSV,
            HEADER TRUE
        )
        """
    ).format(
        sql.Identifier(pg_schema),
        sql.Identifier(table_name),
        sql.SQL(", ").join(
            sql.Identifier(column)
            for column in csv_columns
        ),
    )

    with connection.cursor() as cursor:
        with cursor.copy(copy_query) as copy:
            with csv_path.open(
                "r",
                encoding="utf-8-sig",
                newline="",
            ) as file:
                while chunk := file.read(1024 * 1024):
                    copy.write(chunk)

    return count_csv_rows(csv_path)


def generate_load_summary(
    loaded_files: int,
    loaded_rows: int,
) -> None:
    """Print a concise loading summary."""
    print("\nLoading completed successfully.")
    print(f"CSV files loaded: {loaded_files}")
    print(f"Rows loaded: {loaded_rows}")


def load_all_csvs(
    input_dir: Path,
    pg_schema: str,
) -> None:
    """Load every CSV file from a directory into PostgreSQL."""
    csv_files = sorted(input_dir.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(
            f"No CSV files found in directory: {input_dir}"
        )

    total_rows = 0

    with get_connection() as connection:
        for csv_path in csv_files:
            table_name = csv_path.stem

            print(f"Loading {csv_path.name} -> {pg_schema}.{table_name}")

            loaded_rows = load_csv(
                connection=connection,
                csv_path=csv_path,
                pg_schema=pg_schema,
            )

            total_rows += loaded_rows

            print(f"  {loaded_rows} rows loaded.")

        # The context manager commits only if all files are loaded successfully.

    generate_load_summary(
        loaded_files=len(csv_files),
        loaded_rows=total_rows,
    )


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Load CSV source files into PostgreSQL."
    )

    parser.add_argument(
        "--input-dir",
        type=Path,
        required=True,
        help="Directory containing the source CSV files.",
    )

    parser.add_argument(
        "--pg-schema",
        default="public",
        help="Target PostgreSQL schema. Default: public",
    )

    return parser.parse_args()


def main() -> None:
    """Run the CSV loading process."""
    args = parse_args()

    load_all_csvs(
        input_dir=args.input_dir,
        pg_schema=args.pg_schema,
    )


if __name__ == "__main__":
    main()