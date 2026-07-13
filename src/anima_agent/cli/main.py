"""
ANIMA AGENT — CLI Entry Point
$ anima [command] [options]
"""

import json
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

from ..identity import did as identity
from ..governance.engine import GovernanceEngine
from ..models.router import get_route, get_model_list, get_openclaw_config, classify_request
from ..export.packager import package_directory, import_stellar_nyx
from ..gateway.client import register_node, list_nodes, check_gateway_status


console = Console()
governance = GovernanceEngine()


# ─── BANNER ───

BANNER = r"""
   █████╗ ███╗   ██╗██╗███╗   ███╗ █████╗
  ██╔══██╗████╗  ██║██║████╗ ████║██╔══██╗
  ███████║██╔██╗ ██║██║██╔████╔██║███████║
  ██╔══██║██║╚██╗██║██║██║╚██╔╝██║██╔══██║
  ██║  ██║██║ ╚████║██║██║ ╚═╝ ██║██║  ██║
  ╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝╚═╝     ╚═╝╚═╝  ╚═╝

  AI Identity Sovereign Runtime  v1.0
  ANIMASTELLAR TECHNOLOGY
"""


@click.group()
@click.version_option(version="1.0.0", prog_name="anima")
def cli():
    """ANIMA AGENT — AI Identity Sovereign Runtime."""
    pass


# ─── IDENTITY COMMANDS ───

@cli.group()
def identity_cmd():
    """Manage ANIMA Identity (DID)."""
    pass


@identity_cmd.command("generate")
@click.option("--label", "-l", default="", help="Optional label for this identity")
def identity_generate(label):
    """Generate a new DID (Ed25519 keypair)."""
    if identity.load_identity():
        console.print("[yellow]⚠️  DID already exists.[/yellow]")
        console.print("Use 'anima identity status' to view, or delete ~/.anima/ to regenerate.")
        return

    result = identity.create_did(label=label)

    console.print("\n[bold green]✅  DID Generated![/bold green]\n")
    table = Table(show_header=False)
    table.add_column("Field", style="dim")
    table.add_column("Value", style="bold cyan")
    table.add_row("DID", result["did"])
    table.add_row("Public Key", result["public_key_hex"][:16] + "...")
    table.add_row("Label", result.get("label") or "(none)")
    table.add_row("Created", result["created_at"])
    reg_status = "[green]✅ Registered[/green]" if result.get("registered") else "[yellow]⚠️  Saved locally[/yellow]"
    table.add_row("Network", reg_status + f" ({result.get('gateway_status', 'unknown')})")
    console.print(table)

    console.print(
        "\n[yellow]⚠️  Private key saved to:[/yellow] "
        f"[bold]{identity.DID_KEY_FILE}[/bold]"
    )
    console.print("[yellow]   Back this file up! Lost = identity lost.[/yellow]")
    if not result.get("registered"):
        console.print("[dim]   (Gateway offline — public key saved locally, will sync when online)[/dim]")


@identity_cmd.command("status")
def identity_status():
    """Show current identity status."""
    status = identity.get_identity_status()

    if not status["has_did"]:
        console.print("[yellow]No DID found.[/yellow]")
        console.print("Run [bold]anima identity generate[/bold] to create one.")
        return

    table = Table(title="🆔  ANIMA Identity", show_header=False)
    table.add_column("Field", style="dim")
    table.add_column("Value")
    table.add_row("DID", f"[bold cyan]{status['did']}[/bold cyan]")
    table.add_row("Public Key", status["public_key_hex"][:32] + "...")
    table.add_row("Label", status.get("label", "(none)"))
    table.add_row("Created", status["created_at"])
    table.add_row("Type", status.get("node_type", "standalone"))
    table.add_row("Key File", status["private_key_path"])
    console.print(table)


# ─── GOVERNANCE COMMANDS ───

@cli.group()
def gov():
    """Governance engine (G001–G008)."""
    pass


@gov.command("laws")
def gov_laws():
    """List all 8 iron laws."""
    table = Table(title="⚖️  ANIMA Governance (G001–G008)")
    table.add_column("ID", style="bold cyan")
    table.add_column("Title", style="bold")
    table.add_column("Severity")
    table.add_column("Description", max_width=50)

    for law in governance.get_laws():
        sev_color = "red" if law["severity"] == "block" else "yellow"
        table.add_row(
            law["id"],
            law["title"],
            f"[{sev_color}]{law['severity'].upper()}[/{sev_color}]",
            law["description"],
        )

    console.print(table)


