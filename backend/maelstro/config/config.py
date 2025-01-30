import os
from typing import Any
import yaml
from maelstro.common.types import Credentials


class ConfigError(Exception):
    pass


EMPTY_CONFIG = {
    "sources": {
        "geonetwork_instances": [],
        "geoserver_instances": [],
    },
    "destinations": {}
}


class Config:
    def __init__(self, env_var_name: str | None = None):
        self.config = EMPTY_CONFIG
        if env_var_name is not None:
            config_path = os.environ.get(env_var_name)
            if config_path is not None:
                config_file = config_path
                with open(config_file, encoding="utf8") as cf:
                    self.config = yaml.load(cf, yaml.Loader)

        self.read_all_credentials()

    def read_all_credentials(self) -> None:
        common_credentials = substitute_single_credentials_from_env(
            self.config["sources"]
        )
        for gn_instance in self.config["sources"]["geonetwork_instances"]:
            substitute_single_credentials_from_env(gn_instance, common_credentials)

        for gs_instance in self.config["sources"]["geoserver_instances"]:
            substitute_single_credentials_from_env(gs_instance, common_credentials)

        for geor_instance in self.config["destinations"].values():
            common_credentials = substitute_single_credentials_from_env(geor_instance)

            substitute_single_credentials_from_env(
                geor_instance["geonetwork"], common_credentials
            )
            substitute_single_credentials_from_env(
                geor_instance["geoserver"], common_credentials
            )

    def get_gn_sources(self) -> list[dict[str, str]]:
        return [
            {"name": gn["name"], "url": gn["api_url"]}
            for gn in self.config["sources"]["geonetwork_instances"]
        ]

    def get_gs_sources(self) -> list[str]:
        return [gs["url"] for gs in self.config["sources"]["geoserver_instances"]]

    def get_destinations(self) -> list[dict[str, str]]:
        return [
            {
                "name": k,
                "gn_url": v["geonetwork"]["api_url"],
                "gs_url": v["geoserver"]["url"],
            }
            for k, v in self.config["destinations"].items()
        ]

    def get_access_info(
        self, is_src: bool, is_geonetwork: bool, instance_id: str
    ) -> dict[str, Any]:
        info = None
        if is_src:
            if is_geonetwork:
                infos = (
                    {
                        "auth": Credentials(gn.get("login"), gn.get("password")),
                        "url": gn["api_url"],
                    }
                    for gn in self.config["sources"]["geonetwork_instances"]
                    if gn["name"] == instance_id
                )
            else:
                infos = (
                    {
                        "auth": Credentials(gs.get("login"), gs.get("password")),
                        "url": gs["url"],
                    }
                    for gs in self.config["sources"]["geoserver_instances"]
                    if gs["url"] == instance_id
                )
            try:
                info = next(infos)
            except StopIteration as exc:
                raise ConfigError(
                    f"Key '{instance_id}' could not be found among "
                    f"configured {'geonetwork' if is_geonetwork else 'geoserver'} "
                    "source servers."
                ) from exc
        else:
            inst_type = "geonetwork" if is_geonetwork else "geoserver"
            url_key = "api_url" if is_geonetwork else "url"
            try:
                instance = next(
                    inst
                    for name, inst in self.config["destinations"].items()
                    if name == instance_id
                )[inst_type]
            except StopIteration as exc:
                raise ConfigError(
                    f"Key '{instance_id}' could not be found among "
                    f"configured {'geonetwork' if is_geonetwork else 'geoserver'} "
                    "destination servers."
                ) from exc
            info = {
                "auth": Credentials(instance.get("login"), instance.get("password")),
                "url": instance[url_key],
            }

        if (info["auth"].login is None) or (info["auth"].password is None):
            info["auth"] = None
        return info


def substitute_single_credentials_from_env(
    server_instance: dict[str, Any],
    common_credentials: Credentials = Credentials(None, None),
) -> Credentials:
    common_login, common_password = common_credentials

    if common_login is not None:
        if server_instance.get("login") is None:
            server_instance["login"] = common_login
    if common_password is not None:
        if server_instance.get("password") is None:
            server_instance["password"] = common_password

    read_value_from_env(server_instance, "login")
    read_value_from_env(server_instance, "password")

    return Credentials(server_instance.get("login"), server_instance.get("password"))


def read_value_from_env(
    server_instance: dict[str, Any], value_type: str = "password"
) -> None:
    env_var = server_instance.get(f"{value_type}_env_var")
    if env_var is not None:
        env_value = os.environ.get(env_var)
        if env_value is not None:
            server_instance[value_type] = env_value
        server_instance.pop(f"{value_type}_env_var")


config = Config(env_var_name="MAELSTRO_CONFIG")
