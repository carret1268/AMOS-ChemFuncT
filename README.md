# Chemical Function Taxonomy (ChemFuncT)

[![PyPI version](https://img.shields.io/pypi/v/ChemFuncT.svg)](https://pypi.org/project/ChemFuncT/)
[![License: CC0-1.0](https://img.shields.io/badge/license-CC0--1.0-blue.svg)](https://creativecommons.org/publicdomain/zero/1.0/)


The Analytical Methods and Open Spectra (AMOS) Database's Chemical Function Taxonomy (ChemFuncT) contains mappings between chemicals (via name and DTXSID) and their functional uses. This repository contains a snapshot of the SQLite database and a Python class to help query the database.

## Sources

This dataset was compiled using information from:

- Wikipedia – General-purpose encyclopedia entries on chemical uses.
- [ChemExpo](https://comptox.epa.gov/chemexpo/) – A web application that surfaces reported chemical function use from the EPA's CPDat database.
- [DrugBank](https://go.drugbank.com/) – Pharmaceutical chemical uses and mechanisms.
- [APPRIL](https://ordspub.epa.gov/ords/pesticides/f?p=APPRIL_PUBLIC:2::::::) – The EPA's Active Pesticide Product Registration Informational Listing.

## ChemFuncT Database

A snapshot of the data is contained in `data/ChemFuncT.db`. Here is an ER diagram representation of the database.

![ChemFuncT ER Diagram](https://github.com/carret1268/AMOS-ChemFuncT/blob/main/resources/ER_diagram.png?raw=true)

Descriptions of each table and their variables follow:

| Table | Description |
|-------|-------------|
| Sources | Contains unique identifiers for each source that data was pulled from. |
| Chemicals | Maps the unique chemical identifier (DTXSID) to its chemical name. |
| Classifications | Maps a unique classification ID to a human readable class name (e.g., Pharmaceuticals) and a description of that class. |
| ChemicalClassifications | Maps chemicals (by DTXSID) to their classifications, and which source that classification came from. |
| SourceMappings | Contains the raw category pulled from a given source mapped to a harmonized ChemFuncT class. |
| ClassificationHierarchy | Contains parent/child mappings for each classification. |

### Sources Table

| Variable | Role | Description |
|----------|------|-------------|
| source_id | PK  | A unique identifier for each source. E.g., "wikipedia", "drugbank". |

### Chemicals Table

| Variable | Role | Description |
|----------|------|-------------|
| dtxsid   | PK   | The unique DTXSID for each chemical. |
| name     |      | The EPA's preferred name for each chemical. |

### Classifications Table

| Variable | Role | Description |
|----------|------|-------------|
| id       | PK   | A unique identifier for each classification of the form func_0001. |
| classification || A human readable name for each classification (e.g., Pharmaceuticals). |
| description |   | A description for each classification. |

### ChemicalClassifications Table

| Variable | Role | Description |
|----------|------|-------------|
| dtxsid   | CPK, FK $\rightarrow$ `Chemicals.dtxsid` | The unique DTXSID chemical identifier. |
| classification_id | CPK, FK $\rightarrow$ `Classifications.id` | A unique identifier for each classification. |
| source_id | CPK, FK $\rightarrow$ `Sources.source_id` | The unique source_id for each source. |

### SourceMappings Table

| Variable | Role | Description |
|----------|------|-------------|
| id       | CPK, FK $\rightarrow$ `Classifications.id` | A unique identifier for each classification. |
| source_category | CPK | The raw category pulled from the source that was mapped to the given `id`. |
| source_id | CPK, FK $\rightarrow$ `Sources.source_id | The unique source_id for each source. |

### ClassificationHierarchy

| Variable | Role | Description |
|----------|------|-------------|
| child_id | CPK, FK $\rightarrow$ `Classifications.id` | The unique classification identifier for the child node. |
| parent_id | CPK, FK $\rightarrow$ `Classifications.id` | The unique classification identifier for the parent node. |

## Usage

For the ChemFuncT.ChemFuncTHelper class to work by default, you must use the following directory structure:

![Expected directory structure](https://github.com/carret1268/AMOS-ChemFuncT/blob/main/resources/directory_tree.png?raw=true)

For more information about any given method and its parameters, check the respective docstring in the source code.

### Connecting to ChemFuncT.db

If using the recommended directory structure, the path to ChemFuncT.db is correctly set within the `sqlite_handler.SqliteHandler.chem_func_uses_path` attribute such that instantiating an instance of `ChemFuncT.ChemFuncTHelper` will automatically connect to the database and set the resulting `sqlite3.Connection` and `sqlite3.Cursor` objects to the `ChemFuncT.ChemFuncTHelper.conn` and `ChemFuncT.ChemFuncTHelper.cursor` attributes, respectively.

```python
from chemFuncT import ChemFuncTHelper

FuncDB = ChemFuncTHelper()
```

If using a different directory structure, you can specify the path of your `.db` file when instantiating `ChemFuncT.ChemFuncTHelper` as a string or a `pathlib.Path` object.

```python
FuncDB = ChemFuncTHelper("./path/to/ChemFuncT.db")
```

### Print Database/Table Descriptions

#### ChemFuncTHelper.print_db_description()

This method will print a description of each table with its columns to the console.

```python
FuncDB = ChemFuncTHelper()
FuncDB.print_db_description()
```

Example output:

```dummy
Table: Chemicals
  Column: dtxsid, Type: TEXT, Not Null: 0, Default: None, Primary Key: 1
  Column: name, Type: TEXT, Not Null: 1, Default: None, Primary Key: 0
 ----------------------------------------
Table: Classifications
  Column: id, Type: TEXT, Not Null: 0, Default: None, Primary Key: 1
  Column: classification, Type: TEXT, Not Null: 1, Default: None, Primary Key: 0
  Column: description, Type: TEXT, Not Null: 0, Default: None, Primary Key: 0
----------------------------------------
Table: ChemicalClassifications
  Column: dtxsid, Type: TEXT, Not Null: 1, Default: None, Primary Key: 1
  Column: classification_id, Type: TEXT, Not Null: 1, Default: None, Primary Key: 2
  Column: source_id, Type: TEXT, Not Null: 1, Default: None, Primary Key: 3
----------------------------------------
Table: ClassificationHierarchy
  Column: child_id, Type: TEXT, Not Null: 1, Default: None, Primary Key: 1
  Column: parent_id, Type: TEXT, Not Null: 0, Default: None, Primary Key: 2
----------------------------------------
Table: SourceMappings
  Column: id, Type: TEXT, Not Null: 1, Default: None, Primary Key: 1
  Column: source_category, Type: TEXT, Not Null: 1, Default: None, Primary Key: 2
  Column: source_id, Type: TEXT, Not Null: 1, Default: None, Primary Key: 3
----------------------------------------
Table: Sources
  Column: source_id, Type: TEXT, Not Null: 1, Default: None, Primary Key: 1
----------------------------------------
```

#### ChemFuncTHelper.print_table()

This method will print the contents of a table from the database. The user specifies the number of rows they want printed. To print the first 10 rows of the `SourceMappings` table:

```python
FuncDB = ChemFuncTHelper()
FuncDB.print_table(table_name="SourceMappings", limit=10)
```

To print every row of the `Sources` table:

```python
FuncDB = ChemFuncTHelper()
FuncDB.print_table(table_name="Sources", limit=None)
```

### Making Queries

#### ChemFuncTHelper.query_hierarchy_paths()

This method will return every possible hierarchical path starting from each root node. The returned data structure is by default a tuple of two lists of strings. The first list contains the paths with the classes encoded with their classification id (e.g., func_0004), the second list contains the paths with the class names. Each element represents one possible path (e.g., ['Drugs -> Pharmaceuticals -> Respiratory Drugs -> Anti-allergic Agents', 'Drugs -> Pharmaceuticals -> Respiratory Drugs -> Anti-allergic Agents -> Antihistamines']). Notice that the delimiter ' -> ' points from parent to child.

This method might be useful for further processing, things like determining the longest path from a root node to a leaf node.

```python
FuncDB = ChemFuncTHelper()
id_paths, class_name_paths = FuncDB.query_hierarchy_paths()
```

#### ChemFuncTHelper.get_chem_name()

Takes a DTXSID as a required parameter and returns the chemical name.

```python
FuncDB = ChemFuncTHelper()
dtxsid = "DTXSID9020112"
chem_name = FuncDB.get_chem_name(dtxsid)
print(chem_name)
```

> Atrazine

#### ChemFuncTHelper.get_class_id_from_name()

Takes a class name and returns its class id.

```python
FuncDB = ChemFuncTHelper()
class_name = "Pharmaceuticals"
class_id = FuncDB.get_class_id_from_name(class_name)
print(class_id)
```

> func_0231

#### ChemFuncTHelper.get_class_name_from_id()

Takes a class id and returns its name.

```python
FuncDB = ChemFuncTHelper()
class_id = "func_0231"
class_name = FuncDB.get_class_id_from_name(class_id)
print(class_name)
```

> Pharmaceuticals

#### ChemFuncTHelper.get_chem_classes()

Returns the classes that a chemical (from DTXSID) is a member of. This method is fairly robust in that it allows many alterations of your output through the optional parameters.

It should be noted that the hierarchy of classes is not retained in the returned value - it is either a list of classes or a semicolon delimited string.

To return all classes that Atrazine is a member of, from all sources:

```python
FuncDB = ChemFuncTHelper()
dtxsid = "DTXSID9020112"
atrazine_classes = FuncDB.get_chem_classes(dtxsid)
print(atrazine_classes)
```

> Additives; Biocides; Biologicals; Fertilizers; Herbicides; Hormones; Industrial Chemicals; Pesticides; Soil Additives; Xenohormones

To only get the classes for Atrazine that came from APPRIL in a list:

```python
FuncDB = ChemFuncTHelper()
dtxsid = "DTXSID9020112"
atrazine_classes = FuncDB.get_chem_classes(dtxsid, sources=["appril"], as_str=False)
print(atrazine_classes)
```

> ['Additives', 'Biocides', 'Fertilizers', 'Herbicides', 'Industrial Chemicals', 'Pesticides', 'Soil Additives']

To return the classification IDs instead of the class names:

```python
FuncDB = ChemFuncTHelper()
dtxsid = "DTXSID9020112"
atrazine_classes = FuncDB.get_chem_classes(dtxsid, names=False, sources=["appril"], as_str=False)
print(atrazine_classes)
```

> ['func_0005', 'func_0087', 'func_0153', 'func_0181', 'func_0189', 'func_0227', 'func_0269']

### ChemFuncTHelper.get_chem_classes_batch()

This function is a wrapper for `ChemFunctHelper.get_chem_classes()` that allows you to return the functional use classes for a list of DTXSIDs.

```python
FuncDB = ChemFuncTHelper()
dtxsids = ["DTXSID9020112", "DTXSID2020006"]
batch_classes = FuncDB.get_chem_classes(dtxsids)
```

#### ChemFuncTHelper.get_class_parents()

Returns the direct parents of a given class (accepts either class name or class id).

```python
FuncDB = ChemFuncTHelper()
class_name = "Antinematodal Agents"
parents = FuncDB.get_class_parents(class_name)
print(parents)
```

> ['Anthelmintics', 'Nematicides']

#### ChemFuncTHelper.get_class_children()

Returns the direct children of a given class (accepts either class name or class id).

```python
FuncDB = ChemFuncTHelper()
class_name = "Biocides"
children = FuncDB.get_class_parents(class_name)
print(children)
```

> ['Acaricides', 'Algicides', 'Antifouling Agents', 'Antimicrobial Agents', 'Antimycotics', 'Antiparasitics', 'Avicides', 'Chemosterilants', 'Fumigants', 'Fungicides', 'Fungistats', 'Herbicides', 'Insecticides', 'Molluscicides', 'Nematicides', 'Spermicides', 'Sporicide', 'Sterilizing Agents']

#### ChemFuncTHelper.export_db_to_excel()

This method generates a data dump of `ChemFuncT.db` in the form of a `.xlsx` file. This requires the openpyxl library.

```python
FuncDB = ChemFuncTHelper()
FuncDB.export_db_to_excel("./path/to/ChemFuncT_datadump.xlsx")
```

## Installation

### Option 1 - install from PyPI

`pip install ChemFuncT`

### Option 2 - install from source

```bash
git clone https://github.com/carret1268/AMOS-ChemFuncT.git
cd AMOS-ChemFuncT
pip install -e
```

This uses your local source files directly, so any changes you make are reflected immediately without reinstalling.

## License

[![CC0](https://licensebuttons.net/p/zero/1.0/88x31.png)](https://creativecommons.org/publicdomain/zero/1.0/)
This project is released under [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/).
