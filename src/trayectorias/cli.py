import argparse
from pathlib import Path
from .pipeline import run


def main():
    parser = argparse.ArgumentParser(
        description="TrayectoriasAR: pipeline oficial y auditable"
    )
    parser.add_argument("command", choices=["run"])
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Reproducir los snapshots con verificación SHA-256",
    )
    args = parser.parse_args()
    print("Versión publicada:", run(args.root, args.offline))


if __name__ == "__main__":
    main()
