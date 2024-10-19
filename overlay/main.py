import sys
import os
import logging
from overlay.git_operations import git_add, git_status, git_commit, git_push
from overlay.git_config import get_overlay_path, get_config, BENTOO_DIR, ensure_bentoo_structure

def setup_logging():
    ensure_bentoo_structure()
    log_file = os.path.join(BENTOO_DIR, 'log', 'overlay.log')
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename=log_file,
        filemode='a'  # Append mode
    )
    
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

def main():
    setup_logging()
    
    logging.debug("Starting bentoo utility...")
    logging.debug(f"Arguments received: {sys.argv}")
    logging.debug(f"Current working directory: {os.getcwd()}")
    
    if len(sys.argv) < 4:
        logging.error("Invalid command structure. Use: bentoo overlay repo [action] [path]")
        sys.exit(1)

    if sys.argv[1] != "overlay" or sys.argv[2] != "repo":
        logging.error("Invalid command structure. Use: bentoo overlay repo [action] [path]")
        sys.exit(1)

    action = sys.argv[3]
    path = sys.argv[4] if len(sys.argv) > 4 else "."

    logging.debug("Full config: %s", get_config())
    
    overlay_path = get_overlay_path()
    if not overlay_path:
        logging.error("Error: Overlay path not configured. Please check your config.json file.")
        sys.exit(1)
    
    logging.debug(f"Using overlay path: {overlay_path}")

    if not os.path.exists(overlay_path):
        logging.error(f"Error: Configured overlay path does not exist: {overlay_path}")
        sys.exit(1)

    if action == "add":
        result = git_add(path)
        logging.info("Files added successfully.")
    elif action == "status":
        result = git_status()
        if result:
            logging.info("Changes:\n%s", result)
        else:
            logging.info("Working directory is clean.")
    elif action == "commit":
        result = git_commit()
        if result:
            logging.info("Changes committed successfully.")
        else:
            logging.info("Commit cancelled or no changes to commit.")
    elif action == "push":
        result = git_push()
        if result:
            logging.info("Changes pushed successfully.")
        else:
            logging.info("Push failed or nothing to push.")
    else:
        logging.error(f"Invalid action: {action}. Use add, status, commit, or push.")
        sys.exit(1)

if __name__ == "__main__":
    main()