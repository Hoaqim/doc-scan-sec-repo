import subprocess
import json
import os

def run_syft(image: str, low_resource: bool) -> str:
    sbom_file = "sbom.json"
    scope = "squashed" if low_resource else "all-layers"
    
    cmd = ["syft", image, "--scope", scope, "-o", f"json={sbom_file}"]
    
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return sbom_file
    except subprocess.CalledProcessError:
        return ""

def run_grype(sbom_file: str, low_resource: bool) -> dict:
    cmd = ["grype", f"sbom:{sbom_file}", "-o", "json"]
    
    if low_resource:
        os.environ["GRYPE_DB_AUTO_UPDATE"] = "false"
        
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Grype failed: {e.stderr}")
        return {"matches": []}