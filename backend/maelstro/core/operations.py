from typing import Any, IO, Callable
from requests import Response
from requests.exceptions import HTTPError
from geonetwork import GnApi, GnSession
from geoservercloud.services import RestService  # type: ignore


class OpLogger:
    def __init__(self) -> None:
        self.operations: list[dict[str, str]] = []
        self.services: list[OpService | GnApi] = []

    def add_gn_service(self, gn_service: GnApi, url: str, is_source: bool) -> GnApi:
        op_service = OpService(self, url, is_source, True)
        gn_service.session = GnSessionWrapper(
            op_service, gn_service.session, url
        )  # type: ignore
        self.services.append(gn_service)
        return gn_service

    def add_gs_service(
        self, gs_service: RestService, url: str, is_source: bool
    ) -> "GsOpService":
        service = GsOpService(self, gs_service, url, is_source)
        self.services.append(service)
        return service

    def clear_services(self) -> None:
        self.services.clear()

    def log_operation(
        self, operation: str, url: str, context: str, service_type: str
    ) -> None:
        self.operations.append(
            {
                "operation": operation,
                "url": url,
                "context": context,
                "service_type": service_type,
            }
        )

    def get_operations(self) -> list[Any]:
        return self.operations

    def format_operations(self) -> str:
        return "\n".join(
            f"{op['operation']} on {op['url']} {op['context']} {op['service_type']}"
            for op in self.operations
        )


class OpService:
    def __init__(
        self,
        op_logger: OpLogger,
        url: str,
        is_source: bool,
        is_geonetwork: bool,
        dry_run: bool = False,
    ):
        self.op_logger = op_logger
        self.url = url
        self.context = "source" if is_source else "destination"
        self.service_type = "geonetwork" if is_geonetwork else "geoserver"
        self.log_operation("Init and check version")
        self.dry = dry_run

    def log_operation(self, operation: str) -> None:
        # print(operation, self.url, self.context, self.service_type)
        self.op_logger.log_operation(
            operation, self.url, self.context, self.service_type
        )


class GnOpService(OpService):
    def __init__(
        self,
        op_logger: OpLogger,
        gn_service: GnApi,
        url: str,
        is_source: bool,
        dry_run: bool = False,
    ):
        self.service = gn_service
        super().__init__(op_logger, url, is_source, True, dry_run)

    def get_record_zip(self, uuid: str) -> IO[bytes]:
        self.log_operation(f"Download zip record {uuid}")
        return self.service.get_record_zip(uuid)

    def put_record_zip(self, zipdata: IO[bytes]) -> Any:
        self.log_operation("Upload zip record")
        if self.dry:
            return {"dry-run": True}  # skip writing in dry-run
        else:
            return self.service.put_record_zip(zipdata)


class GnSessionWrapper:
    def __init__(self, op_service: OpService, rest_client: GnSession, url: str):
        self.rest_client = rest_client
        self.op_service = op_service
        self.url = url
        self._request = rest_client.request

    def __getattribute__(self, key: str) -> Any:
        if key in ["get", "put", "post", "delete"]:

            def create_request_wrapper(method: str) -> Callable[..., Any]:
                def request_wrapper(path: str, *args: Any, **kwargs: Any) -> Any:
                    rest_client = object.__getattribute__(self, "rest_client")
                    resp = rest_client.__getattribute__(method).__call__(
                        path, *args, **kwargs
                    )
                    op_service = object.__getattribute__(self, "op_service")
                    url = object.__getattribute__(self, "url")
                    op_service.log_operation(
                        f"{method} ({resp.status_code}) {path.replace(url, '')}"
                    )
                    return resp

                return request_wrapper

            return create_request_wrapper(key)
        return object.__getattribute__(self, "rest_client").__getattribute__(key)


class GsOpService(OpService):
    def __init__(
        self,
        op_logger: OpLogger,
        gs_service: Any,
        url: str,
        is_source: bool,
        dry_run: bool = False,
    ):
        self.service = gs_service
        super().__init__(op_logger, url, is_source, False, dry_run)

    def __getattr__(self, key: str) -> Any:
        class EmptyResponse(Response):
            status_code = 200

            def raise_for_status(self) -> None:
                pass

        class OpClient:
            def __init__(self, rest_client: Any, op_service: OpService):
                self.rest_client = rest_client
                self.op_service = op_service

            def get(self, path: str, *args: Any, **kwargs: Any) -> Response:
                resp: Response = self.rest_client.get(path, *args, **kwargs)
                self.op_service.log_operation(f"GET ({resp.status_code}) {path}")
                return resp

            def put(self, path: str, *args: Any, **kwargs: Any) -> Response:
                if self.op_service.dry:
                    self.op_service.log_operation(f"PUT {path}")
                    # skip writing in dry-run
                    return EmptyResponse()
                else:
                    # catch the raise_for_status in geoserverclous lib
                    try:
                        resp: Response = self.rest_client.put(path, *args, **kwargs)
                    except HTTPError as err:
                        resp = err.response
                    self.op_service.log_operation(f"PUT ({resp.status_code}) {path}")
                    return resp

            def post(self, path: str, *args: Any, **kwargs: Any) -> Response:
                if self.op_service.dry:
                    self.op_service.log_operation(f"POST {path}")
                    # skip writing in dry-run
                    return EmptyResponse()
                else:
                    # catch the raise_for_status in geoserverclous lib
                    try:
                        resp: Response = self.rest_client.post(path, *args, **kwargs)
                    except HTTPError as err:
                        resp = err.response
                    self.op_service.log_operation(f"POST ({resp.status_code}) {path}")
                    return resp

            def delete(self, path: str, *args: Any, **kwargs: Any) -> Response:
                if self.op_service.dry:
                    self.op_service.log_operation(f"DELETE {path}")
                    # skip writing in dry-run
                    return EmptyResponse()
                else:
                    # catch the raise_for_status in geoserverclous lib
                    try:
                        resp: Response = self.rest_client.delete(path, *args, **kwargs)
                    except HTTPError as err:
                        resp = err.response
                    self.op_service.log_operation(f"DELETE ({resp.status_code}) {path}")
                    return resp

        if key == "rest_client":
            return OpClient(self.service.rest_client, self)
        else:
            return self.service.__getattr__(key)
