"""Handles sqlite tasks.

Used for updating local sqlite databases, primarily the
AMOS chemical functional use classifications.

This is more of an abstract class for the specific use case
ChemFUT.ChemFUTHelper class to inherit from,
which automatically make connections to local snapshots of
the ChemFUT DB AND provide methods for common queries.

This class provides basic utilities:

    1. Creating connections to database and storing
       the connection and cursor objects as attributes.
    2. Inserting rows to local .db files.
    3. A print function to print whole tables, or specify
       a number of rows to print.
    4. A print function to print a description of each table
       in the DB.

E. Tyler Carr
November 20, 2024
"""

from __future__ import annotations
from pathlib import Path
import sqlite3
from typing import Union

# from utils import create_functional_use_tables

PathNoneType = str | Path | None


class SqliteHandler:
    """Handles sqlite tasks.

    To create a connection to a local .db file, call

        >>> sqlite_handler = SqliteHandler()
        >>> sqlite_handler.set_conn("/path/to/database.db")

    The path to the chemFUT DB and DSSTox DB is an attribute,
    so if you want to connect with this class instead of those
    using the chemFUT.ChemFUTHelper class, run

        >>> sqlite_handler.set_conn(sqlite_handler.chem_func_uses_path)
    """

    def __init__(self):
        """Constructor for SqliteHandler"""
        self._chem_func_uses_path = (
            Path(__file__).resolve().parent / "data/ChemFuncT.db"
        )

        self.active_path = None
        self.conn = None
        self.cursor = None

    @property
    def chem_func_uses_path(self):
        return self._chem_func_uses_path

    @chem_func_uses_path.setter
    def chem_func_uses_path(self, db_path: str | Path):
        db_path = Path(str(db_path)).resolve()
        if not self._has_db_suffix(db_path):
            raise ValueError(f"db_path should be a '.db' file, not {db_path}")

        self._chem_func_uses_path = db_path

    def _has_db_suffix(self, path: str | Path) -> bool:
        """Returns True if path suffix is .db"""
        if Path(str(path)).resolve().suffix.lower() == ".db":
            return True
        return False

    def set_conn(self, path: PathNoneType) -> tuple[sqlite3.Connection, sqlite3.Cursor]:
        """sets the self.connection and self.cursor attributes from path"""
        if not self._has_db_suffix(path):
            raise ValueError(f"db_path should be a '.db' file, not {path}")

        conn = sqlite3.connect(path)
        cursor = conn.cursor()

        self.active_path = path
        self.conn = conn
        self.cursor = cursor

    def print_db_description(self):
        """Prints a description of the database, including all tables and their descriptions."""
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = self.cursor.fetchall()

        for table in tables:
            table_name = table[0]
            print(f"Table: {table_name}")

            self.cursor.execute(f"PRAGMA table_info({table_name});")
            columns = self.cursor.fetchall()

            for column in columns:
                print(
                    f"  Column: {column[1]}, Type: {column[2]}, Not Null: {column[3]}, Default: {column[4]}, Primary Key: {column[5]}"
                )

            print("-" * 40)

    def insert_row(self, table_name: str, **kwargs):
        """Inserts a row into an existing table within the current connection.

        First it checks that the table exists in the current db. Next it checks
        that all columns and values were provided in kwargs.

        Catches sqlite3.IntegrityErrors -- no error raised if row already exists.

        Parameters
        ----------
        table_name : str
            The table you want to add a row to
        **kwargs
            These keyword arguments take the form column=value. There must be
            a kw for each column, and no additional kws or it will throw a ValueError.
        """
        ## ensure table exists
        self.cursor.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name=?;
            """,
            (table_name,),
        )
        if not self.cursor.fetchone():
            raise ValueError(f"Table '{table_name}' does not exist.")

        ## ensure that kwargs contains all columns and valid values
        self.cursor.execute(f"PRAGMA table_info({table_name});")
        table_columns = [row[1] for row in self.cursor.fetchall()]
        for key in kwargs.keys():
            if key not in table_columns:
                raise ValueError(f"Column {key} was not found in {table_name}.")
        for col in table_columns:
            if col not in kwargs.keys():
                raise ValueError(
                    f"Column {col} exists in {table_name}, you "
                    + "must provide this as an additional kw argument"
                )

        ## create query
        columns = ", ".join(table_columns)
        placeholders = ", ".join(["?"] * len(table_columns))
        values = tuple(
            kwargs[column] for column in table_columns
        )  ## ensure values are in correct order

        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        ## execute query
        try:
            self.cursor.execute(sql, values)
            self.conn.commit()
        except sqlite3.IntegrityError as e:
            details = "".join(f"\t{key}: {kwargs[key]}\n" for key in kwargs)
            print(f"IntegrityError: {e} - row already existed for \n{details}")

    def print_table(self, table_name: str, limit: int | str | None) -> None:
        """Prints the contents of table_name"""
        if limit is None:
            self.cursor.execute(f"SELECT * FROM {table_name};")
        else:
            self.cursor.execute(f"SELECT *FROM {table_name} LIMIT {limit}")

        rows = self.cursor.fetchall()
        column_names = [description[0] for description in self.cursor.description]

        print(" | ".join(column_names))

        for row in rows:
            print(" | ".join(str(cell) for cell in row))


if __name__ == "__main__":
    pass
