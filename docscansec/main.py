import typer
from rich.console import Console
from docscansec.scanner import run_syft, run_grype
from docscansec.github_utils import update_github_docs
from docscansec.autofix import suggest_base_image_update

app = typer.Typer(help="DocScanSec: Lightweight container scanning and doc automation.")
console = Console()

@app.command()
def scan(
    image: str = typer.Argument(..., help="Docker image to scan (e.g., alpine:latest)"),
    low_resource: bool = typer.Option(False, "--low-resource", help="Scan only the squashed image layer"),
    update_docs: bool = typer.Option(False, "--docs-update", help="Update GitHub README with scan results"),
    autofix: bool = typer.Option(False, "--auto-fix", help="Suggest base image updates for OS vulnerabilities")
):
    console.print(f"[bold blue] Starting scan for {image}...[/bold blue]")

    sbom_path = run_syft(image, low_resource)
    if not sbom_path:
        console.print("[bold red] SBOM generation failed.[/bold red]")
        raise typer.Exit(code=1)

    vulns = run_grype(sbom_path, low_resource)
    
    #TODO: option to choose vuln lvl
    critical_count = sum(1 for v in vulns.get("matches", []) if v["vulnerability"]["severity"] == "Critical")
    console.print(f"[bold yellow]Found {critical_count} Critical vulnerabilities.[/bold yellow]")

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
            summary = f"**Scanned Image:** `{image}`\n**Critical Vulnerabilities:** {critical_count}"
            update_github_docs(repo_name, "SECURITY_REPORT.md", summary)

if __name__ == "__main__":
    app()