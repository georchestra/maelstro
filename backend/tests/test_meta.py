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


def test_replace_geoserver():
    with open(os.path.join(os.path.dirname(__file__), 'demo_iso19139.zip'), 'rb') as zf:
        mm = Meta(zf.read())
    assert mm.xml_bytes.find(b"https://public.sig.rennesmetropole.fr/geoserver") >= 0
    mm.update_geoverver_urls(
        {
            "sources": ["https://public.sig.rennesmetropole.fr/geoserver"],
            "destinations": ["https://prod.sig.rennesmetropole.fr/geoserver"],
        }
    )
    assert mm.xml_bytes.find(b"https://public.sig.rennesmetropole.fr/geoserver") == -1
    assert mm.xml_bytes.find(b"https://prod.sig.rennesmetropole.fr/geoserver") >= 0
