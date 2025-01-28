import os
import pytest
from maelstro.config import Config, ConfigError


@pytest.fixture
def test_config_path():
    return os.path.join(os.path.dirname(__file__), "test_config.yaml")


def test_init(test_config_path):
    conf = Config(test_config_path)
    assert conf.config == {
        "sources": {
            "geonetwork_instances": [
                {
                    "name": "GeonetworkMaster",
                    "api_url": "https://demo.georchestra.org/geonetwork/srv/api",
                }
            ],
            "geoserver_instances": [
                {
                    "url": "https://mastergs.rennesmetropole.fr/geoserver/",
                    "login": "test",
                    "password": 1234
                },
                {
                    "url": "https://mastergs.rennesmetropole.fr/geoserver-geofence/",
                    "login": "toto6",
                    "password": "Str0ng_passW0rd"
                }
            ]
        },
        "destinations": {
            "CompoLocale": {
                "geonetwork": {
                    "api_url": "http://geonetwork:8080/geonetwork/srv/api",
                },
                "geoserver": {
                    "url": "https://georchestra-127-0-0-1.nip.io/geoserver"
                }
            },
            "PlateformeProfessionnelle": {
                "login": "toto",
                "password": "passW0rd",
                "geoserver": {
                    "url": "https://portail.sig.rennesmetropole.fr/geoserver",
                    "login": "toto",
                    "password": "overridePW"
                },
                "geonetwork": {
                    "api_url": "https://portail.sig.rennesmetropole.fr/geonetwork/srv/api",
                    "login": "toto",
                    "password": "passW0rd"
                }
            },
            "PlateformePublique": {
                "geoserver": {
                    "url": "https://public.sig.rennesmetropole.fr/geoserver",
                    "login": "toto2",
                    "password": "Str0ng_passW0rd"
                },
                "geonetwork": {
                    "api_url": "https://public.sig.rennesmetropole.fr/geonetwork/srv/api",
                    "login": "toto3",
                    "password": "Str0ng_passW0rd"
                }
            }
        }
    }


def test_subst_env(test_config_path):
    os.environ["DEMO_LOGIN"] = "demo"
    os.environ["LOCAL_LOGIN"] = "test"
    conf = Config(test_config_path)
    conf.config["sources"]["geonetwork_instances"][0]["login"] == "demo"
    conf.config["sources"]["geonetwork_instances"][0]["password"] == "demo"
    conf.config["destinations"]["CompoLocale"]["geonetwork"]["login"] == "test"
    conf.config["destinations"]["CompoLocale"]["geonetwork"]["password"] == "test"


def test_get_info(test_config_path):
    os.environ.pop("DEMO_LOGIN")
    os.environ["DEMO_LOGIN"] = "demo"
    conf = Config(test_config_path)
    assert conf.get_access_info(True, True, "GeonetworkMaster") == {
        "auth": ("demo", "demo"),
        "url": "https://demo.georchestra.org/geonetwork/srv/api",
    }
    assert conf.get_access_info(True, False, "https://mastergs.rennesmetropole.fr/geoserver-geofence/") == {
        "auth": ("toto6", "Str0ng_passW0rd"),
        "url": "https://mastergs.rennesmetropole.fr/geoserver-geofence/",
    }
    assert conf.get_access_info(False, True, "PlateformeProfessionnelle") == {
        "auth": ("toto", "passW0rd"),
        "url": "https://portail.sig.rennesmetropole.fr/geonetwork/srv/api",
    }
    assert conf.get_access_info(False, False, "CompoLocale") == {
        "auth": None,
        "url": "https://georchestra-127-0-0-1.nip.io/geoserver",
    }
    with pytest.raises(ConfigError) as err:
        conf.get_access_info(False, False, "MissingKey")


def test_doc_sample():
    os.environ["PASSWORD_B"] = "pwB"
    conf = Config(os.path.join(os.path.dirname(__file__), "doc_sample_config.yaml"))
    assert conf.config == {
        "sources": {
            "login": "admin",
            "geonetwork_instances": [
                {"name": "a", "login": "admin", "password": "pwA"},
                {"name": "b", "login": "B", "password": "pwB"},
                {"name": "c", "login": "C"},
            ]
        },
        "destinations": {},
    }
