from datetime import datetime
from typing import Any
from fastapi import Request
from sqlalchemy import (
    Engine,
    Column,
    Table,
    Integer,
    String,
    Boolean,
    DateTime,
    create_engine,
    MetaData,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from pydantic import TypeAdapter
from maelstro.config import app_config as config


Base = declarative_base()


DB_CONFIG = {
    "host": "database",
    "port": 5432,
    "login": "georchestra",
    "password": "georchestra",
    "database": "georchestra",
    "schema": "maelstro",
    "table": "logs",
}
DB_CONFIG.update(config.config.get("db_logging", {}))

SCHEMA = str(DB_CONFIG.get("schema"))
DB_URL = (
    f"postgresql://{DB_CONFIG['login']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:"
    f"{DB_CONFIG['port']}/{DB_CONFIG['database']}"
)


class Log(Base):  # type: ignore
    __tablename__ = "logs"
    __table_args__ = {"schema": SCHEMA}

    id = Column(Integer, primary_key=True, autoincrement=True)
    start_time = Column(DateTime, nullable=False, default=datetime.now())
    end_time = Column(DateTime, nullable=False, default=datetime.now())
    first_name = Column(String, nullable=False, default="")
    last_name = Column(String, nullable=False, default="")
    status_code = Column(Integer, nullable=False, default=200)
    dataset_uuid = Column(String, nullable=False, default="")
    src_name = Column(String, nullable=False, default="")
    dst_name = Column(String, nullable=False, default="")
    src_title = Column(String, nullable=False, default="")
    dst_title = Column(String, nullable=False, default="")
    # src_link = Column(String, nullable=False, default="")
    # dst_link = Column(String, nullable=False, default="")
    copy_meta = Column(Boolean, nullable=False, default=False)
    copy_layers = Column(Boolean, nullable=False, default=False)
    copy_styles = Column(Boolean, nullable=False, default=False)
    details = Column(JSONB, nullable=True)

    def to_dict(self, get_details=False) -> dict[str, Any]:  # type: ignore
        return {
            field.name: getattr(self, field.name)
            for field in self.__table__.c
            if get_details or field.name != "details"
        }


def to_bool(param: str | None) -> bool:
    return TypeAdapter(bool).validate_python(param)


def log_request_to_db(
    status_code: int,
    request: Request,
    properties: dict[str, Any],
    operations: list[dict[str, Any]],
) -> None:
    record = {
        "start_time": properties.get("start_time"),
        "end_time": datetime.now(),
        "first_name": request.headers.get("sec-firstname"),
        "last_name": request.headers.get("sec-lastname"),
        "status_code": status_code,
        "dataset_uuid": request.query_params.get("metadataUuid"),
        "src_name": request.query_params.get("src_name"),
        "dst_name": request.query_params.get("dst_name"),
        "src_title": properties.get("src_title"),
        "dst_title": properties.get("dst_title"),
        "copy_meta": to_bool(request.query_params.get("copy_meta")),
        "copy_layers": to_bool(request.query_params.get("copy_layers")),
        "copy_styles": to_bool(request.query_params.get("copy_styles")),
        "details": operations,
    }
    log_to_db(record)


def get_logs(size: int, offset: int, get_details: bool = False) -> list[dict[str, Any]]:
    with Session(get_engine()) as session:
        return [
            row.to_dict(get_details)
            for row in session.query(Log)
            .order_by(Log.id.desc())
            .offset(offset)
            .limit(size)
        ]


def format_log(row: Log) -> str:
    user = f"{row.first_name} {row.last_name}"
    status = "<succes>" if row.status_code == 200 else "<echec> "
    operations = (
        (["metadata"] if row.copy_meta else [])
        + (["couches"] if row.copy_layers else [])
        + (["styles"] if row.copy_styles else [])
    )
    source = f'{row.src_name}:{row.dataset_uuid} - "{row.src_title}"'
    destination = (
        f'{row.dst_name} - "{row.dst_title}" ({", ".join(operations)})'
        if operations
        else "n/a (copy_meta=false, copy_layers=false, copy_styles=false)"
    )
    return f"[{row.start_time}]: {status} {user} copie {source} vers {destination}"


def format_logs(size: int, offset: int) -> list[str]:
    with Session(get_engine()) as session:
        return [
            format_log(row)
            for row in session.query(Log)
            .order_by(Log.id.desc())
            .offset(offset)
            .limit(size)
        ]


def log_to_db(record: dict[str, Any]) -> None:
    with Session(get_engine()) as session:
        session.add(Log(**record))
        session.commit()


def get_engine() -> Engine:
    return create_engine(DB_URL)


def read_db_table(name: str = "logs") -> Table:
    engine = get_engine()
    return Table("logs", MetaData(schema=SCHEMA), autoload_with=engine)


def create_db_table() -> None:
    engine = get_engine()
    Base.metadata.create_all(engine)
