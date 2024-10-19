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
        logging.warning("Warning: Overlay path not set. Using current directory.")
    
    logging.debug(f"Executing git command: {' '.join(command)}")
    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        logging.debug("Command executed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing git command: {e.stderr}")
        return None

def generate_commit_description(git_status):
    changes = defaultdict(lambda: defaultdict(dict))
    eclass_changes = defaultdict(list)
    
    for line in git_status.split('\n'):
        if not line.strip():
            continue
        status, file_path = line[:2], line[3:].strip()
        
        # Ignore metadata.xml and Manifest files
        if file_path.endswith('metadata.xml') or file_path.endswith('Manifest'):
            continue
        
        ebuild_match = re.match(r'(.+)/(.+)/(.+)-(\d+[\d.]+\d+)\.ebuild$', file_path)
        if ebuild_match:
            category, package, name, version = ebuild_match.groups()
            if status.startswith('A'):
                changes['add'][category][package] = version
            elif status.startswith('M'):
                changes['up'][category][package] = version
            elif status.startswith('D'):
                changes['del'][category][package] = version
        elif file_path.endswith('.eclass'):
            eclass_name = os.path.basename(file_path)
            if status.startswith('A'):
                eclass_changes['add'].append(eclass_name)
            elif status.startswith('M'):
                eclass_changes['up'].append(eclass_name)
            elif status.startswith('D'):
                eclass_changes['del'].append(eclass_name)

    def format_packages(category, packages):
        if len(packages) == 1:
            package, version = next(iter(packages.items()))
            return f"{category}/{package}-{version}"
        else:
            sorted_packages = sorted(packages.items())
            
            if len(sorted_packages) == 2:
                pkg1, ver1 = sorted_packages[0]
                pkg2, ver2 = sorted_packages[1]
                if pkg1 in pkg2 or pkg2 in pkg1:
                    diff = pkg2.replace(pkg1, '') if len(pkg2) > len(pkg1) else pkg1.replace(pkg2, '')
                    return f"{category}/{pkg1}{{,{diff}}}-{ver1}"
            
            formatted = ", ".join(f"{pkg}-{ver}" for pkg, ver in sorted_packages)
            return f"{category}/{{{formatted}}}"

    description_parts = []
    
    for action in ['add', 'up', 'del']:
        if changes[action]:
            action_str = f"{action}(" + ", ".join(format_packages(cat, pkgs) for cat, pkgs in sorted(changes[action].items())) + ")"
            description_parts.append(action_str)
        if eclass_changes[action]:
            eclass_str = f"{action}_eclass(" + ", ".join(sorted(eclass_changes[action])) + ")"
            description_parts.append(eclass_str)
    
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
        while True:
            logging.info("Proposed commit description:")
            logging.info(commit_description)
            confirm = input("Is this description correct? (yes/no/edit): ").lower()
            if confirm == 'yes':
                break
            elif confirm == 'edit':
                commit_description = input("Enter your commit description: ")
                break
            elif confirm == 'no':
                logging.info("Commit cancelled.")
                return None
            else:
                logging.info("Invalid input. Please enter 'yes', 'no', or 'edit'.")

        user, email = get_git_user()
        result = run_git_command(['git', '-c', f'user.name={user}', '-c', f'user.email={email}', 'commit', '-m', commit_description])
        if result:
            logging.info("Changes committed successfully.")
            return result
        else:
            logging.error("Failed to commit changes.")
            return None
    else:
        logging.info("No changes to commit.")
        return None

def git_push():
    logging.debug("Pushing changes to remote")
    return run_git_command(['git', 'push'])