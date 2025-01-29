from requests.exceptions import HTTPError


class OpLogger:
    def __init__(self):
        self.operations = []
        self.services = []

    def add_gn_service(self, gs_service, url: str, is_source: bool):
        gn_service = GnOpService(self, gs_service, url, is_source)
        self.services.append(gn_service)
        return gn_service

    def add_gs_service(self, gs_service, url: str, is_source: bool):
        gs_service = GsOpService(self, gs_service, url, is_source)
        self.services.append(gs_service)
        return gs_service

    def clear_services(self):
        self.services.clear()

    def log_operation(self, operation: str, url, context, service_type):
        self.operations.append(
            {
                "operation": operation,
                "url": url,
                "context": context,
                "service_type": service_type
            }
        )

    def get_operations(self):
        return self.operations

    def format_operations(self):
        return "\n".join(
            f"{op['operation']} on {op['url']} {op['context']} {op['service_type']}"
            for op in self.operations
        )


class OpService:
    def __init__(self, op_logger, service, url, is_source, is_geonetwork, dry_run=False):
        self.op_logger = op_logger
        self.service = service
        self.url = url
        self.context = "source" if is_source else "destination"
        self.service_type = "geonetwork" if is_geonetwork else "geoserver"
        self.log_operation("Init and check version")
        self.dry = dry_run

    def log_operation(self, operation):
        self.op_logger.log_operation(operation, self.url, self.context, self.service_type)


class GnOpService(OpService):
    def __init__(self, op_logger, gn_service, url, is_source, dry_run=False):
        super().__init__(op_logger, gn_service, url, is_source, True, dry_run)

    def get_record_zip(self, uuid):
        self.log_operation(f"Download zip record {uuid}")
        return self.service.get_record_zip(uuid)

    def put_record_zip(self, zipdata):
        self.log_operation(f"Upload zip record")
        if self.dry:
            return {"dry-run": True}  # skip writing in dry-run
        else:
            return self.service.put_record_zip(zipdata)


class GsOpService(OpService):
    def __init__(self, op_logger, gn_service, url, is_source, dry_run=False):
        super().__init__(op_logger, gn_service, url, is_source, False, dry_run)

    def __getattr__(self, key):
        class EmptyResponse:
            status_code = 200

            def raise_for_status(self):
                pass

        class OpClient:
            def __init__(self, rest_client, op_service):
                self.rest_client = rest_client
                self.op_service = op_service

            def get(self, path, *args, **kwargs):
                resp = self.rest_client.get(path, *args, **kwargs)
                self.op_service.log_operation(f"GET ({resp.status_code}) {path}")
                return resp

            def put(self, path, *args, **kwargs):
                if self.op_service.dry:
                    self.op_service.log_operation(f"PUT {path}")
                    # skip writing in dry-run
                    return EmptyResponse()
                else:
                    # catch the raise_for_status in geoserverclous lib
                    try:
                        resp = self.rest_client.put(path, *args, **kwargs)
                    except HTTPError as err:
                        resp = err.response
                    self.op_service.log_operation(f"PUT ({resp.status_code}) {path}")
                    return resp

            def post(self, path, *args, **kwargs):
                if self.op_service.dry:
                    self.op_service.log_operation(f"POST {path}")
                    # skip writing in dry-run
                    return EmptyResponse()
                else:
                    # catch the raise_for_status in geoserverclous lib
                    try:
                        resp = self.rest_client.post(path, *args, **kwargs)
                    except HTTPError as err:
                        resp = err.response
                    self.op_service.log_operation(f"POST ({resp.status_code}) {path}")
                    return resp

            def delete(self, path, *args, **kwargs):
                if self.op_service.dry:
                    self.op_service.log_operation(f"DELETE {path}")
                    # skip writing in dry-run
                    return EmptyResponse()
                else:
                    # catch the raise_for_status in geoserverclous lib
                    try:
                        resp = self.rest_client.delete(path, *args, **kwargs)
                    except HTTPError as err:
                        resp = err.response
                    self.op_service.log_operation(f"DELETE ({resp.status_code}) {path}")
                    return resp

        if key == "rest_client":
            return OpClient(self.service.rest_client, self)
        else:
            return self.service.__getattr__(key)
