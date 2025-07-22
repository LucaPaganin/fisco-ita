# app.py
import streamlit as st
from xml_invoice_backend import (
    parse_access_xml, crea_fattura_elettronica,
    VALID_COUNTRIES, VALID_REGIMI_FISCALI,
    VALID_FORMATI_TRASMISSIONE, VALID_TIPI_DOCUMENTO,
    VALID_MODALITA_PAGAMENTO, XML_SCHEMA_NAMESPACE
)

st.set_page_config(page_title="Converti Fattura Access → XML PA")
st.title("Convertitore XML Fattura Elettronica")

uploaded_file = st.file_uploader("Carica file XML da Access", type=["xml"])

with st.form("config_form"):
    tabs = st.tabs(["Dati Trasmissione", "Cedente/Prestatore", "Destinatario", "Dati Fattura", "Beni e Servizi", "Pagamenti"])
    
    with tabs[0]:  # Dati Trasmissione
        st.subheader("Dati Trasmissione")
        col1, col2 = st.columns(2)
        
        with col1:
            id_paese = st.selectbox("Id Paese Mittente", VALID_COUNTRIES, index=VALID_COUNTRIES.index("IT") if "IT" in VALID_COUNTRIES else 0, 
                                   help="Codice ISO della nazione a 2 caratteri")
            id_codice = st.text_input("Id Codice Mittente", value="01036270096", 
                                     help="Identificativo fiscale (es. Partita IVA)")
            progressivo = st.text_input("Progressivo Invio", value="tPpUu",
                                       help="Identificativo univoco del file")
            
        with col2:
            formato = st.selectbox("Formato Trasmissione", VALID_FORMATI_TRASMISSIONE, 
                                  index=VALID_FORMATI_TRASMISSIONE.index("FPR12") if "FPR12" in VALID_FORMATI_TRASMISSIONE else 0,
                                  help="FPR12: Fattura verso privati, FPA12: Fattura verso PA")
            codice_dest = st.text_input("Codice Destinatario", value="X2PH38J",
                                       help="Codice destinatario (6-7 caratteri)")
            
        st.subheader("Contatti Trasmittente")
        col1, col2 = st.columns(2)
        with col1:
            telefono_trasmittente = st.text_input("Telefono Trasmittente", value="0409751179", 
                                                 help="Telefono del trasmittente")
        with col2:
            email_trasmittente = st.text_input("Email Trasmittente", value="info@fatturaelettronica.pa.it",
                                              help="Email del trasmittente")
    
    with tabs[1]:  # Cedente/Prestatore
        st.subheader("Dati Cedente/Prestatore")
        col1, col2 = st.columns(2)
        
        with col1:
            codice_fiscale = st.text_input("Codice Fiscale", value="01036270096",
                                          help="Codice Fiscale")
            denominazione = st.text_input("Denominazione", value="EREDI MASTROIANNI SRL",
                                         help="Denominazione o ragione sociale")
            regime = st.selectbox("Regime Fiscale", VALID_REGIMI_FISCALI, 
                                 index=VALID_REGIMI_FISCALI.index("RF01") if "RF01" in VALID_REGIMI_FISCALI else 0,
                                 help="Regime fiscale del mittente")
        with col2:
            indirizzo = st.text_input("Indirizzo", value="VIA RIO GALLETTO 17",
                                     help="Indirizzo completo")
            cap = st.text_input("CAP", value="17100", 
                               help="Codice Avviamento Postale")
            comune = st.text_input("Comune", value="Savona",
                                  help="Comune della sede")
            provincia = st.text_input("Provincia", value="SV",
                                     help="Sigla provincia (2 caratteri)")
            nazione = st.selectbox("Nazione", VALID_COUNTRIES, 
                                  index=VALID_COUNTRIES.index("IT") if "IT" in VALID_COUNTRIES else 0,
                                  help="Codice ISO della nazione a 2 caratteri")
            
        st.subheader("Dati REA")
        col1, col2, col3 = st.columns(3)
        with col1:
            rea_ufficio = st.text_input("Ufficio REA", value="SV", help="Sigla provincia dell'Ufficio REA")
            rea_numero = st.text_input("Numero REA", value="01036270096", help="Numero di iscrizione al REA")
        with col2:
            rea_capitale = st.text_input("Capitale Sociale", value="0.00", help="Capitale sociale in Euro")
            rea_socio_unico = st.text_input("Socio Unico", value="SM", help="SM: società con più soci, SU: socio unico")
        with col3:
            rea_liquidazione = st.text_input("Stato Liquidazione", value="LN", help="LN: non in liquidazione, LS: in liquidazione")
        
        st.subheader("Contatti")
        col1, col2 = st.columns(2)
        with col1:
            telefono_cedente = st.text_input("Telefono", value="019862194", help="Telefono del cedente")
        with col2:
            email_cedente = st.text_input("Email", value="amministrazione@eredimastroianni.it", help="Email del cedente")
            
    with tabs[2]:  # Destinatario
        st.subheader("Dati Destinatario")
        col1, col2 = st.columns(2)
        
        # Estrai i dati del destinatario dal file XML se presente
        default_dest = {}
        if uploaded_file:
            try:
                dati_tmp = parse_access_xml(uploaded_file.read())
                uploaded_file.seek(0)
                default_dest = dati_tmp.get("Destinatario", {})
            except:
                default_dest = {}
        
        with col1:
            id_paese_dest = st.selectbox("Id Paese Destinatario", VALID_COUNTRIES, 
                                        index=VALID_COUNTRIES.index("IT") if "IT" in VALID_COUNTRIES else 0,
                                        help="Codice ISO della nazione destinatario")
            id_codice_dest = st.text_input("Id Codice Destinatario", 
                                         value=default_dest.get("PartitaIVA", "00267740108"),
                                         help="Partita IVA destinatario")
            cf_dest = st.text_input("Codice Fiscale Destinatario", 
                                  value=default_dest.get("CodiceFiscale", "00267740108"),
                                  help="Codice Fiscale destinatario")
            denominazione_dest = st.text_input("Denominazione Destinatario", 
                                             value=default_dest.get("Denominazione", "CARTIERA TORRE MONDOVI' SPA"),
                                             help="Denominazione del destinatario")
        with col2:
            indirizzo_dest = st.text_input("Indirizzo Destinatario", 
                                          value=default_dest.get("Indirizzo", "VIA BOSSO 3"),
                                          help="Indirizzo del destinatario")
            cap_dest = st.text_input("CAP Destinatario", 
                                    value=default_dest.get("CAP", "12080"),
                                    help="CAP del destinatario")
            comune_dest = st.text_input("Comune Destinatario", 
                                       value=default_dest.get("Comune", "TORRE MONDOVI'"),
                                       help="Comune del destinatario")
            provincia_dest = st.text_input("Provincia Destinatario", 
                                          value=default_dest.get("Provincia", "CN"),
                                          help="Provincia del destinatario")
            nazione_dest = st.selectbox("Nazione Destinatario", VALID_COUNTRIES,
                                       index=VALID_COUNTRIES.index("IT") if "IT" in VALID_COUNTRIES else 0,
                                       help="Nazione del destinatario")
    
    with tabs[3]:  # Dati Fattura
        st.subheader("Dati Generali Documento")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Usa TD01 come default per fattura normake
            tipo_documento = st.selectbox("Tipo Documento", VALID_TIPI_DOCUMENTO, 
                                         index=VALID_TIPI_DOCUMENTO.index("TD01") if "TD01" in VALID_TIPI_DOCUMENTO else 0,
                                         help="Tipologia di documento")
            divisa = st.text_input("Divisa", value="EUR", help="Valuta del documento")
        
        with col2:
            # Usa FatturaNum dal file Fattura.xml se presente, altrimenti default
            default_numero = ""
            default_data = ""
            if uploaded_file:
                try:
                    dati_tmp = parse_access_xml(uploaded_file.read())
                    uploaded_file.seek(0)  # Reimposta il puntatore del file per successive letture
                    default_numero = dati_tmp.get("Numero", "255FE25")
                    default_data = dati_tmp.get("Data", "2025-07-21")
                except:
                    default_numero = "255FE25"
                    default_data = "2025-07-21"
            else:
                default_numero = "255FE25"
                default_data = "2025-07-21"
                
            numero_fattura = st.text_input("Numero Fattura", value=default_numero, help="Numero della fattura")
            data_fattura = st.text_input("Data Fattura", value=default_data, help="Data della fattura (YYYY-MM-DD)")
        
        with col3:
            importo_totale = st.text_input("Importo Totale", value="3632.66", help="Importo totale documento")
            
            # Usa Note dal file Fattura.xml se presente, altrimenti default
            default_causale = ""
            if uploaded_file:
                try:
                    dati_tmp = parse_access_xml(uploaded_file.read())
                    uploaded_file.seek(0)
                    default_causale = dati_tmp.get("Causale", "Applicato sconto 2% per pagamento immediato")
                except:
                    default_causale = "Applicato sconto 2% per pagamento immediato"
            else:
                default_causale = "Applicato sconto 2% per pagamento immediato"
                
            causale = st.text_input("Causale", value=default_causale, help="Causale del documento")
    
    with tabs[4]:  # Beni e Servizi
        st.subheader("Dettaglio Linee")
        st.caption("Per semplicità, vengono inclusi due dettagli linea fissi. In un'implementazione completa, questi dovrebbero essere dinamici.")
        
        st.markdown("**Linea 1**")
        col1, col2 = st.columns(2)
        with col1:
            l1_descrizione = st.text_input("Descrizione Linea 1", value="VENDITA CARTONE 100% DA MACERO DDT 78 DEL 18/07/25",
                                         help="Descrizione della linea 1")
            l1_quantita = st.text_input("Quantità Linea 1", value="24.68", help="Quantità della linea 1")
            l1_unita = st.text_input("Unità di Misura Linea 1", value="TONN", help="Unità di misura della linea 1")
        with col2:
            l1_prezzo = st.text_input("Prezzo Unitario Linea 1", value="110.00", help="Prezzo unitario della linea 1")
            l1_sconto = st.text_input("Percentuale Sconto Linea 1", value="2.00", help="Percentuale di sconto della linea 1")
            l1_prezzo_totale = st.text_input("Prezzo Totale Linea 1", value="2660.50", help="Prezzo totale della linea 1")
            l1_aliquota_iva = st.text_input("Aliquota IVA Linea 1", value="0.00", help="Aliquota IVA della linea 1")
            l1_natura = st.text_input("Natura IVA Linea 1", value="N6.1", help="Natura IVA della linea 1")
            
        st.markdown("**Linea 2**")
        col1, col2 = st.columns(2)
        with col1:
            l2_descrizione = st.text_input("Descrizione Linea 2", value="VENDITA ARCHIVIO BIANCO DA MACERO DDT 78 DEL 18/07/25",
                                         help="Descrizione della linea 2")
            l2_quantita = st.text_input("Quantità Linea 2", value="3.10", help="Quantità della linea 2")
            l2_unita = st.text_input("Unità di Misura Linea 2", value="TONN", help="Unità di misura della linea 2")
        with col2:
            l2_prezzo = st.text_input("Prezzo Unitario Linea 2", value="320.00", help="Prezzo unitario della linea 2")
            l2_sconto = st.text_input("Percentuale Sconto Linea 2", value="2.00", help="Percentuale di sconto della linea 2")
            l2_prezzo_totale = st.text_input("Prezzo Totale Linea 2", value="972.16", help="Prezzo totale della linea 2")
            l2_aliquota_iva = st.text_input("Aliquota IVA Linea 2", value="0.00", help="Aliquota IVA della linea 2")
            l2_natura = st.text_input("Natura IVA Linea 2", value="N6.1", help="Natura IVA della linea 2")
            
        st.subheader("Dati Riepilogo")
        
        # Estrai i dati IVA dal file XML se presente
        default_iva = "0.00"
        default_note_iva = ""
        if uploaded_file:
            try:
                dati_tmp = parse_access_xml(uploaded_file.read())
                uploaded_file.seek(0)
                default_iva = dati_tmp.get("IVA", "0.00")
                # Tronca NoteIVA a 100 caratteri come richiesto dallo schema XML
                note_iva_tmp = dati_tmp.get("NoteIVA", "Art 74 Reverse Charge")
                default_note_iva = note_iva_tmp[:100] if note_iva_tmp else "Art 74 Reverse Charge"
            except:
                default_iva = "0.00"
                default_note_iva = "Art 74 Reverse Charge"
                
        col1, col2 = st.columns(2)
        with col1:
            riepilogo_aliquota = st.text_input("Aliquota IVA", value=default_iva, help="Aliquota IVA del riepilogo")
            riepilogo_natura = st.text_input("Natura IVA", value="N6.1", help="Natura IVA del riepilogo")
        with col2:
            riepilogo_imponibile = st.text_input("Imponibile", value="3632.66", help="Importo imponibile")
            riepilogo_imposta = st.text_input("Imposta", value="0.00", help="Imposta")
            riepilogo_riferimento = st.text_input("Riferimento Normativo", value=default_note_iva, 
                                               help="Riferimento normativo")
    
    with tabs[5]:  # Pagamenti
        st.subheader("Dati Pagamento")
        
        # Estrai i dati di pagamento dal file XML se presente
        default_modo_pag = ""
        default_tempo_pag = ""
        if uploaded_file:
            try:
                dati_tmp = parse_access_xml(uploaded_file.read())
                uploaded_file.seek(0)
                default_modo_pag = dati_tmp.get("ModoPagamento", "")
                default_tempo_pag = dati_tmp.get("TempoPagamento", "")
            except:
                default_modo_pag = ""
                default_tempo_pag = ""
        
        # Mappa tra i modi di pagamento in Access e i codici ModalitaPagamento
        modo_pag_map = {
            "BON.BANC": "MP05",  # Bonifico
            "CONTANTI": "MP01",   # Contanti
            "ASS.BANC": "MP02",   # Assegno
            "RIB.BANC": "MP12",   # RIBA
        }
        
        # Mappa tra i tempi di pagamento in Access e i codici CondizioniPagamento
        tempo_pag_map = {
            "RDVF": "TP02",      # Pagamento completo
            "RATE": "TP01",      # Pagamento a rate
            "ANTI": "TP03",      # Anticipo
        }
        
        # Determina il valore predefinito per ModalitaPagamento
        default_modalita = modo_pag_map.get(default_modo_pag, "MP05")
        # Determina il valore predefinito per CondizioniPagamento
        default_condizioni = tempo_pag_map.get(default_tempo_pag, "TP02")
        
        col1, col2 = st.columns(2)
        with col1:
            condizioni_pagamento = st.text_input("Condizioni Pagamento", value=default_condizioni, 
                                               help="TP01: pagamento a rate, TP02: pagamento completo, TP03: anticipo")
        with col2:
            modalita_pagamento = st.selectbox("Modalità Pagamento", VALID_MODALITA_PAGAMENTO,
                                            index=VALID_MODALITA_PAGAMENTO.index(default_modalita) 
                                                  if default_modalita in VALID_MODALITA_PAGAMENTO 
                                                  else VALID_MODALITA_PAGAMENTO.index("MP05"),
                                            help="Modalità di pagamento")
            
        col1, col2 = st.columns(2)
        with col1:
            importo_pagamento = st.text_input("Importo Pagamento", value="3632.66", help="Importo del pagamento")
        with col2:
            iban = st.text_input("IBAN", value="IT06G0538749530000047355346", help="IBAN per il pagamento")

    st.subheader("Opzioni")
    use_local_schema = st.checkbox("Usa schema locale", value=False, 
                                 help="Utilizza lo schema XSD locale anziché quello online")

    submitted = st.form_submit_button("Genera XML valido")

