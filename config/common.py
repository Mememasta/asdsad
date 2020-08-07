import pytoml as toml

from pathlib import Path


class BaseConfig:

    debug = True
    app_name = 'Crowdsourcing'
    secret_key = b'TyzLMReLCWUiPsTFMActw_0dtEU7kAcFXHNYYm64DNI='

    PROJECT_ROOT = Path(__file__).parent.parent
    static_dir = str(PROJECT_ROOT / 'static')

    def load_config(path = None):
        if path != None:
            path = Path(__file__).parent.parent / path
        else:
            path = Path(__file__).parent.parent / 'config/user_config.toml'

        with open(path) as f:
            conf = toml.load(f)

        return conf
