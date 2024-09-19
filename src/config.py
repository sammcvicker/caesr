import click
from pathlib import Path
import toml
from enum import Enum

class API(Enum):
    ANTHROPIC = {
        "name": "Anthropic", 
        "models": [
            "claude-3-5-sonnet-20240620"
        ]
    }
    OPENAI = {
        "name": "OpenAI",
        "models": [
            "gpt-3.5-turbo"
        ]
    }

class Config:
    def __init__(self):
        self.path = Path("~/.srs/config.toml").expanduser()
        self.dict = self.load_config()
        self.api = self.dict["api"]
        self.api_key = self.dict["api_key"]
        self.model = self.dict["model"]
    
    def load_config(self):
        if self.path.exists():
            with self.path.open() as f:
                dict = toml.load(f)
                required_keys = ["api", "api_key", "model"]
                if all(key in dict for key in required_keys):
                    return dict
                else:
                    click.secho(f"Configuration file {self.path} is missing required keys: {', '.join(required_keys)}", fg='red', bold=True)
                    return self.configure()
        else:
            return self.configure()
    
    def configure(self) -> dict[str, any]:
        # Make the configuration file if it doesn't exist
        if not self.path.exists():
            if click.confirm(f"Create empty {self.path}?", default=True):
                self.path.parent.mkdir(parents=True, exist_ok=True)
                self.path.touch()
        else:
            click.secho(f"srs currently supports the following APIs: {', '.join([api.value['name'] for api in API])}", fg='green', bold=True)
            api = click.prompt("API to use with srs", type=click.Choice([api.name for api in API]))
            click.secho(f"API set to {API[api].value['name']}", fg='green', bold=True)
            api_key = click.prompt(f"{API[api].name} API key", type=str)
            click.secho(f"srs currently supports the following models for {API[api].value['name']}'s API: {', '.join(API[api].value['models'])}", fg='green', bold=True)
            model = click.prompt("Model to use with srs", type=click.Choice(API[api].value['models']), default=API[api].value['models'][0])
            click.secho(f"Model set to {model}", fg='green', bold=True)
            config = {
                "api": api,
                "api_key": api_key,
                "model": model
            }
            with self.path.open('w') as f:
                toml.dump(config, f)
            click.secho(f"Configuration saved to {self.path}", fg='green', bold=True)
        
        return self.load_config()

