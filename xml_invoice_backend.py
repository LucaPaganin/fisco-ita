# backend.py
import xml.etree.ElementTree as ET
from xml.dom import minidom

# Valid countries according to NazioneType in the XSD schema
VALID_COUNTRIES = [
    "IT", "FR", "DE", "ES", "PT", "GB", "US", "NL", "BE", "CH", "AT", "DK", 
    "FI", "GR", "IE", "LU", "NO", "SE", "PL", "RO", "RU", "BR", "CA", "CN", 
    "JP", "IN", "AU", "NZ", "MX", "ZA", "AR", "IL", "CH", "TR"
    # Pattern: [A-Z]{2} - Any two uppercase letters
]

# Valid regime fiscale types according to RegimeFiscaleType in the XSD schema
VALID_REGIMI_FISCALI = [
    "RF01", # Regime ordinario
    "RF02", # Regime dei contribuenti minimi
    "RF04", # Agricoltura e attività connesse e pesca
    "RF05", # Vendita sali e tabacchi
    "RF06", # Commercio dei fiammiferi
    "RF07", # Editoria
    "RF08", # Gestione di servizi di telefonia pubblica
    "RF09", # Rivendita di documenti di trasporto pubblico e di sosta
    "RF10", # Intrattenimenti, giochi e altre attività
    "RF11", # Agenzie di viaggi e turismo
    "RF12", # Agriturismo
    "RF13", # Vendite a domicilio
    "RF14", # Rivendita di beni usati, di oggetti d'arte
    "RF15", # Agenzie di vendite all'asta di oggetti d'arte
    "RF16", # IVA per cassa P.A.
    "RF17", # IVA per cassa
    "RF18", # Altro
    "RF19"  # Regime forfettario
]

# Valid formati trasmissione according to FormatoTrasmissioneType in the XSD schema
VALID_FORMATI_TRASMISSIONE = ["FPR12", "FPA12"]

# Valid tipi documento according to TipoDocumentoType in the XSD schema
VALID_TIPI_DOCUMENTO = [
    "TD01", # Fattura
    "TD02", # Acconto / anticipo su fattura
    "TD03", # Acconto / anticipo su parcella
    "TD04", # Nota di credito
    "TD05", # Nota di debito
    "TD06", # Parcella
    "TD16", # Integrazione fattura reverse charge interno
    "TD17", # Integrazione/autofattura per acquisto servizi dall'estero
    "TD18", # Integrazione per acquisto di beni intracomunitari
    "TD19", # Integrazione/autofattura per acquisto di beni ex art.17 c.2 DPR 633/72
    "TD20", # Autofattura per regolarizzazione e integrazione delle fatture
    "TD21", # Autofattura per splafonamento
    "TD22", # Estrazione beni da Deposito IVA
    "TD23", # Estrazione beni da Deposito IVA con versamento dell'IVA
    "TD24", # Fattura differita di cui all'art.21, comma 4, lett. a)
    "TD25", # Fattura differita di cui all'art.21, comma 4, terzo periodo lett. b)
    "TD26", # Cessione di beni ammortizzabili e per passaggi interni
    "TD27"  # Fattura per autoconsumo o per cessioni gratuite senza rivalsa
]

# Valid modalita pagamento according to the XSD schema
VALID_MODALITA_PAGAMENTO = [
    "MP01", # Contanti
    "MP02", # Assegno
    "MP03", # Assegno circolare
    "MP04", # Contanti presso Tesoreria
    "MP05", # Bonifico
    "MP06", # Vaglia cambiario
    "MP07", # Bollettino bancario
    "MP08", # Carta di pagamento
    "MP09", # RID
    "MP10", # RID utenze
    "MP11", # RID veloce
    "MP12", # RIBA
    "MP13", # MAV
    "MP14", # Quietanza erario
    "MP15", # Giroconto su conti di contabilità speciale
    "MP16", # Domiciliazione bancaria
    "MP17", # Domiciliazione postale
    "MP18", # Bollettino di c/c postale
    "MP19", # SEPA Direct Debit
    "MP20", # SEPA Direct Debit CORE
    "MP21", # SEPA Direct Debit B2B
    "MP22", # Trattenuta su somme già riscosse
    "MP23"  # PagoPA
]

