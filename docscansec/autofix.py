import re
import os
import requests

def get_latest_tag_from_dockerhub(image_name: str) -> str | None:
    url = f"https://hub.docker.com/v2/repositories/library/{image_name}/tags/?page_size=20&ordering=last_updated"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return None
            
        data = response.json()
        for tag_info in data.get("results", []):
            tag = tag_info.get("name")
            
            if tag and tag != "latest" and not any(x in tag.lower() for x in ["rc", "beta", "alpha", "edge"]):
                return tag
                
        return None
    except requests.RequestException:
        return None


def suggest_base_image_update(dockerfile_path: str = "Dockerfile") -> str:
    if not os.path.exists(dockerfile_path):
        return "No Dockerfile found in the current directory to analyze."

    with open(dockerfile_path, "r") as f:
        content = f.read()

    # Extract the image names and tags 'FROM image:tag' also includes multi-stage builds
    matches = list(re.finditer(r'^FROM\s+([a-zA-Z0-9_.-]+)(?::([a-zA-Z0-9_.-]+))?', content, re.MULTILINE))    
    if not matches:
        return "Could not detect a standard 'FROM image:tag' instruction in the Dockerfile."

    suggestions = []
    
    for match in matches:
        image_name = match.group(1)
        current_tag = match.group(2) or "latest"

        latest_tag = get_latest_tag_from_dockerhub(image_name)

        if latest_tag and current_tag != latest_tag:
            suggestions.append(
                f"[bold green] Auto-fix Suggestion for {image_name}:[/bold green]\n"
                f"Consider changing `FROM {image_name}:{current_tag}` to `FROM {image_name}:{latest_tag}` "
                f"(most recently updated stable tag on Docker Hub)."
            )
        elif latest_tag and current_tag == latest_tag:
            suggestions.append(f"Base image `{image_name}:{current_tag}` seems to be up-to-date with Docker Hub.")
        else:
            suggestions.append(f"ℹ Could not fetch dynamic tags for `{image_name}` (it might not be an official library image or network error).")

    return "\n\n".join(suggestions)