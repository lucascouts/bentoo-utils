import os
import subprocess
import re
import logging
from collections import defaultdict
from overlay.git_config import get_config, get_git_user, get_overlay_path

def run_git_command(command):
    overlay_path = get_overlay_path()
    if overlay_path:
        logging.debug(f"Changing directory to: {overlay_path}")
        os.chdir(overlay_path)
    else:
        print("Warning: Overlay path not set. Using current directory.")
    
    logging.debug(f"Executing git command: {' '.join(command)}")
    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        logging.debug("Command executed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error executing git command: {e.stderr}")
        logging.error(f"Command that failed: {' '.join(command)}")
        return None

def generate_commit_description(git_status):
    changes = defaultdict(dict)
    
    def compare_versions(v1, v2):
        def normalize(v):
            return [int(x) for x in re.findall(r'\d+', v)]
        return (normalize(v1) > normalize(v2)) - (normalize(v1) < normalize(v2))

    for line in git_status.split('\n'):
        if not line.strip():
            continue
        status, file_path = line[:2], line[3:].strip()
        
        ebuild_match = re.match(r'(.+)/(.+)/(.+)-(\d+[\d.]+[\d\w-]*)\.ebuild$', file_path)
        if ebuild_match:
            category, package, name, version = ebuild_match.groups()
            full_package = f"{category}/{package}"
            if status.startswith('A'):
                changes['add'][full_package] = version
            elif status.startswith('D'):
                changes['del'][full_package] = version
            elif status.startswith('M'):
                changes['mod'][full_package] = version
            elif status.startswith('R'):
                old_path, new_path = file_path.split(' -> ')
                old_match = re.match(r'(.+)/(.+)/(.+)-(\d+[\d.]+[\d\w-]*)\.ebuild$', old_path)
                new_match = re.match(r'(.+)/(.+)/(.+)-(\d+[\d.]+[\d\w-]*)\.ebuild$', new_path)
                if old_match and new_match:
                    old_version = old_match.group(4)
                    new_version = new_match.group(4)
                    if compare_versions(new_version, old_version) > 0:
                        changes['up'][full_package] = f"{old_version} -> {new_version}"
                    else:
                        changes['down'][full_package] = f"{old_version} -> {new_version}"

    description_parts = []
    
    for action in ['add', 'del', 'mod', 'up', 'down']:
        if changes[action]:
            for pkg, ver in sorted(changes[action].items()):
                if action in ['up', 'down']:
                    action_str = f"{action}({pkg}-{ver})"
                else:
                    action_str = f"{action}({pkg}-{ver})"
                description_parts.append(action_str)
    
    return ", ".join(description_parts)

def git_add(path):
    logging.debug(f"Adding path: {path}")
    return run_git_command(['git', 'add', path])

def git_status():
    logging.debug("Getting git status")
    return run_git_command(['git', 'status', '--porcelain'])

def git_commit():
    logging.debug("Preparing to commit")
    status_output = git_status()
    if status_output:
        commit_description = generate_commit_description(status_output)
        if not commit_description:
            print("No changes detected that require a commit description.")
            print("Current status:")
            print(status_output)
            return None
        
        while True:
            print("Proposed commit description:")
            print(commit_description)
            confirm = input("Options: (y)es to confirm, (e)dit to modify, (c)ancel to abort: ").lower()
            if confirm == 'y':
                break
            elif confirm == 'e':
                commit_description = input("Enter your commit description: ")
                continue
            elif confirm == 'c':
                print("Commit cancelled.")
                return None
            else:
                print("Invalid input. Please enter 'y', 'e', or 'c'.")

        user, email = get_git_user()
        result = run_git_command(['git', '-c', f'user.name={user}', '-c', f'user.email={email}', 'commit', '-m', commit_description])
        if result:
            print(f"Changes committed successfully with description: {commit_description}")
            return result
        else:
            print("Failed to commit changes.")
            return None
    else:
        print("No changes to commit.")
        return None

def git_push():
    logging.debug("Pushing changes to remote")
    result = run_git_command(['git', 'push'])
    if result:
        print("Changes pushed successfully.")
        return result
    else:
        print("Failed to push changes or nothing to push.")
        return None