from io import BytesIO, StringIO
from zipfile import ZipFile
from csv import DictReader
from lxml import etree
from maelstro.common.types import GsLayer
from maelstro.common.models import LinkedLayer


NS_PREFIXES = {
    "iso19139": "gmd",
    "iso19115-3.2018": "cit",
}

NS_TITLE_PREFIXES = {
    "iso19139": "gmd",
    "iso19115-3.2018": "mri",
}

NS_REGISTRIES = {
    "iso19139": {
        "gmd": "http://www.isotc211.org/2005/gmd",
    },
    "iso19115-3.2018": {
        "mri": "http://standards.iso.org/iso/19115/-3/mri/1.0",
        "cit": "http://standards.iso.org/iso/19115/-3/cit/2.0",
    },
}


class MetaXml:
    def __init__(self, xml_bytes: bytes, schema: str = "iso19139"):
        self.xml_bytes = xml_bytes
        self.schema = schema
        self.namespaces = NS_REGISTRIES.get(schema)
        self.prefix = NS_PREFIXES.get(schema)
        self.title_prefix = NS_TITLE_PREFIXES.get(schema)

    def get_title(self) -> str:
        xml_root = etree.parse(BytesIO(self.xml_bytes))
        title_node = xml_root.find(
            f".//{self.title_prefix}:MD_DataIdentification" f"//{self.prefix}:title/",
            self.namespaces,
        )
        if title_node is not None:
            return title_node.text or ""
        return ""

    def get_ogc_geoserver_layers(self) -> list[LinkedLayer]:
        xml_root = etree.parse(BytesIO(self.xml_bytes))
        return [
            self.layerproperties_from_link(link_node)
            for link_node in xml_root.findall(
                f".//{self.prefix}:CI_OnlineResource", self.namespaces
            )
            if self.is_ogc_layer(link_node)
        ]

    def get_gs_layers(
        self, gs_servers: list[str] | None = None
    ) -> dict[str, set[GsLayer]]:
        if gs_servers is None:
            gs_servers = []
        return {
            url: set(
                self.get_gslayer_from_gn_link(l.name, l.server_url, gs_servers)
                for l in self.get_ogc_geoserver_layers()
                if url in l.server_url
            )
            for url in gs_servers
        }

    def get_gslayer_from_gn_link(
        self, layer_name: str, ows_url: str, gs_servers: list[str]
    ) -> GsLayer:
        if ":" in layer_name:
            return GsLayer(*layer_name.split(":"))
        for url in gs_servers:
            ows_url = ows_url.replace(url, "")
        return GsLayer(
            workspace_name=ows_url.lstrip("/").split("/")[0], layer_name=layer_name
        )

    def _apply_xslt(self, xslt_path: str) -> bytes:
        with open(xslt_path, encoding="utf8") as xslt_file:
            xslt = etree.parse(xslt_file)
        transform = etree.XSLT(xslt)
        xml_root = etree.parse(BytesIO(self.xml_bytes))
        return self.dump_tree_to_bytes(transform(xml_root))

    def apply_xslt(self, xslt_path: str) -> tuple[str, str]:
        pre = len(self.xml_bytes)
        self.xml_bytes = self._apply_xslt(xslt_path)
        post = len(self.xml_bytes)
        return f"Before: {pre} bytes", f"After: {post} bytes"

    def apply_xslt_chain(self, xslt_paths: list[str]) -> tuple[str, str]:
        pre = len(self.xml_bytes)
        for xslt_path in xslt_paths:
            self.xml_bytes = self._apply_xslt(xslt_path)
        post = len(self.xml_bytes)
        return f"Before: {pre} bytes", f"After: {post} bytes"

    def dump_tree_to_bytes(self, xml_root: etree._ElementTree) -> bytes:
        b_io = BytesIO()
        xml_root.write(b_io)
        b_io.seek(0)
        return b_io.read()

    def replace_geoserver_src_by_dst_urls(
        self, mapping: dict[str, list[str]]
    ) -> tuple[str, str]:
        xml_root = etree.parse(BytesIO(self.xml_bytes))
        for url_node in xml_root.findall(
            f".//{self.prefix}:CI_OnlineResource/{self.prefix}:linkage/",
            self.namespaces,
        ):
            if (url_node is None) or (url_node.text is None):
                continue
            for src in mapping["sources"]:
                for dst in mapping["destinations"]:
                    url_node.text = url_node.text.replace(src, dst)
        b_io = BytesIO()
        xml_root.write(b_io)
        b_io.seek(0)
        pre = len(self.xml_bytes)
        self.xml_bytes = b_io.read()
        post = len(self.xml_bytes)
        return f"Before: {pre} bytes", f"After: {post} bytes"

    def is_ogc_layer(self, link_node: etree._Element) -> bool:
        link_protocol = self.protocol_from_link(link_node)
        if link_protocol is None:
            return False
        return link_protocol[:7].lower() in ["ogc:wms", "ogc:wfs", "ogc:wcs"]

    def layerproperties_from_link(self, link_node: etree._Element) -> LinkedLayer:
        return LinkedLayer(
            **{
                "server_url": self.url_from_link(link_node) or "",
                "name": self.name_from_link(link_node) or "",
                "description": self.desc_from_link(link_node) or "",
                "protocol": self.protocol_from_link(link_node) or "",
            }
        )

    def url_from_link(self, link_node: etree._Element) -> str | None:
        return self.property_from_link(link_node, f"{self.prefix}:linkage")

    def name_from_link(self, link_node: etree._Element) -> str | None:
        return self.property_from_link(link_node, f"{self.prefix}:name")

    def desc_from_link(self, link_node: etree._Element) -> str | None:
        return self.property_from_link(link_node, f"{self.prefix}:description")

    def protocol_from_link(self, link_node: etree._Element) -> str | None:
        return self.property_from_link(link_node, f"{self.prefix}:protocol")

    def property_from_link(self, link_node: etree._Element, tag: str) -> str | None:
        property_node = link_node.find(tag, self.namespaces)
        if property_node is not None:
            text_node = property_node.find("./")
            if text_node is not None:
                return str(text_node.text)
        return None