# XML Schema namespace
XML_SCHEMA_NAMESPACE = "http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2"


def validate_param(value, valid_values, field_name):
    if value not in valid_values:
        raise ValueError(f"{field_name} non valido. Valori ammessi: {', '.join(valid_values)}")
    return value


def parse_cliente_field(cliente_text):
    """Estrae le informazioni del destinatario dal campo Cliente.
    
    Args:
        cliente_text (str): Il testo del campo Cliente, formato come:
            "NOME - PI- PARTITA_IVA - CF - CODICE_FISCALE - INDIRIZZO - COMUNE - CAP - PROVINCIA"
    
    Returns:
        dict: Un dizionario con le informazioni estratte
    """
    info = {}
    if not cliente_text:
        return info
    
    # Sostituisci le apostrofi codificate
    cliente_text = cliente_text.replace("&apos;", "'")
    
    # Prova a estrarre le parti dalla stringa
    parts = [part.strip() for part in cliente_text.split("-")]
    
    # Estrai le informazioni in base al formato atteso
    if len(parts) >= 1:
        info["Denominazione"] = parts[0].strip()
    
    for i, part in enumerate(parts):
        part = part.strip()
        if i > 0 and i < len(parts) - 1:
            if "PI" in part:
                # Il prossimo elemento dovrebbe essere la partita IVA
                if i + 1 < len(parts):
                    info["PartitaIVA"] = parts[i + 1].strip()
            elif "CF" in part:
                # Il prossimo elemento dovrebbe essere il codice fiscale
                if i + 1 < len(parts):
                    info["CodiceFiscale"] = parts[i + 1].strip()
    
    # Estrai indirizzo, città, CAP e provincia
    # Sono solitamente gli ultimi elementi
    if len(parts) >= 4:
        info["Indirizzo"] = parts[-4].strip() if len(parts) >= 4 else ""
        info["Comune"] = parts[-3].strip() if len(parts) >= 3 else ""
        cap_provincia = parts[-2].strip() if len(parts) >= 2 else ""
        info["CAP"] = cap_provincia.split("-")[0].strip() if "-" in cap_provincia else cap_provincia
        info["Provincia"] = parts[-1].strip() if len(parts) >= 1 else ""
    
    return info


def parse_access_xml(content):
    try:
        # Handle both bytes and string input
        if isinstance(content, bytes):
            try:
                # Try UTF-8 first
                content_str = content.decode('utf-8')
            except UnicodeDecodeError:
                # Fall back to latin-1 or other encodings if UTF-8 fails
                content_str = content.decode('latin-1')
        else:
            content_str = content
            
        # Fix common XML special characters that might be incorrectly escaped
        content_str = content_str.replace("&apos;", "'")
        
        # Parse the XML
        root = ET.fromstring(content_str)
        dati = root.find("Fattura")
        
        if dati is None:
            raise ValueError("Tag 'Fattura' non trovato nel file XML. Verifica che il file sia nel formato corretto.")
        
        # Extract date in correct format (YYYY-MM-DD)
        data_elem = dati.find("Data")
        if data_elem is None:
            data_formatted = ""
        else:
            data_text = data_elem.text
            data_formatted = data_text[:10] if data_text else ""
        
        # Extract causale from Note field
        note_elem = dati.find("Note")
        causale = note_elem.text if note_elem is not None and note_elem.text else ""
        
        # Extract other fields with error handling
        fattura_num_elem = dati.find("FatturaNum")
        numero = fattura_num_elem.text if fattura_num_elem is not None and fattura_num_elem.text else ""
        
        cliente_elem = dati.find("Cliente")
        cliente = cliente_elem.text if cliente_elem is not None and cliente_elem.text else ""
        
        # Extract IVA information
        iva_elem = dati.find("Iva")
        iva = iva_elem.text if iva_elem is not None and iva_elem.text else "0"
        
        # Extract Note IVA
        note_iva_elem = dati.find("NoteIva")
        note_iva = note_iva_elem.text if note_iva_elem is not None and note_iva_elem.text else ""
        
        # Extract Modo Pagamento
        modo_pag_elem = dati.find("ModoPag")
        modo_pagamento = modo_pag_elem.text if modo_pag_elem is not None and modo_pag_elem.text else ""
        
        # Extract Tempo Pagamento
        tempo_pag_elem = dati.find("TempoPag")
        tempo_pagamento = tempo_pag_elem.text if tempo_pag_elem is not None and tempo_pag_elem.text else ""
        
        # Extract Scadenza
        scad_elem = dati.find("Scad")
        scadenza = scad_elem.text[:10] if scad_elem is not None and scad_elem.text else ""
        
        # Extract Sconto
        sconto_elem = dati.find("Sconto")
        sconto = sconto_elem.text if sconto_elem is not None and sconto_elem.text else "0"
        
        # Parse cliente field to extract destinatario information
        destinatario_info = parse_cliente_field(cliente) if cliente else {}
        
        return {
            "Numero": numero,
            "Data": data_formatted,
            "Cliente": cliente,
            "Causale": causale,
            "ImportoTotale": "0.00",  # Placeholder
            "IVA": iva,
            "NoteIVA": note_iva,
            "ModoPagamento": modo_pagamento,
            "TempoPagamento": tempo_pagamento,
            "Scadenza": scadenza,
            "Sconto": sconto,
            "Destinatario": destinatario_info
        }
    except Exception as e:
        # Add detailed error information
        error_msg = f"Errore nel parsing XML: {str(e)}"
        print(error_msg)
        raise ValueError(error_msg)


