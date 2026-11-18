from maelstro.common.types import DbConfig
from maelstro.logging.psql_logger import build_url


def test_build_url_uses_installed_psycopg2_driver():
    config = DbConfig(
        host="database",
        port=5432,
        login="user",
        password="password",
        database="maelstro",
    )

    assert build_url(config) == (
        "postgresql+psycopg2://user:password@database:5432/maelstro"
    )
