from datetime import datetime
from sqlalchemy import Column, Table, Integer, String, Boolean, DateTime, create_engine, MetaData
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

SCHEMA = DB_CONFIG["schema"]
DB_URL = (
    f"postgresql://{DB_CONFIG['login']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:"
    f"{DB_CONFIG['port']}/{DB_CONFIG['database']}"
)


class Log(Base):
    __tablename__ = 'logs'
    __table_args__ = {'schema': SCHEMA}

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

    def to_dict(self, get_details=False):
        return {
            field.name: getattr(self, field.name)
            for field in self.__table__.c
            if get_details or field.name != "details"
        }


def to_bool(param: str) -> bool:
    return TypeAdapter(bool).validate_python(param)


def log_request_to_db(status_code, request, log_handler):
    record = {
        "start_time": log_handler.properties.get("start_time"),
        "end_time": datetime.now(),
        "first_name": request.headers.get("sec-firstname"),
        "last_name": request.headers.get("sec-lastname"),
        "status_code": status_code,
        "dataset_uuid": request.query_params.get("metadataUuid"),
        "src_name": request.query_params.get("src_name"),
        "dst_name": request.query_params.get("dst_name"),
        "src_title": log_handler.properties.get("src_title"),
        "dst_title": log_handler.properties.get("dst_title"),
        "copy_meta": to_bool(request.query_params.get("copy_meta")),
        "copy_layers": to_bool(request.query_params.get("copy_layers")),
        "copy_styles": to_bool(request.query_params.get("copy_styles")),
        "details": log_handler.get_json_responses(),
    }
    log_to_db(record)


def get_logs(size, offset, get_details=False):
    with Session(get_engine()) as session:
        return [
            row.to_dict(get_details)
            for row in session.query(Log).order_by(Log.id.desc()).offset(offset).limit(size)
        ]


def format_logs(size, offset):
    with Session(get_engine()) as session:
        def row_to_copy_operations(row: Log):
            return ", ".join(
                (["metadata"] if row.copy_meta else [])
                + (["couches"] if row.copy_layers else [])
                + (["styles"] if row.copy_styles else [])
            )
        return [
            (
                f"[{row.start_time}]: "
                f"<{'succes' if row.status_code == 200 else 'echec '}> "
                f"{row.first_name} {row.last_name} "
                f'copie {row.src_name} - "{row.src_title}" '
                f'vers {row.dst_name} - "{row.dst_title}" '
                f"({row_to_copy_operations(row)})"
            )
            for row in session.query(Log).order_by(Log.id.desc()).offset(offset).limit(size)
        ]


def log_to_db(record):
    with Session(get_engine()) as session:
        session.add(Log(**record))
        session.commit()


def get_engine():
    return create_engine(DB_URL)


def read_db_table(name="logs"):
    engine = get_engine()
    return Table("logs", MetaData(schema=SCHEMA), autoload_with=engine)


def create_db_table():
    engine = get_engine()
    Base.metadata.create_all(engine)
