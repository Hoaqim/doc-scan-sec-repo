import pytest
from unittest.mock import patch, MagicMock
from docscansec.github_utils import update_github_docs

@patch("docscansec.github_utils.os.getenv")
@patch("docscansec.github_utils.requests.get")
@patch("docscansec.github_utils.requests.put")
def test_update_github_docs_success(mock_put, mock_get, mock_getenv):
    
    mock_getenv.return_value = "fake_github_token"
    
    mock_get_response = MagicMock()
    mock_get_response.status_code = 200
    mock_get_response.json.return_value = {"sha": "dummy_sha_12345"}
    mock_get.return_value = mock_get_response
    
    mock_put_response = MagicMock()
    mock_put_response.status_code = 200 
    mock_put.return_value = mock_put_response
    
    result = update_github_docs("octocat/repo", "SECURITY.md", "Found 0 vulns.")
    
    assert result is True
    mock_get.assert_called_once()
    mock_put.assert_called_once()
    
    put_kwargs = mock_put.call_args[1]
    assert "json" in put_kwargs
    assert put_kwargs["json"]["sha"] == "dummy_sha_12345"
    assert "docs(security)" in put_kwargs["json"]["message"]

@patch("docscansec.github_utils.os.getenv")
def test_update_github_docs_no_token(mock_getenv):
    mock_getenv.return_value = None
    
    result = update_github_docs("octocat/repo", "SECURITY.md", "summary")
    
    assert result is False