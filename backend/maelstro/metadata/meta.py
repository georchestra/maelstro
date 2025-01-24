from io import BytesIO, StringIO
from zipfile import ZipFile
from csv import DictReader
from lxml import etree


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


class Meta:
    def __init__(self, zipfile: bytes):
        self.zipfile = zipfile
        with ZipFile(BytesIO(zipfile)) as zf:
            zip_properties = zf.read("index.csv").decode()
            dr = DictReader(StringIO(zip_properties), delimiter=";")
            self.properties = next(dr)

            self.xml_bytes = zf.read(f"{self.properties['uuid']}/metadata/metadata.xml")

        schema = self.properties.get("schema", "iso19139")
        self.namespaces = NS_REGISTRIES.get(schema)
        self.prefix = NS_PREFIXES.get(schema)

    def get_ogc_geoserver_layers(self) -> list[dict[str, str | None]]:
        xml_root = etree.parse(BytesIO(self.xml_bytes))

        return [
            self.layerproperties_from_link(link_node)
            for link_node in xml_root.findall(
                f".//{self.prefix}:CI_OnlineResource", self.namespaces
            )
            if self.is_ogc_layer(link_node)
        ]

    def is_ogc_layer(self, link_node: etree._Element) -> bool:
        link_protocol = self.protocol_from_link(link_node)
        if link_protocol is None:
            return False
        return link_protocol[:7].lower() in ["ogc:wms", "ogc:wfs", "ogc:wcs"]

    def layerproperties_from_link(
        self, link_node: etree._Element
    ) -> dict[str, str | None]:
        return {
            "server_url": self.url_from_link(link_node),
            "name": self.name_from_link(link_node),
            "description": self.desc_from_link(link_node),
            "protocol": self.protocol_from_link(link_node),
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
