# backend.py
import xml.etree.ElementTree as ET
from xml.dom import minidom

VALID_COUNTRIES = [
    "IT", "FR", "DE", "ES", "PT", "GB", "US", "NL", "BE", "CH", # ...
    # Aggiungere l'elenco completo secondo le specifiche
]

VALID_REGIMI_FISCALI = [
    "RF01", "RF02", "RF04", "RF05", "RF06", "RF07", "RF08", "RF09",
    "RF10", "RF11", "RF12", "RF13", "RF14", "RF15", "RF16", "RF17", "RF18", "RF19"
]

VALID_FORMATI_TRASMISSIONE = ["FPR12", "FPA12"]

VALID_TIPI_DOCUMENTO = ["TD01", "TD02", "TD24", "TD25"]

VALID_MODALITA_PAGAMENTO = ["MP01", "MP02", "MP05", "MP12"]


def validate_param(value, valid_values, field_name):
    if value not in valid_values:
        raise ValueError(f"{field_name} non valido. Valori ammessi: {', '.join(valid_values)}")
    return value


def parse_access_xml(content):
    root = ET.fromstring(content)
    dati = root.find("Fattura")
    return {
        "Numero": dati.find("FatturaNum").text,
        "Data": dati.find("Data").text[:10],
        "Cliente": dati.find("Cliente").text,
        "Causale": dati.find("Note").text,
        "ImportoTotale": "0.00"  # Placeholder
    }


def crea_fattura_elettronica(dati_access, params):
    ns_uri = "http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2"
    ET.register_namespace("p", ns_uri)

    root = ET.Element("{p}FatturaElettronica".format(p=ns_uri), {
        "versione": params["FormatoTrasmissione"],
        "xmlns:ds": "http://www.w3.org/2000/09/xmldsig#",
        "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "xsi:schemaLocation": f"{ns_uri} http://www.fatturapa.gov.it/export/fatturazione/sdi/fatturapa/v1.2/Schema_del_file_xml_FatturaPA_versione_1.2.xsd"
    })

    header = ET.SubElement(root, "FatturaElettronicaHeader")
    trasm = ET.SubElement(header, "DatiTrasmissione")
    id_trasm = ET.SubElement(trasm, "IdTrasmittente")
    ET.SubElement(id_trasm, "IdPaese").text = validate_param(params["IdPaeseMittente"], VALID_COUNTRIES, "IdPaese")
    ET.SubElement(id_trasm, "IdCodice").text = params["IdCodiceMittente"]
    ET.SubElement(trasm, "ProgressivoInvio").text = params["ProgressivoInvio"]
    ET.SubElement(trasm, "FormatoTrasmissione").text = validate_param(params["FormatoTrasmissione"], VALID_FORMATI_TRASMISSIONE, "FormatoTrasmissione")
    ET.SubElement(trasm, "CodiceDestinatario").text = params["CodiceDestinatario"]

    cedente = ET.SubElement(header, "CedentePrestatore")
    dati_anag = ET.SubElement(cedente, "DatiAnagrafici")
    id_iva = ET.SubElement(dati_anag, "IdFiscaleIVA")
    ET.SubElement(id_iva, "IdPaese").text = validate_param(params["IdPaeseMittente"], VALID_COUNTRIES, "IdPaese")
    ET.SubElement(id_iva, "IdCodice").text = params["IdCodiceMittente"]
    ET.SubElement(dati_anag, "CodiceFiscale").text = params["CodiceFiscaleMittente"]
    anagrafica = ET.SubElement(dati_anag, "Anagrafica")
    ET.SubElement(anagrafica, "Denominazione").text = params["DenominazioneMittente"]
    ET.SubElement(dati_anag, "RegimeFiscale").text = validate_param(params["RegimeFiscale"], VALID_REGIMI_FISCALI, "RegimeFiscale")

    sede = ET.SubElement(cedente, "Sede")
    ET.SubElement(sede, "Indirizzo").text = params["IndirizzoMittente"]
    ET.SubElement(sede, "CAP").text = params["CAPMittente"]
    ET.SubElement(sede, "Comune").text = params["ComuneMittente"]
    ET.SubElement(sede, "Provincia").text = params["ProvinciaMittente"]
    ET.SubElement(sede, "Nazione").text = validate_param(params["NazioneMittente"], VALID_COUNTRIES, "Nazione")

    body = ET.SubElement(root, "FatturaElettronicaBody")
    dati_gen = ET.SubElement(body, "DatiGenerali")
    dati_doc = ET.SubElement(dati_gen, "DatiGeneraliDocumento")
    ET.SubElement(dati_doc, "TipoDocumento").text = validate_param(params.get("TipoDocumento", "TD01"), VALID_TIPI_DOCUMENTO, "TipoDocumento")
    ET.SubElement(dati_doc, "Divisa").text = "EUR"
    ET.SubElement(dati_doc, "Data").text = dati_access["Data"]
    ET.SubElement(dati_doc, "Numero").text = dati_access["Numero"]
    ET.SubElement(dati_doc, "ImportoTotaleDocumento").text = dati_access["ImportoTotale"]
    ET.SubElement(dati_doc, "Causale").text = dati_access["Causale"]

    return minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
