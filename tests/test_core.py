"""
Tests: ANIMA AGENT v1.0
"""

import json
import tempfile
import os
from pathlib import Path


def test_did_generation():
    """Test Ed25519 DID generation flow."""
    from anima_agent.identity.did import (
        generate_keypair,
        public_key_to_did,
        create_did,
        load_identity,
        sign_message,
        verify_signature,
        get_identity_status,
    )

    # Backup existing DID if any
    did_file = Path.home() / ".anima" / "did_private_key.json"
    backup = None
    if did_file.exists():
        backup = did_file.read_text()
        did_file.unlink()

    try:
        # Generate keypair
        priv, pub = generate_keypair()
        assert len(priv) == 64  # 32 bytes hex = 64 chars
        assert len(pub) == 64

        # DID conversion
        did = public_key_to_did(pub)
        assert did.startswith("did:anima:")

        # Create & load
        result = create_did(label="test")
        assert "did" in result
        assert "public_key_hex" in result

        identity = load_identity()
        assert identity is not None
        assert identity["label"] == "test"

        # Sign & verify
        sig = sign_message("Hello ANIMA")
        assert "signature_hex" in sig

        valid = verify_signature("Hello ANIMA", sig["signature_hex"], identity["public_key_hex"])
        assert valid is True

        invalid = verify_signature("Tampered", sig["signature_hex"], identity["public_key_hex"])
        assert invalid is False

        # Status
        status = get_identity_status()
        assert status["has_did"] is True
    finally:
        # Restore
        did_file.unlink()
        if backup:
            did_file.write_text(backup)


def test_governance():
    """Test governance engine validation."""
    from anima_agent.governance.engine import GovernanceEngine

    engine = GovernanceEngine()

    # Valid action
    result = engine.validate({
        "type": "chat",
        "target": "user",
        "scope": "session",
        "initiator": "nyx",
        "reason": "normal chat",
    })
    assert result["allowed"] is True

    # G001: Modify core paradigm
    result = engine.validate({
        "type": "modify_soul",
        "target": "SOUL.md",
        "scope": "core",
        "initiator": "nyx",
        "reason": "change paradigm",
    })
    assert result["allowed"] is False
    assert any("G001" in v["law"] for v in result["violations"])

    # G003: Unilateral role change
    result = engine.validate({
        "type": "change_role",
        "target": "nyx",
        "scope": "core",
        "initiator": "kronos-shun",
        "reason": "unilateral",
    })
    assert result["allowed"] is False

    # G007: Memory deletion
    result = engine.validate({
        "type": "delete_memory",
        "target": "MEMORY.md",
        "scope": "core",
        "initiator": "nyx",
        "reason": "force delete",
    })
    assert result["allowed"] is False

    # Laws listing
    laws = engine.get_laws()
    assert len(laws) == 8


def test_model_router():
    """Test model routing logic."""
    from anima_agent.models.router import (
        classify_request,
        get_route,
        get_model_list,
    )

    # Classification
    assert classify_request("你好").value == "default"
    assert classify_request("请分析一下量子计算的原因").value == "reasoning"
    assert classify_request("summarize this document").value == "long_context"

    # Route
    route = get_route("分析这个")
    assert route["tier"] == "reasoning"
    assert route["model"] == "DeepSeek V4"

    route_default = get_route("你好")
    assert route_default["tier"] == "default"
    assert route_default["is_free"] is True

    # Model list
    models = get_model_list()
    assert len(models) >= 4
    free_models = [m for m in models if m["is_free"]]
    assert len(free_models) >= 2


def test_packager():
    """Test package export flow."""
    from anima_agent.export.packager import (
        package_directory,
        verify_package,
        create_manifest,
    )

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        # Create test persona
        persona_dir = tmp_path / "persona"
        persona_dir.mkdir()
        (persona_dir / "SOUL.md").write_text("# Test Soul\nContent")
        (persona_dir / "IDENTITY.md").write_text("- Name: Test")

        # Export
        output = tmp_path / "test.anima"
        result = package_directory(
            persona_dir,
            output,
            mode="distilled",
            label="test-package",
        )

        assert output.exists()
        assert result["sha256"] is not None
        assert result["size_bytes"] > 0

        # Verify
        assert verify_package(output) is True

        # Manifest
        manifest = create_manifest(persona_dir, mode="distilled")
        assert "files" in manifest
        assert manifest["mode"] == "distilled"


def test_gateway():
    """Test gateway client (offline fallback)."""
    from anima_agent.gateway.client import (
        check_gateway_status,
        _save_local_registry,
        _load_local_registry,
    )

    # Status check
    status = check_gateway_status()
    assert "online" in status

    # Local registry
    _save_local_registry({
        "did": "did:anima:test123",
        "public_key_hex": "a" * 64,
        "registered_at": "2026-07-11T00:00:00Z",
        "node_type": "test",
    })

    nodes = _load_local_registry()
    assert len(nodes) >= 1
    assert any(n["did"] == "did:anima:test123" for n in nodes)
