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

    vulns = run_grype(sbom_path, low_resource)
    vulns_dict = {}
    vuln_details = {}

    for s_name in severity.split(","):
        matches = [v for v in vulns.get("matches", []) if v["vulnerability"]["severity"].lower() == s_name.lower()]
        if matches:
            vulns_dict[s_name] = len(matches)
            cves = list(set([m["vulnerability"]["id"] for m in matches]))
            vuln_details[s_name] = cves
            console.print(f"[bold yellow]Found {len(matches)} {s_name} vulnerabilities.[/bold yellow]")

    if autofix:
        console.print("[cyan] Analyzing for auto-fix suggestions...[/cyan]")
        suggestion = suggest_base_image_update("Dockerfile")
        console.print(suggestion)

    if update_docs:
        repo_name = os.getenv("GITHUB_REPOSITORY")
        if not repo_name:
            console.print("[bold red]Please set the GITHUB_REPOSITORY env var (e.g., 'user/repo').[/bold red]")
        else:
            md_lines = [f"**Scanned Image:** `{image}`\n", "### Vulnerability Summary\n"]
            if not vulns_dict:
                md_lines.append("No specified vulnerabilities found!\n")
            else:
                for sev, count in vulns_dict.items():
                    md_lines.append(f"- **{sev}**: {count}")
                md_lines.append("\n### Vulnerability Details\n")
                for sev, cves in vuln_details.items():
                    display_cves = ", ".join(cves[:20])
                    if len(cves) > 20:
                        display_cves += f" ... *(and {len(cves) - 20} more)*"
                    md_lines.append(f"**{sev}**:\n`{display_cves}`\n")

                summary = "\n".join(md_lines)
                update_github_docs(repo_name, "SECURITY_REPORT.md", summary)

if __name__ == "__main__":
    app()