class MetaZip(MetaXml):
    def __init__(self, zipfile: bytes, uuid=None):
        self.zipfile = zipfile
        with ZipFile(BytesIO(zipfile)) as zf:
            zip_properties = zf.read("index.csv").decode()
            dr = DictReader(StringIO(zip_properties), delimiter=";")
            if(uuid):
                self.properties = next(csv_line for csv_line in dr if csv_line["uuid"] == uuid)
            else:
                self.properties = next(dr)

            xml_bytes = zf.read(f"{self.properties['uuid']}/metadata/metadata.xml")

        schema = self.properties.get("schema", "iso19139")

        super().__init__(xml_bytes, schema)

    def replace_geoserver_src_by_dst_urls(
        self, mapping: dict[str, list[str]]
    ) -> tuple[str, str]:
        ret = super().replace_geoserver_src_by_dst_urls(mapping)
        self.update_zip()
        return ret

    def apply_xslt(self, xslt_path: str) -> tuple[str, str]:
        ret = super().apply_xslt(xslt_path)
        self.update_zip()
        return ret

    def apply_xslt_chain(self, xslt_paths: list[str]) -> tuple[str, str]:
        ret = super().apply_xslt_chain(xslt_paths)
        self.update_zip()
        return ret

    def update_zip(self) -> tuple[str, str]:
        new_bytes = BytesIO(b"")
        with ZipFile(BytesIO(self.zipfile), "r") as zf_src:
            # get compression type from non directory elements of zip archive
            compression = next(
                fi.compress_type for fi in zf_src.infolist() if not fi.is_dir()
            )
            md_filepath = f"{self.properties['uuid']}/metadata/metadata.xml"
            pre_info = zf_src.getinfo(md_filepath)
            with ZipFile(new_bytes, "w", compression=compression) as zf_dst:
                for file_info in zf_src.infolist():
                    if file_info.is_dir():
                        zf_dst.mkdir(file_info)
                    else:
                        file_path = file_info.filename
                        with zf_dst.open(file_path, "w") as zb:
                            if file_path == md_filepath:
                                zb.write(self.xml_bytes)
                            else:
                                zb.write(zf_src.read(file_path))
                post_info = zf_dst.getinfo(md_filepath)
        new_bytes.seek(0)
        self.zipfile = new_bytes.read()
        return str(pre_info), str(post_info)

    def get_zip(self) -> bytes:
        return self.zipfile
