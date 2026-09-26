"""Prepara autenticación local; no registra usuarios ni claves en Snowflake."""

import argparse, json, os, re
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

p = argparse.ArgumentParser()
p.add_argument("--account", required=True)
p.add_argument(
    "--directory", type=Path, default=Path.home() / ".config/trayectorias/snowflake"
)
a = p.parse_args()
if not re.fullmatch(r"[A-Za-z0-9_.-]+", a.account):
    raise ValueError("Identificador inválido")
folder = a.directory
folder.mkdir(parents=True, exist_ok=True)
folder.chmod(0o700)
keyfile = folder / "rsa_key.p8"
if not keyfile.exists():
    key = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    with os.fdopen(
        os.open(keyfile, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "wb"
    ) as f:
        f.write(
            key.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.PKCS8,
                serialization.NoEncryption(),
            )
        )
else:
    keyfile.chmod(0o600)
    key = serialization.load_pem_private_key(keyfile.read_bytes(), password=None)
public = (
    key.public_key()
    .public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
    )
    .decode()
)
(folder / "rsa_key.pub").write_text(public)
body = "".join(public.splitlines()[1:-1])
(
    folder / "registrar_pipeline.sql"
).write_text(f"""-- Ejecutar una sola vez en Snowflake con tu sesión administradora.
-- Crea un usuario de servicio exclusivo, sin contraseña, con el rol del proyecto.
-- Contiene únicamente la clave pública; la privada queda en tu equipo.
USE ROLE SECURITYADMIN;
CREATE USER TRAYECTORIAS_PIPELINE
 TYPE=SERVICE
 DEFAULT_ROLE=TRAYECTORIAS_ROLE
 DEFAULT_WAREHOUSE=TRAYECTORIAS_WH
 RSA_PUBLIC_KEY='{body}'
 COMMENT='Pipeline de portfolio TrayectoriasAR';
GRANT ROLE TRAYECTORIAS_ROLE TO USER TRAYECTORIAS_PIPELINE;
-- Tu usuario personal y su MFA no se modifican.
""")
config = {
    "SNOWFLAKE_ACCOUNT": a.account,
    "SNOWFLAKE_USER": "TRAYECTORIAS_PIPELINE",
    "SNOWFLAKE_ROLE": "TRAYECTORIAS_ROLE",
    "SNOWFLAKE_WAREHOUSE": "TRAYECTORIAS_WH",
    "SNOWFLAKE_DATABASE": "TRAYECTORIAS_AR",
    "SNOWFLAKE_PRIVATE_KEY_PATH": str(keyfile),
}
with os.fdopen(
    os.open(folder / "connection.json", os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600),
    "w",
) as f:
    os.fchmod(f.fileno(), 0o600)
    json.dump(config, f, indent=2)
print("Archivos preparados; clave privada con modo 600. Registro remoto pendiente.")
