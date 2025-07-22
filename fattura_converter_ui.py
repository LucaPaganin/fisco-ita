# app.py
import streamlit as st
from backend import (
    parse_access_xml, crea_fattura_elettronica,
    VALID_COUNTRIES, VALID_REGIMI_FISCALI,
    VALID_FORMATI_TRASMISSIONE, VALID_TIPI_DOCUMENTO,
    VALID_MODALITA_PAGAMENTO
)

st.set_page_config(page_title="Converti Fattura Access → XML PA")
st.title("Convertitore XML Fattura Elettronica")

uploaded_file = st.file_uploader("Carica file XML da Access", type=["xml"])

with st.form("config_form"):
    st.subheader("Parametri obbligatori")
    col1, col2 = st.columns(2)

    with col1:
        id_paese = st.selectbox("Id Paese Mittente", VALID_COUNTRIES)
        id_codice = st.text_input("Id Codice Mittente")
        codice_fiscale = st.text_input("Codice Fiscale Mittente")
        denominazione = st.text_input("Denominazione Mittente")
        regime = st.selectbox("Regime Fiscale", VALID_REGIMI_FISCALI)
        formato = st.selectbox("Formato Trasmissione", VALID_FORMATI_TRASMISSIONE)
        tipo_documento = st.selectbox("Tipo Documento", VALID_TIPI_DOCUMENTO)

    with col2:
        indirizzo = st.text_input("Indirizzo Mittente")
        cap = st.text_input("CAP")
        comune = st.text_input("Comune")
        provincia = st.text_input("Provincia")
        nazione = st.selectbox("Nazione Mittente", VALID_COUNTRIES)
        progressivo = st.text_input("Progressivo Invio")
        codice_dest = st.text_input("Codice Destinatario")

    submitted = st.form_submit_button("Genera XML valido")

if uploaded_file and submitted:
    try:
        content = uploaded_file.read()
        dati = parse_access_xml(content)
        params = {
            "IdPaeseMittente": id_paese,
            "IdCodiceMittente": id_codice,
            "CodiceFiscaleMittente": codice_fiscale,
            "DenominazioneMittente": denominazione,
            "RegimeFiscale": regime,
            "FormatoTrasmissione": formato,
            "TipoDocumento": tipo_documento,
            "IndirizzoMittente": indirizzo,
            "CAPMittente": cap,
            "ComuneMittente": comune,
            "ProvinciaMittente": provincia,
            "NazioneMittente": nazione,
            "ProgressivoInvio": progressivo,
            "CodiceDestinatario": codice_dest
        }
        xml_output = crea_fattura_elettronica(dati, params)
        st.success("✅ XML generato correttamente!")
        st.download_button("📥 Scarica XML", xml_output, file_name="Fattura_Elettronica.xml")
    except Exception as e:
        st.error(f"❌ Errore durante la generazione: {e}")
