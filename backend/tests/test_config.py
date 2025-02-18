import os
import pytest
from maelstro.config import Config, ConfigError
from maelstro.common.types import Credentials, DbConfig


os.environ["CONFIG_PATH"] = os.path.join(os.path.dirname(__file__), "test_config.yaml")
os.environ["DB_CONFIG_PATH"] = os.path.join(os.path.dirname(__file__), "test_db_config.yaml")
os.environ["XSLT_CONFIG_PATH"] = os.path.join(os.path.dirname(__file__), "test_xslst_config.yaml")


def test_init():
    conf = Config("CONFIG_PATH")
    assert conf.config == {
        "sources": {
            "geonetwork_instances": [
                {
                    "name": "GeonetworkMaster",
                    "api_url": "https://demo.georchestra.org/geonetwork/srv/api",
                    'password': '${DEMO_CRD}',
                    'login': '${DEMO_CRD}',
                },
                {
                    "name": "GeonetworkRennes",
                    "api_url": "https://public.sig.rennesmetropole.fr/geonetwork/srv/api",
                }
            ],
            "geoserver_instances": [
                {
                    "url": "https://mastergs.rennesmetropole.fr/geoserver/",
                    "login": "test",
                    "password": "1234"
                },
                {
                    "url": "https://mastergs.rennesmetropole.fr/geoserver-geofence/",
                    "login": "toto6",
                    "password": "Str0ng_passW0rd"
                },
                {
                    "url": "https://data.lillemetropole.fr/geoserver/"
                },
            ]
        },
        "destinations": {
            "CompoLocale": {
                "geonetwork": {
                    "api_url": "https://georchestra-127-0-0-1.nip.io/geonetwork/srv/api",
                    "login": "testadmin",
                    "password": "testadmin",
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


def test_subst_env():
    os.environ["DEMO_CRD"] = "demo"
    os.environ["LOCAL_LOGIN"] = "test"
    conf = Config("CONFIG_PATH")
    conf.config["sources"]["geonetwork_instances"][0]["login"] == "demo"
    conf.config["sources"]["geonetwork_instances"][0]["password"] == "demo"
    conf.config["destinations"]["CompoLocale"]["geonetwork"]["login"] == "test"
    conf.config["destinations"]["CompoLocale"]["geonetwork"]["password"] == "test"


def test_subst_env_db():
    os.environ["PGHOST"] = "database"
    os.environ["PGPORT"] = "5432"
    os.environ["PGDATABASE"] = "log"
    os.environ["PGUSER"] = "user"
    os.environ["PGPASSWORD"] = "pass"

    conf = Config("DB_CONFIG_PATH")
    assert conf.has_db_logging()
    assert conf.get_db_config() == DbConfig('database', '5432', 'user', 'pass', 'log', 'maelstro', 'logs')


def test_get_info():
    os.environ.pop("DEMO_CRD")
    os.environ["DEMO_CRD"] = "demo"
    conf = Config("CONFIG_PATH")
    assert conf.get_access_info(True, True, "GeonetworkMaster") == {
        "auth": Credentials("demo", "demo"),
        "url": "https://demo.georchestra.org/geonetwork/srv/api",
    }
    assert conf.get_access_info(True, False, "https://mastergs.rennesmetropole.fr/geoserver-geofence/") == {
        "auth": Credentials("toto6", "Str0ng_passW0rd"),
        "url": "https://mastergs.rennesmetropole.fr/geoserver-geofence/",
    }
    assert conf.get_access_info(False, True, "PlateformeProfessionnelle") == {
        "auth": Credentials("toto", "passW0rd"),
        "url": "https://portail.sig.rennesmetropole.fr/geonetwork/srv/api",
    }
    assert conf.get_access_info(False, False, "CompoLocale") == {
        "auth": None,
        "url": "https://georchestra-127-0-0-1.nip.io/geoserver",
    }
    with pytest.raises(ConfigError) as err:
        conf.get_access_info(False, False, "MissingKey")


def test_xslts():
    conf = Config("XSLT_CONFIG_PATH")
    assert set(conf.get_all_transformation_pairs().keys()) == {
        'GeonetworkMaster -> PlateformeProfessionnelle',
        'GeonetworkMaster -> PlateformePublique',
        'GeonetworkMaster -> CompoLocale',
        'GeonetworkRennes -> PlateformePublique',
        'GeonetworkRennes -> CompoLocale'
    }
    assert len(conf.get_transformation_pair("GeonetworkMaster", "CompoLocale")) == 2
    assert len(conf.get_transformation_pair("GeonetworkRennes", "CompoLocale")) == 1
    assert len(conf.get_transformation_pair("GeonetworkRennes", "PlateformeProfessionelle")) == 0
    assert [
        el["xsl_path"]
        for el in conf.get_transformation_pair("GeonetworkMaster", "CompoLocale")
    ] == ["./tests/test_public_to_prod.xsl", "./tests/test_xslt_prod_to_final_prod.xsl"]
    assert [
        el["xsl_path"]
        for el in conf.get_transformation_pair("GeonetworkRennes", "PlateformePublique")
    ] == ["./tests/test_xslt_prod_to_final_prod.xsl", "./tests/test_public_to_prod.xsl"]


def test_doc_sample():
    os.environ["SAMPLE_PATH"] = os.path.join(os.path.dirname(__file__), "doc_sample_config.yaml")
    os.environ["PASSWORD_B"] = "pwB"
    conf = Config("SAMPLE_PATH")
    assert conf.config == {
        "sources": {
            "login": "admin", 'password': '${COMMON_PW}',
            "geonetwork_instances": [
                {"name": "a", "login": "admin", "password": "pwA"},
                {"name": "b", "login": "B", "password": "pwB"},
                {"name": "c", "login": "C", 'password': '${COMMON_PW}'},
            ],
            "geoserver_instances": [],
        },
        "destinations": {},
    }
