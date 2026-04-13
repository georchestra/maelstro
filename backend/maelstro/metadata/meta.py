from io import BytesIO, StringIO
from zipfile import ZipFile
from csv import DictReader
from typing import cast
from maelstro.common.types import GsLayer
from maelstro.common.models import LinkedLayer

from saxonche import PySaxonProcessor, PyXdmNode  # type: ignore

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
        "gco": "http://www.isotc211.org/2005/gco",
    },
    "iso19115-3.2018": {
        "mri": "http://standards.iso.org/iso/19115/-3/mri/1.0",
        "cit": "http://standards.iso.org/iso/19115/-3/cit/2.0",
        "gco": "http://standards.iso.org/iso/19115/-3/gco/1.0",
    },
}


class MetaXml:
    def __init__(self, xml_bytes: bytes, schema: str = "iso19139"):
        self.xml_bytes = xml_bytes
        self.schema = schema
        self.namespaces = NS_REGISTRIES.get(schema, {})
        self.prefix = NS_PREFIXES.get(schema)
        self.title_prefix = NS_TITLE_PREFIXES.get(schema)

        # Initialize Saxon Processor
        self.proc = PySaxonProcessor(license=False)
        self.xpath_processor = self.proc.new_xpath_processor()
        for prefix, uri in self.namespaces.items():
            self.xpath_processor.declare_namespace(prefix, uri)

    def _get_root(self) -> PyXdmNode:
        """Parses current xml_bytes into a Saxon XdmNode."""
        return self.proc.parse_xml(xml_text=self.xml_bytes.decode("utf-8"))

    def get_title(self) -> str:
        root = self._get_root()
        self.xpath_processor.set_context(xdm_item=root)
        query = f"//{self.title_prefix}:MD_DataIdentification//{self.prefix}:title//gco:CharacterString"
        title_node = self.xpath_processor.evaluate_single(query)
        return title_node.string_value if title_node else ""

    def get_ogc_geoserver_layers(self) -> list[LinkedLayer]:
        root = self._get_root()
        self.xpath_processor.set_context(xdm_item=root)
        query = f"//{self.prefix}:CI_OnlineResource"
        nodes = self.xpath_processor.evaluate(query)

        return [
            self.layerproperties_from_link(cast(PyXdmNode, node))
            for node in nodes
            if self.is_ogc_layer(cast(PyXdmNode, node))
        ]

    def get_gs_layers(
        self, gs_servers: list[str] | None = None
    ) -> dict[str, set[GsLayer]]:
        if gs_servers is None:
            gs_servers = []
        layers = self.get_ogc_geoserver_layers()
        return {
            url: set(
                self.get_gslayer_from_gn_link(l.name, l.server_url, gs_servers)
                for l in layers
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
        xsltproc = self.proc.new_xslt30_processor()
        root = self._get_root()
        executable_xsl = xsltproc.compile_stylesheet(stylesheet_file=xslt_path)
        output = executable_xsl.transform_to_string(xdm_node=root)
        return cast(bytes, output.encode("utf-8"))

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

    def replace_geoserver_src_by_dst_urls(
        self, mapping: dict[str, list[str]]
    ) -> tuple[str, str]:
        pre = len(self.xml_bytes)

        root = self._get_root()
        self.xpath_processor.set_context(xdm_item=root)
        query = f"//{self.prefix}:CI_OnlineResource/{self.prefix}:linkage//(gco:CharacterString|gmd:URL)"
        url_nodes = self.xpath_processor.evaluate(query)

        xml_as_string = root.to_string()

        for url_node in url_nodes:
            original_url = url_node.string_value
            if not original_url:
                continue

            updated_url = original_url
            # Your exact nested loop algorithm
            for src in mapping["sources"]:
                for dst in mapping["destinations"]:
                    updated_url = updated_url.replace(src, dst)

            if updated_url != original_url:
                xml_as_string = xml_as_string.replace(original_url, updated_url)

        # 4. Update the internal state
        self.xml_bytes = xml_as_string.encode("utf-8")
        post = len(self.xml_bytes)
        return f"Before: {pre} bytes", f"After: {post} bytes"

    def is_ogc_layer(self, link_node: PyXdmNode) -> bool:
        protocol = self.protocol_from_link(link_node)
        if not protocol:
            return False
        return protocol[:7].lower() in ["ogc:wms", "ogc:wfs", "ogc:wcs"]

    def layerproperties_from_link(self, link_node: PyXdmNode) -> LinkedLayer:
        return LinkedLayer(
            **{
                "server_url": self.url_from_link(link_node) or "",
                "name": self.name_from_link(link_node) or "",
                "description": self.desc_from_link(link_node) or "",
                "protocol": self.protocol_from_link(link_node) or "",
            }
        )

    def url_from_link(self, link_node: PyXdmNode) -> str | None:
        return self.property_from_link(link_node, f"{self.prefix}:linkage")

    def name_from_link(self, link_node: PyXdmNode) -> str | None:
        return self.property_from_link(link_node, f"{self.prefix}:name")

    def desc_from_link(self, link_node: PyXdmNode) -> str | None:
        return self.property_from_link(link_node, f"{self.prefix}:description")

    def protocol_from_link(self, link_node: PyXdmNode) -> str | None:
        return self.property_from_link(link_node, f"{self.prefix}:protocol")

    def property_from_link(self, link_node: PyXdmNode, tag: str) -> str | None:
        self.xpath_processor.set_context(xdm_item=link_node)
        # In Saxon, we query relative to the link_node
        prop_node = self.xpath_processor.evaluate_single(
            f"./{tag}//gco:CharacterString | ./{tag}//gmd:URL"
        )
        return prop_node.string_value if prop_node else None

    def __del__(self) -> None:
        # Clean up Saxon C++ resources
        if hasattr(self, "proc"):
            self.proc.close()


class MetaZip(MetaXml):
    def __init__(self, zipfile: bytes):
        self.zipfile = zipfile
        with ZipFile(BytesIO(zipfile)) as zf:
            zip_properties = zf.read("index.csv").decode()
            dr = DictReader(StringIO(zip_properties), delimiter=";")
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
