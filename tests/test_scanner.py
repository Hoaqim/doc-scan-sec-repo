import pytest
import json
import subprocess
from unittest.mock import patch
from docscansec.scanner import run_syft, run_grype

@patch("docscansec.scanner.subprocess.run")
def test_run_syft_success(mock_subprocess):
    mock_subprocess.return_value = None 
    
    result = run_syft("alpine:latest", low_resource=True)
    
    mock_subprocess.assert_called_once()
    assert "squashed" in mock_subprocess.call_args[0][0]
    assert result == "sbom.json"

@patch("docscansec.scanner.subprocess.run")
def test_run_syft_failure(mock_subprocess):
    mock_subprocess.side_effect = subprocess.CalledProcessError(1, "syft")
    
    result = run_syft("broken-image:tag", low_resource=False)
    
    assert result == ""



@patch("docscansec.scanner.subprocess.run")
def test_run_grype_success(mock_subprocess):
    mock_output = {
        "matches": [
            {"vulnerability": {"id": "CVE-2026-1234", "severity": "Critical"}}
        ]
    }
    
    class DummyResult:
        stdout = json.dumps(mock_output)
        
    mock_subprocess.return_value = DummyResult()
    
    result = run_grype("fake_sbom.json", low_resource=True)
    
    assert "matches" in result
    assert result["matches"][0]["vulnerability"]["severity"] == "Critical"