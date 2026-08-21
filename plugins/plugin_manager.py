import importlib.util
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PLUGINS_DIR = PROJECT_ROOT / "plugins"
DATA_DIR = PROJECT_ROOT / "data"
PLUGIN_CONFIG_FILE = DATA_DIR / "plugins.json"


def _load_config():
    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not PLUGIN_CONFIG_FILE.exists():
        return {
            "disabled_plugins": [],
        }

    try:
        with PLUGIN_CONFIG_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError

        data.setdefault(
            "disabled_plugins",
            [],
        )

        return data

    except (
        json.JSONDecodeError,
        OSError,
        ValueError,
    ):
        return {
            "disabled_plugins": [],
        }


def _save_config(data):
    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with PLUGIN_CONFIG_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            data,
            file,
            indent=4,
        )


def discover_plugins():
    PLUGINS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    plugins = []

    for file_path in PLUGINS_DIR.glob("*.py"):
        if file_path.name in [
            "__init__.py",
            "plugin_manager.py",
        ]:
            continue

        plugins.append(
            file_path.stem
        )

    return sorted(plugins)


def is_plugin_enabled(plugin_name):
    config = _load_config()

    disabled = config.get(
        "disabled_plugins",
        [],
    )

    return plugin_name not in disabled


def enable_plugin(plugin_name):
    config = _load_config()

    disabled = config.get(
        "disabled_plugins",
        [],
    )

    if plugin_name in disabled:
        disabled.remove(plugin_name)

    config["disabled_plugins"] = disabled

    try:
        _save_config(config)
        return (
            f"Plugin '{plugin_name}' enabled."
        )

    except OSError as error:
        return (
            f"Could not enable plugin: {error}"
        )


def disable_plugin(plugin_name):
    config = _load_config()

    disabled = config.get(
        "disabled_plugins",
        [],
    )

    if plugin_name not in disabled:
        disabled.append(plugin_name)

    config["disabled_plugins"] = disabled

    try:
        _save_config(config)
        return (
            f"Plugin '{plugin_name}' disabled."
        )

    except OSError as error:
        return (
            f"Could not disable plugin: {error}"
        )


def load_plugin(plugin_name):
    if not is_plugin_enabled(
        plugin_name
    ):
        return {
            "success": False,
            "error": (
                f"Plugin '{plugin_name}' "
                f"is disabled."
            ),
        }

    plugin_path = (
        PLUGINS_DIR
        / f"{plugin_name}.py"
    )

    if not plugin_path.exists():
        return {
            "success": False,
            "error": (
                f"Plugin '{plugin_name}' "
                f"was not found."
            ),
        }

    try:
        spec = (
            importlib.util
            .spec_from_file_location(
                plugin_name,
                plugin_path,
            )
        )

        if (
            spec is None
            or spec.loader is None
        ):
            return {
                "success": False,
                "error": (
                    f"Could not load plugin "
                    f"'{plugin_name}'."
                ),
            }

        module = (
            importlib.util
            .module_from_spec(spec)
        )

        spec.loader.exec_module(
            module
        )

        return {
            "success": True,
            "module": module,
        }

    except Exception as error:
        return {
            "success": False,
            "error": (
                f"Plugin load error: "
                f"{error}"
            ),
        }


def get_plugin_status():
    plugins = discover_plugins()

    if not plugins:
        return "No plugins installed."

    lines = []

    for number, plugin in enumerate(
        plugins,
        start=1,
    ):
        status = (
            "Enabled"
            if is_plugin_enabled(plugin)
            else "Disabled"
        )

        lines.append(
            f"{number}. {plugin} "
            f"- {status}"
        )

    return "\n".join(lines)


if __name__ == "__main__":
    print(
        get_plugin_status()
    )