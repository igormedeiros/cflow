from typing import Dict, List
import os
from core.logger import log


def load_environment_variables(required_keys: List[str]) -> Dict[str, str]:
    """
    Loads required environment variables.

    Args:
        required_keys: List of environment variable keys to load

    Returns:
        Dict[str, str]: Dictionary with loaded environment variables

    Raises:
        ValueError: If any required environment variable is missing
    """
    env_vars = {}
    missing_vars = []

    for key in required_keys:
        value = os.getenv(key)
        if value is None:
            missing_vars.append(key)
            log.error(f"Required environment variable not found: '{key}'")
        else:
            env_vars[key] = value
            if any(sensitive in key.lower() for sensitive in ['token', 'key', 'secret', 'password']):
                masked_value = value[:4] + '*' * (len(value) - 4)
                log.info(f"Loaded environment variable: {key}={masked_value}")
            else:
                log.info(f"Loaded environment variable: {key}={value}")

    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

    return env_vars