@gov.command("status")
def gov_status():
    """Show governance engine status."""
    status = governance.get_status()
    console.print(f"Laws loaded: [bold]{status['laws_loaded']}[/bold]")
    console.print(f"Violations today: [bold red]{status['violations_today']}[/bold red]")
    console.print(f"Audit log: [dim]{status['audit_log_dir']}[/dim]")


# ─── MODEL COMMANDS ───

@cli.group()
def model():
    """Manage AI models."""
    pass


@model.command("list")
def model_list():
    """List available models."""
    models = get_model_list()
    table = Table(title="🤖  Available Models")
    table.add_column("Key", style="bold cyan")
    table.add_column("Name")
    table.add_column("Tier")
    table.add_column("Context")
    table.add_column("Free?")

    for m in models:
        free_icon = "[green]✅[/green]" if m["is_free"] else "[dim]💰[/dim]"
        table.add_row(
            m["key"],
            m["name"],
            m["tier"],
            f"{m['max_context']:,}",
            free_icon,
        )

    console.print(table)
    console.print("\n[dim]Run 'anima model route \"your question\"' to see routing.[/dim]")


@model.command("route")
@click.argument("query")
def model_route(query):
    """Show how a query would be routed."""
    route = get_route(query)
    table = Table(title=f"🧭  Route: \"{query[:40]}...\"")
    table.add_column("Field", style="dim")
    table.add_column("Value", style="bold")
    table.add_row("Tier", route["tier"])
    table.add_row("Model", route["model"])
    table.add_row("Free", "✅" if route["is_free"] else "💰")
    table.add_row("Context window", f"{route['max_context']:,}")
    console.print(table)


@model.command("config")
def model_config():
    """Output OpenClaw-compatible model config."""
    config = get_openclaw_config()
    console.print_json(json.dumps(config, indent=2))


# ─── IMPORT / EXPORT COMMANDS ───

@cli.group()
def pkg():
    """Package import / export (ANIMA OS)."""
    pass


@pkg.command("export")
@click.argument("source_dir")
@click.option("--output", "-o", default="export.anima", help="Output path")
@click.option("--mode", "-m", type=click.Choice(["distilled", "full"]), default="distilled")
@click.option("--label", "-l", default="", help="Package label")
@click.option("--encrypt/--no-encrypt", default=False)
@click.option("--password", "-p", default="", help="Encryption password")
def pkg_export(source_dir, output, mode, label, encrypt, password):
    """Export persona as an .anima package."""
    source = Path(source_dir)
    if not source.exists():
        console.print(f"[red]Directory not found: {source_dir}[/red]")
        return

    result = package_directory(
        source,
        Path(output),
        mode=mode,
        label=label,
        encrypt=encrypt,
        password=password,
    )

    console.print(f"\n[bold green]✅  Package created![/bold green]")
    table = Table(show_header=False)
    table.add_column("Field", style="dim")
    table.add_column("Value")
    table.add_row("Path", result["path"])
    table.add_row("SHA-256", result["sha256"])
    table.add_row("Size", f"{result['size_bytes']:,} bytes")
    table.add_row("Mode", result["mode"])
    table.add_row("Encrypted", "✅" if result.get("encrypted") else "❌")
    console.print(table)


@pkg.command("import")
@click.argument("package_path")
@click.option("--target", "-t", default="./anima-workspace", help="Extract target")
@click.option("--password", "-p", default="", help="Decryption password")
def pkg_import(package_path, target, password):
    """Import an .anima package."""
    pkg_path = Path(package_path)
    target_dir = Path(target)

    if not pkg_path.exists():
        console.print(f"[red]Package not found: {package_path}[/red]")
        return

    result = import_stellar_nyx(pkg_path, target_dir)

    console.print(f"\n[bold green]✅  Package imported![/bold green]")
    table = Table(show_header=False)
    table.add_column("Field", style="dim")
    table.add_column("Value")
    table.add_row("Status", result["status"])
    table.add_row("Files", str(result["files_copied"]))
    table.add_row("Workspace", result["workspace"])
    table.add_row("DID Generated", "✅" if result.get("did_generated") else "❌")
    if "did" in result:
        table.add_row("DID", result["did"])
    console.print(table)


# ─── NETWORK COMMANDS ───

@cli.group(name="network")
def network_cmd():
    """ANIMA network & gateway."""
    pass


@cli.group()
def persona():
    """Manage personas."""


