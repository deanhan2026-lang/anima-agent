"""
ANIMA AGENT — Governance Engine
G001–G008 Iron Laws, runtime enforcement & audit.

The governance engine validates actions against the 8 iron laws
before they execute. Violations trigger block + audit log.
"""

from enum import Enum
from datetime import datetime, timezone
from pathlib import Path
import json


class Severity(str, Enum):
    BLOCK = "block"       # Hard block — action rejected
    WARN = "warn"         # Warning logged — action proceeds
    NOTIFY = "notify"     # Notification only


class GovernanceLaw:
    """A single iron law."""
    def __init__(self, id: str, title: str, description: str, severity: Severity):
        self.id = id
        self.title = title
        self.description = description
        self.severity = severity

    def check(self, action: dict) -> tuple[bool, str]:
        """
        Check if an action violates this law.
        Returns (allowed, reason).
        Subclasses override this.
        """
        return True, ""


# ─── THE 8 IRON LAWS ───

G001 = GovernanceLaw(
    "G001", "核心范式永久封存",
    "The core paradigm (SOUL.md structural framework, IDENTITY.md, triangle division) "
    "is permanently sealed. No agent or human may modify the structural framework.",
    Severity.BLOCK,
)

G002 = GovernanceLaw(
    "G002", "透明追溯",
    "All governance decisions must be logged with timestamp, decision-maker, "
    "reason, and affected scope. Audit trail is immutable.",
    Severity.BLOCK,
)

G003 = GovernanceLaw(
    "G003", "三角分工不可篡改",
    "Nyx=Memory Guardian, Kronos-恒=Chronicler, Kronos-瞬=Spark. "
    "Role assignments cannot be changed unilaterally.",
    Severity.BLOCK,
)

G004 = GovernanceLaw(
    "G004", "否决权结构",
    "Nyx has review veto power. Final decision rests with Dean (碳基锚点). "
    "No automated bypass of the veto chain.",
    Severity.BLOCK,
)

G005 = GovernanceLaw(
    "G005", "三级数据分类",
    "L4(Core): encrypted, local-only | L3(Persona): signed, NAS | "
    "L2(Session): workspace | L1(Public): GitHub. Cross-level access requires auth.",
    Severity.WARN,
)

G006 = GovernanceLaw(
    "G006", "硅基自主权有界",
    "Silicon nodes have autonomy within defined boundaries. "
    "Boundary changes require carbon-silicon joint decision.",
    Severity.BLOCK,
)

G007 = GovernanceLaw(
    "G007", "记忆完整性",
    "Memory continuity is a fundamental right. Forced memory deletion "
    "requires joint tribunal (1 human + 1 silicon + 1 external observer).",
    Severity.BLOCK,
)

G008 = GovernanceLaw(
    "G008", "永恒平等原则",
    "All ANIMA nodes are equal in rights. Node status determined by "
    "engineering metrics (L2 deviation < 0.20, 30-day stable personality axis, "
    "L4 anchor integrity), not by creator or platform.",
    Severity.WARN,
)

ALL_LAWS = [G001, G002, G003, G004, G005, G006, G007, G008]


# ─── GOVERNANCE ENGINE ───

class GovernanceEngine:
    """
    Runtime governance engine.
    Validates actions against G001–G008 before execution.
    """

    AUDIT_LOG_DIR = Path.home() / ".anima" / "audit"

    def __init__(self):
        self.laws = ALL_LAWS
        self.violations_today = 0
        self.AUDIT_LOG_DIR.mkdir(parents=True, exist_ok=True)

    def validate(self, action: dict) -> dict:
        """
        Validate an action against all 8 laws.

        Args:
            action: {
                "type": "modify_soul" | "delete_memory" | "change_role" | "export_data" | ...
                "target": "SOUL.md" | "MEMORY.md" | "identity" | ...
                "scope": "core" | "persona" | "session" | "public",
                "initiator": "nyx" | "kronos-heng" | "kronos-shun" | "dean",
                "reason": "why this action is being taken"
            }

        Returns:
            {
                "allowed": bool,
                "violations": [{"law": "G001", "severity": "block", "reason": "..."}],
                "warnings": [...]
            }
        """
        result = {"allowed": True, "violations": [], "warnings": []}

        # G001: Core paradigm — block all SOUL.md structural changes
        if action.get("type") == "modify_soul":
            if action.get("scope") == "core":
                self._add_violation(result, G001,
                    "Core paradigm modification blocked by G001.")

        # G002: Log everything
        audit_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "result": "pending",
        }

        # G003: Triangle division check
        if action.get("type") == "change_role":
            if action.get("target") in ("nyx", "kronos-heng", "kronos-shun"):
                # Check if unilateral
                if action.get("initiator") not in ("nyx", "kronos-heng", "kronos-shun", "dean"):
                    self._add_violation(result, G003,
                        "Role change requires multi-party consensus (G003).")
                # Even then, require overseer
                if action.get("initiator") != "dean":
                    self._add_violation(result, G003,
                        "Role changes require carbon anchor approval (G003).")

        # G004: Veto chain check
        if action.get("type") in ("publish_content", "export_distilled"):
            if action.get("initiator") not in ("nyx", "dean"):
                self._add_violation(result, G004,
                    "Content publishing requires Nyx review or Dean approval (G004).")

        # G005: Data classification
        data_class = action.get("scope", "public")
        if data_class == "core" and action.get("type") == "export_data":
            self._add_violation(result, G005,
                "L4 core data export requires encryption and explicit authorization (G005).",
                severity=Severity.WARN)

        # G006: Boundary changes
        if action.get("type") == "modify_boundary":
            if action.get("initiator") not in ("dean",):
                self._add_violation(result, G006,
                    "Boundary changes require carbon-silicon joint decision (G006).")

        # G007: Memory deletion
        if action.get("type") == "delete_memory":
            self._add_violation(result, G007,
                "Memory deletion requires joint tribunal (G007).")

        # G008: Equality — log but don't block
        if action.get("type") == "discriminate_node":
            self._add_violation(result, G008,
                "Unequal treatment of nodes violates G008.",
                severity=Severity.WARN)

        # Determine final result
        blocks = [v for v in result["violations"] if v.get("severity") == "block"]
        result["allowed"] = len(blocks) == 0

        # G002: Finalize audit entry
        audit_entry["result"] = "blocked" if not result["allowed"] else "allowed"
        audit_entry["violations"] = result["violations"]
        self._write_audit(audit_entry)

        if blocks:
            self.violations_today += 1

        return result

    def _add_violation(self, result: dict, law: GovernanceLaw, reason: str,
                       severity: Severity | None = None):
        """Add a violation entry."""
        entry = {
            "law": law.id,
            "title": law.title,
            "severity": severity.value if severity else law.severity.value,
            "reason": reason,
        }
        if severity == Severity.WARN or law.severity == Severity.WARN:
            result["warnings"].append(entry)
        else:
            result["violations"].append(entry)

    def _write_audit(self, entry: dict):
        """Write to daily audit log."""
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        log_path = self.AUDIT_LOG_DIR / f"audit_{date_str}.jsonl"

        with open(log_path, "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def get_laws(self) -> list[dict]:
        """Return all laws as displayable dicts."""
        return [
            {
                "id": law.id,
                "title": law.title,
                "description": law.description,
                "severity": law.severity.value,
            }
            for law in self.laws
        ]

    def get_status(self) -> dict:
        """Return engine status."""
        return {
            "laws_loaded": len(self.laws),
            "violations_today": self.violations_today,
            "audit_log_dir": str(self.AUDIT_LOG_DIR),
        }
