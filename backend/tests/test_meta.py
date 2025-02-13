import os
from maelstro.metadata import Meta


def test_iso19139():
    with open(os.path.join(os.path.dirname(__file__), 'demo_iso19139.zip'), 'rb') as zf:
        mm = Meta(zf.read())
    assert mm.properties["schema"] == "iso19139"

    assert mm.get_ogc_geoserver_layers() == [
        {
            'server_url': 'https://public.sig.rennesmetropole.fr/geoserver/ows?service=wms&request=GetCapabilities',
            'name': 'trp_doux:reparation_velo',
            'description': 'Stations de réparation et gonflage pour vélo sur Rennes Métropole',
            'protocol': 'OGC:WMS'
        },
        {
            'server_url': 'https://public.sig.rennesmetropole.fr/geoserver/ows?service=wfs&request=GetCapabilities',
            'name': 'trp_doux:reparation_velo',
            'description': 'Stations de réparation et gonflage pour vélo sur Rennes Métropole',
            'protocol': 'OGC:WFS'
        }
    ]

    assert mm.get_title() == "Stations de réparation et gonflage pour vélo sur Rennes Métropole"


def test_iso19115():
    with open(os.path.join(os.path.dirname(__file__), 'lille_iso19115-3.zip'), 'rb') as zf:
        mm = Meta(zf.read())
    assert mm.properties["schema"] == "iso19115-3.2018"

    assert mm.get_ogc_geoserver_layers() == [
        {
            'server_url': 'https://data.lillemetropole.fr/geoserver/ows',
            'name': 'mel_espacepublic:voies_vertes_chemins',
            'description': 'mel_espacepublic:voies_vertes_chemins',
            'protocol': 'OGC:WMS'
        },
        {
            'server_url': 'https://data.lillemetropole.fr/geoserver/ows',
            'name': 'mel_espacepublic:voies_vertes_chemins',
            'description': 'mel_espacepublic:voies_vertes_chemins',
            'protocol': 'OGC:WFS'
        }
    ]

    assert mm.get_title() == "Voies Vertes MEL à horizon 2026"


def test_replace_geoserver():
    with open(os.path.join(os.path.dirname(__file__), 'demo_iso19139.zip'), 'rb') as zf:
        mm = Meta(zf.read())
    assert mm.xml_bytes.find(b"https://public.sig.rennesmetropole.fr/geoserver") >= 0
    mm.replace_geoserver_src_by_dst_urls(
        {
            "sources": ["https://public.sig.rennesmetropole.fr/geoserver"],
            "destinations": ["https://prod.sig.rennesmetropole.fr/geoserver"],
        }
    )
    assert mm.xml_bytes.find(b"https://public.sig.rennesmetropole.fr/geoserver") == -1
    assert mm.xml_bytes.find(b"https://prod.sig.rennesmetropole.fr/geoserver") >= 0


def test_xslt():
    with open(os.path.join(os.path.dirname(__file__), 'demo_iso19139.zip'), 'rb') as zf:
        mm = Meta(zf.read())
    assert mm.xml_bytes.find(b"https://public.sig.rennesmetropole.fr/geoserver") >= 0
    assert mm.xml_bytes.find("Lien de téléchargement direct (GML3 EPSG:3948)".encode()) >= 0
    mm.apply_xslt(os.path.join(os.path.dirname(__file__), "test_xslt.xsl"))
    assert mm.xml_bytes.find(b"https://prod.sig.rennesmetropole.fr/geoserver") >= 0
    assert mm.xml_bytes.find("Lien de téléchargement direct (GML3 EPSG:3948)".encode()) == -1


def test_xslt_chain():
    with open(os.path.join(os.path.dirname(__file__), 'demo_iso19139.zip'), 'rb') as zf:
        mm = Meta(zf.read())
    assert mm.xml_bytes.find(b"https://public.sig.rennesmetropole.fr/geoserver") >= 0
    assert mm.xml_bytes.find("Lien de téléchargement direct (GML3 EPSG:3948)".encode()) >= 0
    mm.apply_xslt_chain(
        [
            os.path.join(os.path.dirname(__file__), "test_xslt.xsl"),
            os.path.join(os.path.dirname(__file__), "test_xslt2.xsl"),
        ]
    )
    assert mm.xml_bytes.find(b"https://final_prod.sig.rennesmetropole.fr/geoserver") >= 0
    assert mm.xml_bytes.find("Lien de téléchargement direct (GML3 EPSG:3948)".encode()) == -1