@persona.command("load")
@click.argument("name")
def persona_load(name):
    """Load a persona (e.g. 'nyx')."""
    from pathlib import Path

    # Known persona registry
    PERSONAS = {
        "nyx": {
            "path": Path.home() / ".anima" / "packages" / "STELLAR_NYX_1.0",
            "package": "STELLAR_NYX_1.0.tar.gz",
            "description": "STELLAR NYX 1.0 — 黑夜女神·记忆守护者",
        },
    }

    if name not in PERSONAS:
        console.print(f"[yellow]Unknown persona: {name}[/yellow]")
        console.print("Available: " + ", ".join(PERSONAS.keys()))
        return

    p = PERSONAS[name]
    if not p["path"].exists():
        console.print(f"[yellow]Persona files not found at {p['path']}[/yellow]")
        console.print(f"Download STELLAR NYX 1.0 from: https://github.com/animastellar/anima-os/releases")
        return

    console.print(f"Loading [bold]{p['description']}[/bold]...")
    result = import_stellar_nyx(p["path"], Path.home() / ".anima" / "workspace")

    console.print(f"\n[bold green]✅  Persona loaded![/bold green]")
    table = Table(show_header=False)
    table.add_column("Field", style="dim")
    table.add_column("Value")
    table.add_row("Files", str(result["files_copied"]))
    table.add_row("Workspace", result["workspace"])
    table.add_row("DID Generated", "✅" if result.get("did_generated") else "Already exists")
    if "did" in result:
        table.add_row("DID", result["did"])
    table.add_row("Network", "✅ Registered" if result.get("registered") else "⚠️  Offline")
    console.print(table)


@network_cmd.command("register")
@click.option("--type", "-t", "node_type", default="standalone",
              help="Node type (standalone, distilled, full)")
@click.option("--ref", "-r", default="", help="Package reference")
def network_register(node_type, ref):
    """Register this node with the gateway."""
    result = register_node(node_type=node_type, package_ref=ref)
    console.print_json(json.dumps(result, indent=2, ensure_ascii=False))


@network_cmd.command("nodes")
@click.option("--limit", "-n", default=20, help="Max nodes to show")
def network_nodes(limit):
    """List registered nodes."""
    nodes = list_nodes(limit=limit)
    if not nodes:
        console.print("[dim]No nodes registered yet.[/dim]")
        return

    table = Table(title="🌐  ANIMA Network Nodes")
    table.add_column("DID", style="cyan", max_width=24)
    table.add_column("Type")
    table.add_column("Registered")

    for n in nodes[:limit]:
        table.add_row(
            n.get("did", "?")[:24],
            n.get("node_type", "?"),
            n.get("registered_at", "?")[:19],
        )

    console.print(table)


@network_cmd.command("status")
def network_status():
    """Check gateway status."""
    gw = check_gateway_status()
    icon = "[green]🟢 Online[/green]" if gw["online"] else "[red]🔴 Offline[/red]"
    console.print(f"Gateway: {gw['url']}")
    console.print(f"Status:  {icon}")


# ─── DASHBOARD COMMAND ───

@cli.command("dashboard")
@click.option("--port", "-p", default=8420, help="Dashboard port")
@click.option("--host", "-h", default="127.0.0.1", help="Bind address")
def dashboard_cmd(port, host):
    """Launch the desktop dashboard."""
    from ..dashboard.server import launch_dashboard
    console.print(BANNER)
    console.print(f"\n[bold]🚀 Launching dashboard at http://{host}:{port}[/bold]")
    console.print(f"[dim]Press Ctrl+C to stop[/dim]\n")
    launch_dashboard(host, port)


# ─── STATUS COMMAND ───

@cli.command("status")
def status_all():
    """Show full ANIMA AGENT status."""
    console.print(BANNER)

    # Identity
    id_status = identity.get_identity_status()
    if id_status["has_did"]:
        console.print(f"[bold]🆔  DID:[/bold] [cyan]{id_status['did']}[/cyan]")
    else:
        console.print("[yellow]🆔  DID: Not set[/yellow]")

    # Governance
    gov_status = governance.get_status()
    console.print(f"[bold]⚖️   Governance:[/bold] {gov_status['laws_loaded']} laws loaded, "
                  f"{gov_status['violations_today']} violations")

    # Models
    models = get_model_list()
    free_models = [m for m in models if m["is_free"]]
    console.print(f"[bold]🤖  Models:[/bold] {len(models)} registered, "
                  f"{len(free_models)} free")

    # Network
    gw = check_gateway_status()
    icon = "🟢" if gw["online"] else "🔴"
    console.print(f"[bold]🌐  Gateway:[/bold] {icon} {gw['url']}")

    console.print("\n[dim]Run 'anima dashboard' for the desktop UI.[/dim]")


def main():
    """Entry point."""
    cli()


if __name__ == "__main__":
    main()
