from pathlib import Path
from typing import Literal, Union

import msgspec
from platformdirs import user_config_dir

from ..models import ModelType


class Settings(msgspec.Struct, rename="kebab"):
    MODEL: str = list(ModelType)[0].name
    INPUT_MODE: Union[Literal["singleline"], Literal["multiline"]] = "singleline"
    STREAM_MODE: bool = False

    @staticmethod
    def get_settings() -> "Settings":
        config_path: Path = Path(user_config_dir("duck_chat")) / "conf.toml"
        if not config_path.exists():
            s = Settings()
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, "wb") as f:
                f.write(msgspec.toml.encode(s))
            return s
        with open(config_path, "rb") as f:
            buff = f.read()
        s = msgspec.toml.decode(buff, type=Settings)
        print(s)
        return s
