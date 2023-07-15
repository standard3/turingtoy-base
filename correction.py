import json
import os
import subprocess as sp
from concurrent.futures import (
    ThreadPoolExecutor,
)
from pathlib import (
    Path,
)
from typing import (
    Optional,
)

import typer

app = typer.Typer()

root_clone_dir = Path(".local") / "correction"
root_clone_dir.mkdir(parents=True, exist_ok=True)
root_dir = os.getcwd()

correction_dir = Path("correction")
correction_dir.mkdir(parents=True, exist_ok=True)


def run(command_line: str, *args, **kwargs):
    cp = sp.run(command_line.split(" "), *args, **kwargs)
    return cp


@app.command("clone")
def clone():
    for file_ in Path("./rendu").iterdir():
        clone_dir = root_clone_dir / file_.stem.replace(" ", "-")
        if not file_.stem.startswith("_") and not clone_dir.exists():
            print(clone_dir)
            repo, commit = file_.read_text().splitlines()[:2]
            run(f"git clone {repo} {clone_dir}")
            os.chdir(clone_dir)
            run(f"git checkout -b correction {commit}")
            os.chdir(root_dir)


all_tests_python = {
    "test_turing_machine_double_1": 1,
    "test_turing_machine_add_two_binary_numbers": 1,
    "test_turing_machine_binary_multiplication": 1,
}


@app.command("test-projet")
def test_projet(etudiant: Optional[str] = None):
    results = (
        json.loads((correction_dir / "results_projet.json").read_text())
        if (correction_dir / "results_projet.json").is_file()
        else {}
    )
    log_dir = correction_dir / "logs_projet"
    log_dir.mkdir(exist_ok=True, parents=True)

    def _run(folder):
        if folder.stem != etudiant and folder.stem in [
            "MADELAIN_Anselme",  # boucles infinie
        ]:  # seems to have an infinite loop
            return
        if folder.stem in results:  # already processed
            return
        print(f"Processing {folder}")
        out_lines = []
        result = {}
        for test in all_tests_python:
            result[test] = False
        run(f"rm -r ./src")
        run(f"cp -r {folder}/src .")

        def _run_test(test):
            print(test)
            cp2 = run(
                f".venv/scripts/python -m pytest tests/test_turing.py -k {test}",
                universal_newlines=True,
                stdout=sp.PIPE,
                stderr=sp.PIPE,
            )
            if cp2.returncode != 0:
                result[test] = False
            else:
                result[test] = True
            out_lines.append(f"# {test} stdout:")
            out_lines.append(cp2.stdout)
            out_lines.append(f"# {test} stderr:")
            out_lines.append(cp2.stderr)

        with ThreadPoolExecutor(max_workers=len(all_tests_python)) as executor:
            executor.map(_run_test, all_tests_python)

        out_file = log_dir / folder.stem
        out_file.write_text("\n".join(out_lines))
        results[folder.stem] = result
        (correction_dir / "results_projet.json").write_text(
            json.dumps(results, indent=2)
        )
        print(f"Done {folder}")

    if etudiant is not None:
        _run(root_clone_dir / etudiant)
    else:
        for folder in root_clone_dir.iterdir():
            _run(folder)


@app.command("note")
def note():
    results_projet = json.loads((correction_dir / "results_projet.json").read_text())
    notes = {}

    sum_weight = {
        "projet": 0,
    }
    for weight in all_tests_python.values():
        sum_weight["projet"] += weight

    assert set(results_projet.keys()) == set(results_projet.keys())

    for etudiant in results_projet:
        notes[etudiant] = {
            "projet": 0,
        }
        for test, weight in all_tests_python.items():
            if results_projet[etudiant][test]:
                notes[etudiant]["projet"] += weight

        for item in ["projet"]:
            notes[etudiant][item] /= sum_weight[item]
            notes[etudiant][item] *= 20
            notes[etudiant][item] = round(notes[etudiant][item], 1)
    (correction_dir / "notes.json").write_text(json.dumps(notes, indent=2))


if __name__ == "__main__":
    app()
