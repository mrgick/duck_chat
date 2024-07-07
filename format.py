import argparse
import glob
import os
import subprocess
import sys
from itertools import chain
from pathlib import Path

try:
    import black  # noqa
    import isort  # noqa
    import ruff  # noqa
except Exception as e:
    print(e)
    print("Error: did you run env and install full requirements?")
    quit()

BASE_DIR = Path().parent


def find_dirs() -> list[str]:
    """Get all dirs, not in .gitignore"""
    exclude_dirs = []
    gitignore = BASE_DIR / ".gitignore"
    if gitignore.exists():
        with open(gitignore, "r") as f:
            exclude_dirs = f.readlines()
        exclude_dirs = [x.strip().replace("/", "") for x in exclude_dirs]
        exclude_dirs.append(".git")
    dirs = []
    for f in BASE_DIR.iterdir():
        if f.is_dir() and f.name not in exclude_dirs:
            dirs.append(f)
    return dirs


def find_files(dirs: list) -> list[Path]:
    """Get all python files recursive"""
    files = glob.iglob("*.py", root_dir=BASE_DIR)
    for _dir in dirs:
        f = glob.iglob(f"{_dir}/**/*.py", root_dir=BASE_DIR, recursive=True)
        files = chain(files, f)

    _files = []
    for file in files:
        _file = BASE_DIR.absolute() / file
        _files.append(_file)
    return _files


def parse_args():
    def FilePath(astring):
        file = Path(astring)
        if not file.exists():
            raise argparse.ArgumentTypeError(f"File={file} does not exists!")
        return file

    parser = argparse.ArgumentParser(
        description="Code formatter with ruff, isort and black.",
    )
    parser.add_argument(
        "--files",
        metavar="file",
        type=FilePath,
        nargs="+",
        help="path to file",
        required=False,
    )
    parser.add_argument(
        "--fix",
        action="store",
        nargs="*",
        help="fix code with ruff",
        required=False,
    )
    parser.add_argument(
        "--silent",
        action="store",
        nargs="*",
        help="silent mode, log only errors",
        required=False,
    )

    args = parser.parse_args()
    return args


def run():
    args = parse_args()
    print("Formatting code")

    stdout = None
    if args.silent is not None:
        stdout = subprocess.DEVNULL
        sys.stdout = open(os.devnull, "w")

    files = args.files
    if not files:
        print("Finding files")
        dirs = find_dirs()
        files = find_files(dirs)

    if args.fix is None:
        print("Ruff fixing")
        subprocess.run(
            ["ruff", "check", *files, "--unsafe-fixes", "--fix"], stdout=stdout
        )

    print("Isort fix imports")
    subprocess.run(["isort", *files], stdout=stdout)

    print("Black linting")
    subprocess.run(["black", *files], stderr=stdout, stdout=stdout)

    print("---------Done---------")

    print("Errors unfixed:")
    subprocess.run(["ruff", "check", *files])


if __name__ == "__main__":
    run()
