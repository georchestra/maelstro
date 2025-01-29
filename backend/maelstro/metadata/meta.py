from io import BytesIO, StringIO
from zipfile import ZipFile
from csv import DictReader
from lxml import etree
from maelstro.common.types import GsLayer


NS_PREFIXES = {
    "iso19139": "gmd",
    "iso19115-3.2018": "cit",
}

NS_REGISTRIES = {
    "iso19139": {
        "gmd": "http://www.isotc211.org/2005/gmd",
    },
    "iso19115-3.2018": {
        "cit": "http://standards.iso.org/iso/19115/-3/cit/2.0",
    },
}


class MetaXml:
    def __init__(self, xml_bytes: bytes, schema: str = "iso19139"):
        self.xml_bytes = xml_bytes
        self.namespaces = NS_REGISTRIES.get(schema)
        self.prefix = NS_PREFIXES.get(schema)

    def get_ogc_geoserver_layers(self) -> list[dict[str, str]]:
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
                self.get_gslayer_from_gn_link(l["name"], l["server_url"], gs_servers)
                for l in self.get_ogc_geoserver_layers()
                if url in l["server_url"]
            )
            for url in gs_servers
        }

    def get_gslayer_from_gn_link(
        self, layer_name: str, ows_url: str, gs_servers: list[str]
    ) -> GsLayer:
        if not layer_name:
            layer_name = "GAM:plan_b3_psc_02_captage_pct"
        if ":" in layer_name:
            return GsLayer(*layer_name.split(":"))
        for url in gs_servers:
            ows_url = ows_url.replace(url, "")
        return GsLayer(
            workspace_name=ows_url.lstrip("/").split("/")[0], layer_name=layer_name
        )

    def update_geoverver_urls(self, mapping: dict[str, list[str]]) -> None:
        xml_root = etree.parse(BytesIO(self.xml_bytes))
        for link_node in xml_root.findall(
            f".//{self.prefix}:CI_OnlineResource", self.namespaces
        ):
            if link_node is not None:
                url_node = link_node.find(f".//{self.prefix}:linkage", self.namespaces)
                if url_node is not None:
                    text_node = url_node.find("./")
                    for src in mapping["sources"]:
                        for dst in mapping["destinations"]:
                            if text_node is not None:
                                if text_node.text is not None:
                                    text_node.text = text_node.text.replace(src, dst)
        b_io = BytesIO()
        xml_root.write(b_io)
        b_io.seek(0)
        self.xml_bytes = b_io.read()

    def is_ogc_layer(self, link_node: etree._Element) -> bool:
        link_protocol = self.protocol_from_link(link_node)
        if link_protocol is None:
            return False
        return link_protocol[:7].lower() in ["ogc:wms", "ogc:wfs", "ogc:wcs"]

    def layerproperties_from_link(self, link_node: etree._Element) -> dict[str, str]:
        return {
            "server_url": self.url_from_link(link_node) or "",
            "name": self.name_from_link(link_node) or "",
            "description": self.desc_from_link(link_node) or "",
            "protocol": self.protocol_from_link(link_node) or "",
        }

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
    def __init__(self, zipfile: bytes):
        self.zipfile = zipfile
        with ZipFile(BytesIO(zipfile)) as zf:
            zip_properties = zf.read("index.csv").decode()
            dr = DictReader(StringIO(zip_properties), delimiter=";")
            self.properties = next(dr)

            xml_bytes = zf.read(f"{self.properties['uuid']}/metadata/metadata.xml")

        schema = self.properties.get("schema", "iso19139")

        super().__init__(xml_bytes, schema)