if uploaded_file and submitted:
    try:
        # Convert to string for better error handling
        content = uploaded_file.read()
        content_str = content.decode('utf-8')
        
        # Debug information in an expander to save screen space
        with st.expander("Debug - XML Contenuto"):
            st.code(content_str[:1000] + "..." if len(content_str) > 1000 else content_str)
        
        # Parse the input XML
        dati = parse_access_xml(content)
        
        # Prepare parameters for fattura elettronica
        params = {
            # Opzioni generali
            "UseLocalSchema": use_local_schema,
            
            # Dati Trasmissione
            "IdPaeseMittente": id_paese,
            "IdCodiceMittente": id_codice,
            "ProgressivoInvio": progressivo,
            "FormatoTrasmissione": formato,
            "CodiceDestinatario": codice_dest,
            "TelefonoTrasmittente": telefono_trasmittente,
            "EmailTrasmittente": email_trasmittente,
            
            # Cedente/Prestatore
            "CodiceFiscaleMittente": codice_fiscale,
            "DenominazioneMittente": denominazione,
            "RegimeFiscale": regime,
            "IndirizzoMittente": indirizzo,
            "CAPMittente": cap,
            "ComuneMittente": comune,
            "ProvinciaMittente": provincia,
            "NazioneMittente": nazione,
            
            # REA
            "UfficioREA": rea_ufficio,
            "NumeroREA": rea_numero,
            "CapitaleSociale": rea_capitale,
            "SocioUnico": rea_socio_unico,
            "StatoLiquidazione": rea_liquidazione,
            
            # Contatti
            "TelefonoCedente": telefono_cedente,
            "EmailCedente": email_cedente,
            
            # Destinatario
            "IdPaeseDestinatario": id_paese_dest,
            "IdCodiceDestinatario": id_codice_dest,
            "CodiceFiscaleDestinatario": cf_dest,
            "DenominazioneDestinatario": denominazione_dest,
            "IndirizzoDestinatario": indirizzo_dest,
            "CAPDestinatario": cap_dest,
            "ComuneDestinatario": comune_dest,
            "ProvinciaDestinatario": provincia_dest,
            "NazioneDestinatario": nazione_dest,
            
            # Dati Fattura
            "TipoDocumento": tipo_documento,
            "Divisa": divisa,
            "NumeroFattura": numero_fattura,
            "DataFattura": data_fattura,
            "ImportoTotale": importo_totale,
            "Causale": causale,
            
            # Dettaglio Linee 1
            "L1_Descrizione": l1_descrizione,
            "L1_Quantita": l1_quantita,
            "L1_UnitaMisura": l1_unita,
            "L1_PrezzoUnitario": l1_prezzo,
            "L1_Sconto": l1_sconto,
            "L1_PrezzoTotale": l1_prezzo_totale,
            "L1_AliquotaIVA": l1_aliquota_iva,
            "L1_Natura": l1_natura,
            
            # Dettaglio Linee 2
            "L2_Descrizione": l2_descrizione,
            "L2_Quantita": l2_quantita,
            "L2_UnitaMisura": l2_unita,
            "L2_PrezzoUnitario": l2_prezzo,
            "L2_Sconto": l2_sconto,
            "L2_PrezzoTotale": l2_prezzo_totale,
            "L2_AliquotaIVA": l2_aliquota_iva,
            "L2_Natura": l2_natura,
            
            # Dati Riepilogo
            "Riepilogo_AliquotaIVA": riepilogo_aliquota,
            "Riepilogo_Natura": riepilogo_natura,
            "Riepilogo_Imponibile": riepilogo_imponibile,
            "Riepilogo_Imposta": riepilogo_imposta,
            "Riepilogo_Riferimento": riepilogo_riferimento,
            
            # Dati Pagamento
            "CondizioniPagamento": condizioni_pagamento,
            "ModalitaPagamento": modalita_pagamento,
            "ImportoPagamento": importo_pagamento,
            "IBAN": iban
        }
        
        # Generate the XML
        xml_output = crea_fattura_elettronica(dati, params)
        
        # Display success and preview
        st.success("✅ XML generato correttamente!")
        
        # Show XML preview
        with st.expander("Anteprima XML"):
            st.code(xml_output[:1000] + "..." if len(xml_output) > 1000 else xml_output, language="xml")
        
        # Download button for the XML file
        st.download_button(
            "📥 Scarica XML", 
            xml_output, 
            file_name=f"Fattura_Elettronica_{dati.get('Numero', 'nuovo')}.xml",
            mime="application/xml"
        )
    except Exception as e:
        st.error(f"❌ Errore durante la generazione: {e}")
        st.error("Controlla che il file XML sia un valido file XML Access con i campi corretti.")
        import traceback
        st.expander("Dettagli errore").code(traceback.format_exc())
