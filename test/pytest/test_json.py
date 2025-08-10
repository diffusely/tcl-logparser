import subprocess
import json
from pathlib import Path
import difflib
import pytest

def test_parsed_logs_match_golden():
	repo_root = Path(__file__).parent.parent.parent
	tcl_script = repo_root / "bin" / "parse_logs.tcl"
	logs_dir = repo_root / "example"
	generated_file = repo_root / "parsed_logs.json"
	golden_file = repo_root / "test" / "golden" / "golden.json"

	try:
		subprocess.run(["tclsh", str(tcl_script), "-path", str(logs_dir)],
					check=True, capture_output=True, text=True)
	except subprocess.CalledProcessError as e:
		error_output = e.stdout + "\n" + e.stderr

		pytest.fail(f"TCL script failed with exit code {e.returncode}.\n{error_output}", pytrace=False)

	with open(generated_file, "r", encoding="utf-8") as f:
		generated_data = json.load(f)

	with open(golden_file, "r", encoding="utf-8") as f:
		golden_data = json.load(f)

	if generated_data != golden_data:
		gen_str = json.dumps(generated_data, indent=4, ensure_ascii=False).splitlines()
		gold_str = json.dumps(golden_data, indent=4, ensure_ascii=False).splitlines()

		diff = difflib.unified_diff(
			gold_str,
			gen_str,
			fromfile='golden.json',
			tofile='generated.json',
			lineterm=''
		)
		print('\n'.join(diff))
		assert False, "Parsed logs JSON does not match the golden reference."
