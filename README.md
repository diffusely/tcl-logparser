# tcl-logparser

## Overview

`tcl-logparser` is a TCL script that recursively scans all `.log` files in a specified directory (and its subdirectories). It parses lines beginning with `error:`, `warning:`, or `info:`, extracting these messages along with their line numbers and organizing the results into a JSON file.

A Python `pytest` script is also provided to automatically verify the correctness of the output by comparing it against a golden reference JSON file.

---

### 1. Run the TCL Log Parser

From the root directory of the project, open the integrated terminal in Visual Studio Code and run:

```sh
tclsh bin/parse_logs.tcl -path example
```

- This command scans all `.log` files inside the `example` directory (and its subdirectories).
- It generates a JSON file `parsed_logs.json` in the root directory containing the parsed log messages.

---

### 2. Run the Automated Test

1. Make sure you have `pytest` installed:

    ```sh
    pip install pytest
    ```

2. Run the test in the terminal:

    ```sh
    pytest test/pytest/test_json_diff.py
    ```

- This test runs the TCL script and compares the generated JSON file with the golden reference.
