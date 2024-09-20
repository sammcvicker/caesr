import click
from pathlib import Path
import toml
from typing import Any, Dict
from srs.utils import styles

CONFIG_PATH = Path("~/.srs/config.toml").expanduser()
REQUIRED_KEYS: list[str] = ["api_name", "api_key", "model_name"]

SUPPORTED_MODELS: Dict[str, list[str]] = {
    "Anthropic": ["claude-3-5-sonnet-20240620"],
    "OpenAI": ["gpt-3.5-turbo"]
}
    
def load_config() -> dict[str, str]:
    # If the config file exists, load it
    if CONFIG_PATH.exists():
        with CONFIG_PATH.open() as f:
            config = toml.load(f)
            # Check that it has everything it needs
            if all(key in config for key in REQUIRED_KEYS):
                return config
            # If it doesn't, configure what's missing
            else:
                missing_keys = [key for key in REQUIRED_KEYS if key not in config]
                click.secho(f"Missing from config: {', '.join(missing_keys)}", **styles["bad"])
                return configure(config)
    # If it doesn't exist, create and configure a new one
    else:
        if click.confirm(f"Create empty {CONFIG_PATH} and configure?", default=True):
            CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            CONFIG_PATH.touch()
            return configure()

def configure(config: dict[str, str] = None) -> dict[str, Any]:

    config = config if config else {}

    # Run the user through configuration
    if "api_name" not in config:
        api_names = [key for key in SUPPORTED_MODELS.keys()]
        click.secho(f"Supported APIs: {', '.join(api_names)}", **styles["good"])
        config["api_name"] = click.prompt("API to use", type=click.Choice(api_names), default=api_names[0])

    if "api_key" not in config:
        config["api_key"] = click.prompt(f"{config["api_name"]} API key to use", type=str, hide_input=True)
    
    if "model_name" not in config:
        usable_models = SUPPORTED_MODELS[config["api_name"]]
        click.secho(f"Supported {config["api_name"]} models: {', '.join(usable_models)}", **styles["good"])
        config["model_name"] = click.prompt("Model to use", type=click.Choice(usable_models), default=usable_models[0])

    # Save the config
    with CONFIG_PATH.open('w') as f:
        toml.dump(config, f)
    click.secho(f"Config saved to {CONFIG_PATH}", **styles["good"])
    
    # Return a loaded config
    return load_config()