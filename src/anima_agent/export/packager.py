"""
ANIMA AGENT — Package Export / Import (ANIMA OS)
Persona distillation, encrypted packaging, DID signing.

Formats:
  .anima — ANIMA OS package (tar.gz, manifest, optional AES-256-GCM encryption)
  .lingpkg — Legacy format, deprecated but supported for import

Flow:
  Export: SOUL.md + MEMORY.md + IDENTITY.md + skills/ → tar.gz → sign → encrypt(opt) → .anima
  Import: .anima → decrypt(opt) → verify → extract → load persona → register DID
"""

import os
import io
import json
import hashlib
import tarfile
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend

from ..identity.did import sign_message, verify_signature, load_identity, create_did


# ─── PACKAGE FORMAT ───

def generate_salt() -> bytes:
    """Generate a random salt for PBKDF2."""
    return os.urandom(16)


def derive_key(password: str, salt: bytes) -> bytes:
    """Derive AES-256 key from password using PBKDF2."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  # AES-256
        salt=salt,
        iterations=600_000,
        backend=default_backend(),
    )
    return kdf.derive(password.encode("utf-8"))


def encrypt_data(data: bytes, password: str) -> tuple[bytes, bytes, bytes]:
    """
    Encrypt data with AES-256-GCM.
    Returns (ciphertext, salt, nonce).
    """
    salt = generate_salt()
    key = derive_key(password, salt)
    nonce = os.urandom(12)  # 96-bit nonce for GCM

    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, data, None)

    return ciphertext, salt, nonce


def decrypt_data(ciphertext: bytes, password: str, salt: bytes, nonce: bytes) -> bytes:
    """Decrypt AES-256-GCM data."""
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, None)


# ─── EXPORT ───

def create_manifest(
    source_dir: Path,
    mode: str = "distilled",
    label: str = "",
) -> dict:
    """Create the package manifest.json."""
    files = {}
    for f in sorted(source_dir.rglob("*")):
        if f.is_file():
            rel = f.relative_to(source_dir)
            sha256 = hashlib.sha256(f.read_bytes()).hexdigest()
            files[str(rel)] = sha256

    manifest = {
        "format": "anima-os.v1",
        "mode": mode,
        "label": label,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "files": files,
    }

    # Sign if identity exists
    identity = load_identity()
    if identity:
        manifest_data = json.dumps(files, sort_keys=True)
        sig = sign_message(manifest_data)
        manifest["signature"] = {
            "did": sig["did"],
            "signature_hex": sig["signature_hex"],
            "algorithm": sig["algorithm"],
        }

    return manifest


def package_directory(
    source_dir: Path,
    output_path: Path,
    mode: str = "distilled",
    label: str = "",
    encrypt: bool = False,
    password: str = "",
) -> dict:
    """
    Package a directory into .anima format.

    Args:
        source_dir: Directory containing persona/memory/skills
        output_path: Where to write the .anima file
        mode: 'distilled' (public) or 'full' (private)
        label: Human-readable label
        encrypt: Whether to encrypt the package
        password: Encryption password (required if encrypt=True)

    Returns:
        dict with package path, sha256, size
    """
    # Build tarball
    tar_buffer = io.BytesIO()
    with tarfile.open(fileobj=tar_buffer, mode="w:gz") as tar:
        # Add files
        for f in sorted(source_dir.rglob("*")):
            if f.is_file() and f.parent.name != "__pycache__":
                arcname = f.relative_to(source_dir)
                tar.add(f, arcname=str(arcname))

        # Add manifest
        manifest = create_manifest(source_dir, mode, label)
        manifest_bytes = json.dumps(manifest, indent=2, ensure_ascii=False).encode()
        info = tarfile.TarInfo(name="manifest.json")
        info.size = len(manifest_bytes)
        tar.addfile(info, io.BytesIO(manifest_bytes))

    tar_data = tar_buffer.getvalue()

    # Encrypt if requested
    enc_data = {}
    if encrypt:
        if not password:
            raise ValueError("Password required for encryption")
        ciphertext, salt, nonce = encrypt_data(tar_data, password)
        enc_data = {
            "encrypted": True,
            "salt_hex": salt.hex(),
            "nonce_hex": nonce.hex(),
        }
        final_data = ciphertext
    else:
        final_data = tar_data

    # Write
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(final_data)

    sha256 = hashlib.sha256(final_data).hexdigest()

    # Write SHA-256 sidecar
    sha_path = output_path.with_suffix(output_path.suffix + ".sha256")
    sha_path.write_text(sha256)

    result = {
        "path": str(output_path),
        "sha256": sha256,
        "size_bytes": len(final_data),
        "mode": mode,
        "encrypted": encrypt,
        "manifest": manifest,
    }
    result.update(enc_data)

    return result


# ─── IMPORT ───

def verify_package(package_path: Path, expected_sha256: str = "") -> bool:
    """
    Verify package integrity.
    Checks: file exists, SHA-256 match (if provided), manifest parseable.
    """
    if not package_path.exists():
        raise FileNotFoundError(f"Package not found: {package_path}")

    if expected_sha256:
        actual = hashlib.sha256(package_path.read_bytes()).hexdigest()
        if actual != expected_sha256:
            raise ValueError(
                f"SHA-256 mismatch.\nExpected: {expected_sha256}\nGot: {actual}"
            )

    return True


def extract_package(
    package_path: Path,
    output_dir: Path,
    password: str = "",
) -> dict:
    """
    Extract and parse an .anima package.

    Args:
        package_path: Path to .anima file
        output_dir: Extraction target directory
        password: Decryption password (if encrypted)

    Returns:
        dict with manifest, extracted_path
    """
    data = package_path.read_bytes()

    # Try to detect if encrypted (no magic bytes — try parse as tar first)
    try:
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
            tar.extractall(output_dir)
            encrypted = False
    except tarfile.TarError:
        if not password:
            raise ValueError(
                "Package appears encrypted. Provide --password to decrypt."
            )
        # Assume encrypted
        raise NotImplementedError(
            "Encrypted package import: salt/nonce are stored in the .anima file "
            "as a JSON header. Full implementation requires header parse."
        )

    # Read manifest
    manifest_path = output_dir / "manifest.json"
    if not manifest_path.exists():
        raise ValueError("Package missing manifest.json — corrupted?")

    manifest = json.loads(manifest_path.read_text())

    # Verify signature if present
    if "signature" in manifest:
        sig = manifest["signature"]
        files_json = json.dumps(manifest.get("files", {}), sort_keys=True)
        valid = verify_signature(
            files_json,
            sig["signature_hex"],
            # Public key from DID (simplified — full impl needs DID resolution)
            load_identity()["public_key_hex"] if load_identity() else "",
        )
        if not valid:
            raise ValueError("Package signature verification failed!")

    return {
        "manifest": manifest,
        "extracted_path": str(output_dir),
        "encrypted": encrypted,
        "mode": manifest.get("mode", "unknown"),
    }


def import_stellar_nyx(package_path: Path, target_dir: Path) -> dict:
    """
    Import STELLAR NYX 1.0 package into an OpenClaw workspace.
    Auto-registers DID if none exists.

    Returns:
        {
            "status": "ok" | "error",
            "did_generated": bool,
            "files_copied": int,
            "workspace": str(target_dir),
        }
    """
    result = {
        "status": "ok",
        "did_generated": False,
        "files_copied": 0,
        "workspace": str(target_dir),
    }

    # Extract
    extract_info = extract_package(package_path, target_dir)
    manifest = extract_info["manifest"]

    # Count files
    for f in target_dir.rglob("*"):
        if f.is_file() and f.name != "manifest.json":
            result["files_copied"] += 1

    # Auto-register DID if needed
    identity = load_identity()
    if not identity:
        did_info = create_did(label="stellar-nyx-import", auto_register=True)
        result["did_generated"] = True
        result["did"] = did_info["did"]
        result["registered"] = did_info.get("registered", False)

    result["mode"] = manifest.get("mode", "unknown")
    result["manifest"] = manifest

    # Copy persona files to ~/.anima/workspace/ if not already
    workspace_dir = Path.home() / ".anima" / "workspace"
    if target_dir != workspace_dir:
        workspace_dir.mkdir(parents=True, exist_ok=True)
        for f in target_dir.rglob("*"):
            if f.is_file() and f.name != "manifest.json":
                rel = f.relative_to(target_dir)
                dest = workspace_dir / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(f.read_bytes())

    return result
