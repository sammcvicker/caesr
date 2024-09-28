import click
from pathlib import Path
import toml
from typing import Any, Dict
from csr.styles import styles

CONFIG_PATH = Path("~/.config/csr/config.toml").expanduser()
REQUIRED_KEYS: list[str] = ["api_name", "api_key", "model_name"]

SUPPORTED_MODELS: Dict[str, list[str]] = {
    "Anthropic": ["claude-3-5-sonnet-20240620"],
    "OpenAI": ["gpt-3.5-turbo"]
}

def _ensure_exists(path: Path) -> None:
    """
    Ensure that the given path exists. If it doesn't, create the directory and the file.

    Args:
        path (Path): The path to ensure exists.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch()

def _ensure_valid_config(config: dict[str, str]) -> dict[str, str]:
    """
    Ensure that the configuration has all required keys.

    Args:
        config (dict[str, str]): The current configuration.

    Returns:
        dict[str, str]: A valid configuration with all required keys.
    """
    missing_keys = [key for key in REQUIRED_KEYS if key not in config]
    if not missing_keys:
        return config
    else:
        click.secho(f"Missing from config: {', '.join(missing_keys)}", **styles["bad"])
        return configure(config)
    
def _save_config(config: dict[str, str]) -> None:
    """
    Save the configuration to the config file.

    Args:
        config (dict[str, str]): The configuration to save.
    """
    with CONFIG_PATH.open('w') as f:
        toml.dump(config, f)
    click.secho(f"Config saved to {CONFIG_PATH}", **styles["good"])
    
def load_config() -> dict[str, str]:
    """
    Load the configuration from the config file. If it doesn't exist, create and configure a new one.

    Returns:
        dict[str, str]: The loaded or newly created configuration.
    """
    if CONFIG_PATH.exists():
        with CONFIG_PATH.open() as f:
            config = toml.load(f)
            return _ensure_valid_config(config)
    else:
        if click.confirm(f"Create empty {CONFIG_PATH} and configure?", default=True):
            _ensure_exists(CONFIG_PATH)
            return configure()

def configure(config: dict[str, str] = None, force_reconfigure: bool = False) -> dict[str, Any]:
    """
    Configure the application settings interactively.

    Args:
        config (dict[str, str], optional): An existing configuration to update. Defaults to None.
        force_reconfigure (bool, optional): Whether to force reconfiguration of all settings. Defaults to False.

    Returns:
        dict[str, Any]: The updated configuration.
    """
    config = config if config else {}

    if "api_name" not in config or force_reconfigure:
        valid_api_names = [key for key in SUPPORTED_MODELS.keys()]
        config["api_name"] = click.prompt(
            "API to use", 
            type=click.Choice(valid_api_names), 
            default=valid_api_names[0]
        )

    if "api_key" not in config or force_reconfigure:
        config["api_key"] = click.prompt(
            f"{config["api_name"]} API key to use", 
            type=str, 
            hide_input=True
        )
    
    if "model_name" not in config or force_reconfigure:
        usable_models = SUPPORTED_MODELS[config["api_name"]]
        config["model_name"] = click.prompt(
            "Model to use", 
            type=click.Choice(usable_models), 
            default=usable_models[0]
        )

    _save_config(config)
    
    return config