def crea_fattura_elettronica(dati_access, params):
    """
    Crea un file XML per la fattura elettronica conforme allo schema XSD.
    
    Args:
        dati_access: Dizionario con i dati della fattura estratti dal file XML di Access
        params: Dizionario con i parametri di configurazione
        
    Returns:
        String: XML formattato della fattura elettronica
    """
    # Namespace URLs
    ns_uri = XML_SCHEMA_NAMESPACE
    
    # Register namespaces - this ensures proper prefixes are used
    ET.register_namespace("p", ns_uri)  # Register with prefix "p" for compatibility
    ET.register_namespace("ds", "http://www.w3.org/2000/09/xmldsig#")
    ET.register_namespace("xsi", "http://www.w3.org/2001/XMLSchema-instance")
    
    # Determine schema location - use local file if specified
    use_local_schema = params.get("UseLocalSchema", False)
    if use_local_schema:
        # Use local schema file
        schema_location = f"{ns_uri} Schema_VFPR12.xsd"
    else:
        # Use online schema
        schema_location = f"{ns_uri} http://www.fatturapa.gov.it/export/fatturazione/sdi/fatturapa/v1.2/Schema_del_file_xml_FatturaPA_versione_1.2.xsd"
    
    # Create the root element with proper namespace formatting using prefix "p"
    # Non includiamo xmlns:p poiché è già registrato con ET.register_namespace
    root = ET.Element("{" + ns_uri + "}FatturaElettronica", {
        "versione": validate_param(params["FormatoTrasmissione"], VALID_FORMATI_TRASMISSIONE, "FormatoTrasmissione"),
        "xmlns:ds": "http://www.w3.org/2000/09/xmldsig#",
        "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "xsi:schemaLocation": schema_location
    })

    # HEADER
    header = ET.SubElement(root, "FatturaElettronicaHeader")
    
    # 1. Dati Trasmissione
    trasm = ET.SubElement(header, "DatiTrasmissione")
    id_trasm = ET.SubElement(trasm, "IdTrasmittente")
    ET.SubElement(id_trasm, "IdPaese").text = validate_param(params["IdPaeseMittente"], VALID_COUNTRIES, "IdPaese")
    ET.SubElement(id_trasm, "IdCodice").text = params["IdCodiceMittente"]
    ET.SubElement(trasm, "ProgressivoInvio").text = params["ProgressivoInvio"]
    ET.SubElement(trasm, "FormatoTrasmissione").text = validate_param(params["FormatoTrasmissione"], VALID_FORMATI_TRASMISSIONE, "FormatoTrasmissione")
    ET.SubElement(trasm, "CodiceDestinatario").text = params["CodiceDestinatario"]
    
    # Contatti Trasmittente (opzionali)
    contatti_trasm = ET.SubElement(trasm, "ContattiTrasmittente")
    if "TelefonoTrasmittente" in params and params["TelefonoTrasmittente"]:
        ET.SubElement(contatti_trasm, "Telefono").text = params["TelefonoTrasmittente"]
    if "EmailTrasmittente" in params and params["EmailTrasmittente"]:
        ET.SubElement(contatti_trasm, "Email").text = params["EmailTrasmittente"]

    # 2. Cedente/Prestatore
    cedente = ET.SubElement(header, "CedentePrestatore")
    dati_anag = ET.SubElement(cedente, "DatiAnagrafici")
    id_iva = ET.SubElement(dati_anag, "IdFiscaleIVA")
    ET.SubElement(id_iva, "IdPaese").text = validate_param(params["IdPaeseMittente"], VALID_COUNTRIES, "IdPaese")
    ET.SubElement(id_iva, "IdCodice").text = params["IdCodiceMittente"]
    ET.SubElement(dati_anag, "CodiceFiscale").text = params["CodiceFiscaleMittente"]
    anagrafica = ET.SubElement(dati_anag, "Anagrafica")
    ET.SubElement(anagrafica, "Denominazione").text = params["DenominazioneMittente"]
    ET.SubElement(dati_anag, "RegimeFiscale").text = validate_param(params["RegimeFiscale"], VALID_REGIMI_FISCALI, "RegimeFiscale")

    # Sede del cedente
    sede = ET.SubElement(cedente, "Sede")
    ET.SubElement(sede, "Indirizzo").text = params["IndirizzoMittente"]
    ET.SubElement(sede, "CAP").text = params["CAPMittente"]
    ET.SubElement(sede, "Comune").text = params["ComuneMittente"]
    ET.SubElement(sede, "Provincia").text = params["ProvinciaMittente"]
    ET.SubElement(sede, "Nazione").text = validate_param(params["NazioneMittente"], VALID_COUNTRIES, "Nazione")
    
    # Iscrizione REA (opzionale)
    if "UfficioREA" in params and params["UfficioREA"]:
        iscr_rea = ET.SubElement(cedente, "IscrizioneREA")
        ET.SubElement(iscr_rea, "Ufficio").text = params["UfficioREA"]
        ET.SubElement(iscr_rea, "NumeroREA").text = params["NumeroREA"]
        ET.SubElement(iscr_rea, "CapitaleSociale").text = params["CapitaleSociale"]
        ET.SubElement(iscr_rea, "SocioUnico").text = params["SocioUnico"]
        ET.SubElement(iscr_rea, "StatoLiquidazione").text = params["StatoLiquidazione"]
    
    # Contatti (opzionale)
    if "TelefonoCedente" in params and params["TelefonoCedente"]:
        contatti = ET.SubElement(cedente, "Contatti")
        ET.SubElement(contatti, "Telefono").text = params["TelefonoCedente"]
        if "EmailCedente" in params and params["EmailCedente"]:
            ET.SubElement(contatti, "Email").text = params["EmailCedente"]
    
    # 3. Cessionario/Committente (destinatario)
    cessionario = ET.SubElement(header, "CessionarioCommittente")
    dati_anag_cess = ET.SubElement(cessionario, "DatiAnagrafici")
    if "IdCodiceDestinatario" in params and params["IdCodiceDestinatario"]:
        id_iva_cess = ET.SubElement(dati_anag_cess, "IdFiscaleIVA")
        ET.SubElement(id_iva_cess, "IdPaese").text = validate_param(params["IdPaeseDestinatario"], VALID_COUNTRIES, "IdPaeseDestinatario")
        ET.SubElement(id_iva_cess, "IdCodice").text = params["IdCodiceDestinatario"]
    
    if "CodiceFiscaleDestinatario" in params and params["CodiceFiscaleDestinatario"]:
        ET.SubElement(dati_anag_cess, "CodiceFiscale").text = params["CodiceFiscaleDestinatario"]
    
    anagrafica_cess = ET.SubElement(dati_anag_cess, "Anagrafica")
    ET.SubElement(anagrafica_cess, "Denominazione").text = params["DenominazioneDestinatario"]
    
    # Sede del destinatario
    sede_dest = ET.SubElement(cessionario, "Sede")
    ET.SubElement(sede_dest, "Indirizzo").text = params["IndirizzoDestinatario"]
    ET.SubElement(sede_dest, "CAP").text = params["CAPDestinatario"]
    ET.SubElement(sede_dest, "Comune").text = params["ComuneDestinatario"]
    ET.SubElement(sede_dest, "Provincia").text = params["ProvinciaDestinatario"]
    ET.SubElement(sede_dest, "Nazione").text = validate_param(params["NazioneDestinatario"], VALID_COUNTRIES, "NazioneDestinatario")
    
    # BODY
    body = ET.SubElement(root, "FatturaElettronicaBody")
    
    # 1. Dati Generali
    dati_gen = ET.SubElement(body, "DatiGenerali")
    dati_doc = ET.SubElement(dati_gen, "DatiGeneraliDocumento")
    ET.SubElement(dati_doc, "TipoDocumento").text = validate_param(params.get("TipoDocumento", "TD01"), VALID_TIPI_DOCUMENTO, "TipoDocumento")
    ET.SubElement(dati_doc, "Divisa").text = params.get("Divisa", "EUR")
    ET.SubElement(dati_doc, "Data").text = params.get("DataFattura", dati_access.get("Data", ""))
    ET.SubElement(dati_doc, "Numero").text = params.get("NumeroFattura", dati_access.get("Numero", ""))
    ET.SubElement(dati_doc, "ImportoTotaleDocumento").text = params.get("ImportoTotale", dati_access.get("ImportoTotale", "0.00"))
    ET.SubElement(dati_doc, "Causale").text = params.get("Causale", dati_access.get("Causale", ""))
    
    # 2. Dati Beni Servizi
    dati_beni_servizi = ET.SubElement(body, "DatiBeniServizi")
    
    # Dettaglio Linee - Linea 1
    if all(k in params for k in ("L1_Descrizione", "L1_Quantita", "L1_PrezzoUnitario")):
        dettaglio1 = ET.SubElement(dati_beni_servizi, "DettaglioLinee")
        ET.SubElement(dettaglio1, "NumeroLinea").text = "1"
        ET.SubElement(dettaglio1, "Descrizione").text = params["L1_Descrizione"]
        ET.SubElement(dettaglio1, "Quantita").text = params["L1_Quantita"]
        
        if "L1_UnitaMisura" in params and params["L1_UnitaMisura"]:
            ET.SubElement(dettaglio1, "UnitaMisura").text = params["L1_UnitaMisura"]
        
        ET.SubElement(dettaglio1, "PrezzoUnitario").text = params["L1_PrezzoUnitario"]
        
        # Sconto/Maggiorazione (opzionale)
        if "L1_Sconto" in params and params["L1_Sconto"]:
            sconto1 = ET.SubElement(dettaglio1, "ScontoMaggiorazione")
            ET.SubElement(sconto1, "Tipo").text = "SC"  # SC: sconto, MG: maggiorazione
            ET.SubElement(sconto1, "Percentuale").text = params["L1_Sconto"]
        
        ET.SubElement(dettaglio1, "PrezzoTotale").text = params["L1_PrezzoTotale"]
        ET.SubElement(dettaglio1, "AliquotaIVA").text = params.get("L1_AliquotaIVA", "0.00")
        
        # Natura IVA (opzionale)
        if "L1_Natura" in params and params["L1_Natura"]:
            ET.SubElement(dettaglio1, "Natura").text = params["L1_Natura"]
    
    # Dettaglio Linee - Linea 2
    if all(k in params for k in ("L2_Descrizione", "L2_Quantita", "L2_PrezzoUnitario")):
        dettaglio2 = ET.SubElement(dati_beni_servizi, "DettaglioLinee")
        ET.SubElement(dettaglio2, "NumeroLinea").text = "2"
        ET.SubElement(dettaglio2, "Descrizione").text = params["L2_Descrizione"]
        ET.SubElement(dettaglio2, "Quantita").text = params["L2_Quantita"]
        
        if "L2_UnitaMisura" in params and params["L2_UnitaMisura"]:
            ET.SubElement(dettaglio2, "UnitaMisura").text = params["L2_UnitaMisura"]
        
        ET.SubElement(dettaglio2, "PrezzoUnitario").text = params["L2_PrezzoUnitario"]
        
        # Sconto/Maggiorazione (opzionale)
        if "L2_Sconto" in params and params["L2_Sconto"]:
            sconto2 = ET.SubElement(dettaglio2, "ScontoMaggiorazione")
            ET.SubElement(sconto2, "Tipo").text = "SC"
            ET.SubElement(sconto2, "Percentuale").text = params["L2_Sconto"]
        
        ET.SubElement(dettaglio2, "PrezzoTotale").text = params["L2_PrezzoTotale"]
        ET.SubElement(dettaglio2, "AliquotaIVA").text = params.get("L2_AliquotaIVA", "0.00")
        
        # Natura IVA (opzionale)
        if "L2_Natura" in params and params["L2_Natura"]:
            ET.SubElement(dettaglio2, "Natura").text = params["L2_Natura"]
    
    # Dati Riepilogo
    if all(k in params for k in ("Riepilogo_AliquotaIVA", "Riepilogo_Imponibile")):
        riepilogo = ET.SubElement(dati_beni_servizi, "DatiRiepilogo")
        ET.SubElement(riepilogo, "AliquotaIVA").text = params["Riepilogo_AliquotaIVA"]
        
        # Natura IVA (opzionale)
        if "Riepilogo_Natura" in params and params["Riepilogo_Natura"]:
            ET.SubElement(riepilogo, "Natura").text = params["Riepilogo_Natura"]
        
        ET.SubElement(riepilogo, "ImponibileImporto").text = params["Riepilogo_Imponibile"]
        ET.SubElement(riepilogo, "Imposta").text = params["Riepilogo_Imposta"]
        
        # Riferimento Normativo (opzionale)
        if "Riepilogo_Riferimento" in params and params["Riepilogo_Riferimento"]:
            # Tronca il valore a 100 caratteri come richiesto dallo schema XML
            riferimento_normativo = params["Riepilogo_Riferimento"][:100]
            ET.SubElement(riepilogo, "RiferimentoNormativo").text = riferimento_normativo
    
    # 3. Dati di Pagamento
    if all(k in params for k in ("CondizioniPagamento", "ModalitaPagamento", "ImportoPagamento")):
        dati_pagamento = ET.SubElement(body, "DatiPagamento")
        ET.SubElement(dati_pagamento, "CondizioniPagamento").text = params["CondizioniPagamento"]
        
        dettaglio_pagamento = ET.SubElement(dati_pagamento, "DettaglioPagamento")
        ET.SubElement(dettaglio_pagamento, "ModalitaPagamento").text = validate_param(
            params["ModalitaPagamento"], VALID_MODALITA_PAGAMENTO, "ModalitaPagamento")
        ET.SubElement(dettaglio_pagamento, "ImportoPagamento").text = params["ImportoPagamento"]
        
        # IBAN (opzionale)
        if "IBAN" in params and params["IBAN"]:
            ET.SubElement(dettaglio_pagamento, "IBAN").text = params["IBAN"]
    
    # Convert the ElementTree to string with encoding specified
    xml_bytes = ET.tostring(root, encoding="utf-8")
    with open("data/output.xml", "wb") as f:
        f.write(xml_bytes)

    # Parse with minidom for pretty printing, maintaining correct namespace handling
    dom = minidom.parseString(xml_bytes)
    
    # Format with proper indentation
    pretty_xml = dom.toprettyxml(indent="  ", encoding="utf-8")
    
    # Convert bytes to string for return
    pretty_xml_str = pretty_xml.decode('utf-8')
    
    # Remove extra blank lines that minidom sometimes adds
    lines = pretty_xml_str.splitlines()
    filtered_lines = [line for line in lines if line.strip()]
    pretty_xml_clean = '\n'.join(filtered_lines)
    
    # Ensure XML declaration is correct
    if not pretty_xml_clean.startswith('<?xml'):
        pretty_xml_clean = '<?xml version="1.0" encoding="UTF-8"?>\n' + pretty_xml_clean
    
    # Add a final newline
    if not pretty_xml_clean.endswith('\n'):
        pretty_xml_clean += '\n'
        
    return pretty_xml_clean
