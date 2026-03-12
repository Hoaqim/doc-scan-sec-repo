import re
import os

def suggest_base_image_update(dockerfile_path: str = "Dockerfile") -> str:
    if not os.path.exists(dockerfile_path):
        return "No Dockerfile found in the current directory to analyze."

    with open(dockerfile_path, "r") as f:
        content = f.read()

    # Extract the image names and tags 'FROM image:tag' also includes multi-stage builds
    matches = list(re.finditer(r'^FROM\s+([a-zA-Z0-9_.-]+):([a-zA-Z0-9_.-]+)', content, re.MULTILINE))
    
    if not matches:
        return "Could not detect a standard 'FROM image:tag' instruction in the Dockerfile."

    #TODO: change static
    safer_tags = {
        "alpine": "3.19", 
        "ubuntu": "24.04",
        "node": "20-alpine",
        "python": "3.12-slim",
        "golang": "1.22-alpine"
    }

    for match in matches:
        image_name = match.group(1)
        current_tag = match.group(2)

        if image_name in safer_tags and current_tag != safer_tags[image_name]:
            suggestions.append(
                f"[bold green] Auto-fix Suggestion for {image_name}:[/bold green]\n"
                f"Change `FROM {image_name}:{current_tag}` to `FROM {image_name}:{safer_tags[image_name]}` "
                f"to instantly patch vulnerabilities."
            )
        elif image_name in safer_tags and current_tag == safer_tags[image_name]:
            suggestions.append(f"Base image `{image_name}:{current_tag}` is already utilizing a recommended secure tag.")
        else:
            suggestions.append(f"ℹ Base image `{image_name}:{current_tag}` is not in our known auto-fix database.")

    return "\n\n".join(suggestions)