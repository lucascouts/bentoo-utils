import os
import json
import logging
import configparser

BENTOO_DIR = os.path.expanduser('~/.bentoo')
CONFIG_PATH = os.path.join(BENTOO_DIR, 'config.json')
GITCONFIG_PATH = os.path.expanduser('~/.gitconfig')

def ensure_bentoo_structure():
    if not os.path.exists(BENTOO_DIR):
        os.makedirs(BENTOO_DIR)
    log_dir = os.path.join(BENTOO_DIR, 'log')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'w') as f:
            json.dump({}, f)

def get_config():
    ensure_bentoo_structure()
    logging.debug(f"Looking for config file at: {CONFIG_PATH}")
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r') as f:
                config = json.load(f)
                logging.debug("Config file loaded successfully")
                return config
        except json.JSONDecodeError as e:
            logging.error(f"Error parsing config.json: {e}")
    return {}

def get_overlay_path():
    config = get_config()
    overlay_path = config.get('overlay', {}).get('local', '')
    if not overlay_path:
        logging.error("Overlay path not found in config. Config contents:")
        logging.error(json.dumps(config, indent=2))
    else:
        logging.debug(f"Overlay path found: {overlay_path}")
    return overlay_path

def get_git_user():
    if os.path.exists(GITCONFIG_PATH):
        config = configparser.ConfigParser()
        config.read(GITCONFIG_PATH)
        if 'user' in config:
            user = config['user'].get('name')
            email = config['user'].get('email')
            logging.debug(f"Git user found in .gitconfig: user={user}, email={email}")
            return user, email
    
    bentoo_config = get_config()
    repo_config = bentoo_config.get('overlay', {}).get('repo', {})
    user = repo_config.get('user')
    email = repo_config.get('email')
    logging.debug(f"Git user configuration from bentoo config: user={user}, email={email}")
    return user, email

def set_git_user(user, email):
    if not os.path.exists(GITCONFIG_PATH):
        config = get_config()
        config.setdefault('overlay', {}).setdefault('repo', {})['user'] = user
        config.setdefault('overlay', {}).setdefault('repo', {})['email'] = email
        
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=2)
        logging.info(f"Updated bentoo config with user: {user}, email: {email}")
    else:
        config = configparser.ConfigParser()
        config.read(GITCONFIG_PATH)
        if 'user' not in config:
            config['user'] = {}
        config['user']['name'] = user
        config['user']['email'] = email
        with open(GITCONFIG_PATH, 'w') as f:
            config.write(f)
        logging.info(f"Updated .gitconfig with user: {user}, email: {email}")
    
    logging.info(f"Git user set to: {user} <{email}>")