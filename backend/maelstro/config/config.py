import os
import re
import yaml
from typing import Any
from maelstro.common.types import Credentials, DbConfig


class ConfigError(Exception):
    pass


EMPTY_CONFIG: dict[str, Any] = {
    "sources": {
        "geonetwork_instances": [],
        "geoserver_instances": [],
    },
    "destinations": {},
}
REGEX_ENV_VAR = r"^\${(.*)}$"


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
        db_config = self.config.get("db_logging")
        if db_config is not None:
            substitute_single_credentials_from_env(db_config)

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

    def has_db_logging(self) -> bool:
        return "db_logging" in self.config

    def get_db_config(self) -> DbConfig:
        return DbConfig(**self.config.get("db_logging", {}))

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
    current_login = server_instance.get("login")
    server_instance["login"] = check_for_env(current_login)
    current_password = server_instance.get("password")
    server_instance["password"] = check_for_env(current_password)

    # en support for db
    current_host = check_for_env(server_instance.get("host"))
    if current_host is not None:
        server_instance["host"] = current_host
    current_port = check_for_env(server_instance.get("port"))
    if current_port is not None:
        server_instance["port"] = current_port
    current_login = check_for_env(server_instance.get("login"))
    if current_login is not None:
        server_instance["login"] = current_login
    current_database = check_for_env(server_instance.get("database"))
    if current_database is not None:
        server_instance["database"] = current_database
    current_schema = check_for_env(server_instance.get("schema"))
    if current_schema is not None:
        server_instance["schema"] = current_schema

    if common_login is not None:
        if server_instance.get("login") is None:
            server_instance["login"] = common_login
    if common_password is not None:
        if server_instance.get("password") is None:
            server_instance["password"] = common_password
    print(server_instance)
    return Credentials(server_instance.get("login"), server_instance.get("password"))


def check_for_env(current_to_test: str | Any | None) -> str | None:
    if current_to_test is not None:
        current_env = re.match(REGEX_ENV_VAR, current_to_test)
        if current_env:
            if os.environ.get(current_env.group(1)):
                return os.environ.get(current_env.group(1))
    return current_to_test


config = Config(env_var_name="MAELSTRO_CONFIG")
