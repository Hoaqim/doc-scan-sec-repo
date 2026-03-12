import re
import os

def suggest_base_image_update(dockerfile_path: str = "Dockerfile") -> str:
    if not os.path.exists(dockerfile_path):
        return "No Dockerfile found in the current directory to analyze."

    with open(dockerfile_path, "r") as f:
        content = f.read()

    # Regex to extract the image name and tag from 'FROM image:tag'
    match = re.search(r'^FROM\s+([a-zA-Z0-9_.-]+):([a-zA-Z0-9_.-]+)', content, re.MULTILINE)
    
    if not match:
        return "Could not detect a standard 'FROM image:tag' instruction in the Dockerfile."

    image_name = match.group(1)
    current_tag = match.group(2)

    #TODO: change static
    safer_tags = {
        "alpine": "3.19", 
        "ubuntu": "24.04",
        "node": "20-alpine",
        "python": "3.12-slim",
        "golang": "1.22-alpine"
    }

    if image_name in safer_tags and current_tag != safer_tags[image_name]:
        return (
            f"[bold green] Auto-fix Suggestion:[/bold green]\n"
            f"Change `FROM {image_name}:{current_tag}` to `FROM {image_name}:{safer_tags[image_name]}` "
            f"in your Dockerfile to instantly patch underlying OS vulnerabilities and reduce attack surface."
        )
    elif image_name in safer_tags and current_tag == safer_tags[image_name]:
        return f"Base image `{image_name}:{current_tag}` is already utilizing a recommended secure tag."
    else:
        return f"ℹBase image `{image_name}:{current_tag}` is not in our known auto-fix database. Manual review advised."