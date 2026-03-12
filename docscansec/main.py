import typer
import os   
from rich.console import Console
from docscansec.scanner import run_syft, run_grype
from docscansec.github_utils import update_github_docs
from docscansec.autofix import suggest_base_image_update

app = typer.Typer(help="DocScanSec: Lightweight container scanning and doc automation.")
console = Console()

@app.callback()
def main_callback():
    pass

@app.command()
def scan(
    image: str = typer.Argument(..., help="Docker image to scan (e.g., alpine:latest)"),
    low_resource: bool = typer.Option(False, "--low-resource", help="Scan only the squashed image layer"),
    update_docs: bool = typer.Option(False, "--docs-update", help="Update GitHub README with scan results"),
    autofix: bool = typer.Option(False, "--auto-fix", help="Suggest base image updates for OS vulnerabilities"),
    severity: str = typer.Option("Critical", "--severity", help="Vulnerability severity level to report (e.g., Low,Medium,High,Critical)")
):
    console.print(f"[bold blue] Starting scan for {image}...[/bold blue]")

    sbom_path = run_syft(image, low_resource)
    if not sbom_path:
        console.print("[bold red] SBOM generation failed.[/bold red]")
        raise typer.Exit(code=1)

    vulns_dict = {}
    vulns = run_grype(sbom_path, low_resource)

    for s_name in severity.split(","):
        vuln_count = sum(1 for v in vulns.get("matches", []) if v["vulnerability"]["severity"].lower() == s_name.lower())
        vulns_dict[s_name] = vuln_count
        console.print(f"[bold yellow]Found {vuln_count} {s_name.capitalize()} vulnerabilities.[/bold yellow]")

    if autofix:
        console.print("[cyan] Analyzing for auto-fix suggestions...[/cyan]")
        suggestion = suggest_base_image_update("Dockerfile")
        console.print(suggestion)

    if update_docs:
        repo_name = os.getenv("GITHUB_REPOSITORY")
        if not repo_name:
            console.print("[bold red]Please set the GITHUB_REPOSITORY env var (e.g., 'user/repo').[/bold red]")
        else:
            console.print("[cyan] Pushing updates to documentation...[/cyan]")
            summary = f"**Scanned Image:** `{image}`\n** Vulnerabilities:** {vulns_dict}"
            update_github_docs(repo_name, "SECURITY_REPORT.md", summary)

if __name__ == "__main__":
    app()