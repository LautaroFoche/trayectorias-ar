"""Backup local reproducible en estructura, sin entornos, secretos ni historial Git."""

import argparse
from pathlib import Path
import tarfile


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    current = (root / "reports/current").resolve().name
    cloud = (
        (root / "reports/snowflake/current").resolve().name
        if (root / "reports/snowflake/current").exists()
        else None
    )
    excluded = {
        ".venv",
        ".airflow-venv",
        ".airflow",
        ".git",
        ".pytest_cache",
        "__pycache__",
        "deliverables",
        "node_modules",
    }

    def allowed(info):
        parts = Path(info.name).parts[1:]
        if any(p in excluded for p in parts):
            return None
        if any(
            p.endswith((".pem", ".p8", ".key", ".pyc")) or p == ".env" for p in parts
        ):
            return None
        if parts[:2] == ("reports", "runs") and len(parts) > 2 and parts[2] != current:
            return None
        if (
            parts[:3] == ("reports", "snowflake", "runs")
            and len(parts) > 3
            and parts[3] != cloud
        ):
            return None
        if parts and parts[-1] == ".pipeline.lock":
            return None
        return info

    args.output.parent.mkdir(parents=True, exist_ok=True)
    # Symlinks relativos conservados: el replay puede cambiar reports/current al extraer.
    with tarfile.open(args.output, "w:gz", dereference=False) as archive:
        for path in sorted(root.iterdir()):
            archive.add(path, arcname="PROYECTO1/" + path.name, filter=allowed)
    print(args.output, args.output.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
