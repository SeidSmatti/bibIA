# bibIA/app.py

"""
Application principale de bibIA avec Streamlit.
"""

import streamlit as st
import asyncio
from typing import List, Dict, Any

# On importe le module de configuration pour pouvoir modifier ses variables dynamiquement
import src.config as config
from src.parser import split_bibliography, parse_entry
from src.verifier import verify_references

def initialize_state():
    """Initialise les variables dans le session_state de Streamlit."""
    if 'entries' not in st.session_state:
        st.session_state.entries = []
    if 'verification_results' not in st.session_state:
        st.session_state.verification_results = []

def display_results(results: List[Dict[str, Any]]):
    """Affiche les résultats de la vérification de manière riche et détaillée."""
    st.header("Résultats de la vérification")
    if not results:
        st.info("Aucun résultat à afficher.")
        return

    for i, result in enumerate(results):
        status = result.get('status', 'not_verifiable')
        with st.container(border=True):
            if status == 'found':
                st.success(f"**Entrée #{i+1} : TROUVÉE**", icon="✅")
            elif status == 'not_found':
                st.error(f"**Entrée #{i+1} : NON TROUVÉE**", icon="❌")
            else:
                st.warning(f"**Entrée #{i+1} : VÉRIFICATION INCOMPLÈTE OU IMPOSSIBLE**", icon="⚠️")
            
            st.markdown(f"> {result.get('original_text', '')}")
            with st.expander("Voir les détails de l'analyse et de la vérification"):
                # ... (code d'affichage des détails inchangé) ...
                st.subheader("Données utilisées pour la vérification")
                parsed_data = {k: v for k, v in result.items() if k not in ['original_text', 'verification_details', 'status', 'found_in']}
                st.json(parsed_data)
                st.subheader("Journal de vérification par source")
                details = result.get('verification_details', [])
                if not details:
                    st.caption("Aucune source n'a pu être interrogée.")
                else:
                    for source_result in details:
                        s_name = source_result.get('source')
                        s_status = source_result.get('status')
                        s_link = source_result.get('link')
                        s_details = source_result.get('details') or source_result.get('reason')
                        if s_status == 'found':
                            st.markdown(f"✔️ **{s_name} :** Trouvé ! → [Lien]({s_link})")
                        elif s_status == 'not_found':
                            st.markdown(f"❌ **{s_name} :** Non trouvé.")
                        elif s_status == 'error':
                            st.markdown(f"⚠️ **{s_name} :** Erreur ({s_details})")
                        elif s_status == 'skipped':
                            st.markdown(f"⏩ **{s_name} :** Ignoré ({s_details})")


async def main():
    """Fonction principale qui exécute l'application Streamlit."""
    st.set_page_config(page_title="VerifBiblio", layout="wide", initial_sidebar_state="collapsed")
    
    initialize_state()

    st.title("bibIA : Détecteur de Bibliographie Hallucinée 🤖")
    st.markdown("Une application pour vérifier la validité de vos références bibliographiques avec Google Scholar et crossref")

    st.info("ℹ️ **Mode d'emploi** : **1.** Collez votre bibliographie. **2.** Cliquez sur `Analyser`. **3.** Corrigez les éléments détectés si besoin. **4.** Choisissez un délai et cliquez sur `Vérifier`.")

    raw_bibliography_input = st.text_area(
        label="**Étape 1 : Collez votre bibliographie ici**",
        height=250,
        placeholder="Exemple :\n\nFoucault, M. (1975). Surveiller et punir : Naissance de la prison. Gallimard."
    )

    if st.button("Analyser la bibliographie", type="primary"):
        # ... (logique d'analyse inchangée) ...
        if not raw_bibliography_input.strip():
            st.warning("Le champ de la bibliographie est vide.")
        else:
            with st.spinner("Analyse et parsing des entrées..."):
                detected_entries = split_bibliography(raw_bibliography_input)
                st.session_state.entries = [parse_entry(entry) for entry in detected_entries]
                st.session_state.verification_results = []
            st.success(f"{len(st.session_state.entries)} entrées bibliographiques détectées et prêtes pour la validation.")

    if st.session_state.entries:
        st.markdown("---")
        st.header("Étape 2 & 3 : Validez les données et lancez la vérification")
        
        with st.form(key='correction_form'):
            for i, entry_data in enumerate(st.session_state.entries):
                with st.container(border=True):
                    # ... (formulaire de modification des entrées inchangé) ...
                    st.markdown(f"**Entrée #{i+1}**")
                    st.text_area("Texte original", value=entry_data["original_text"], key=f"original_text_{i}", label_visibility="collapsed")
                    st.markdown("###### Éléments détectés (modifiables) :")
                    cols = st.columns(2)
                    entry_data['author'] = cols[0].text_input("Auteur(s)", value=entry_data.get('author'), key=f"author_{i}")
                    entry_data['year'] = cols[1].text_input("Année", value=entry_data.get('year'), key=f"year_{i}")
                    entry_data['title'] = st.text_input("Titre", value=entry_data.get('title'), key=f"title_{i}")
                    cols_journal = st.columns(3)
                    entry_data['journal'] = cols_journal[0].text_input("Revue/Journal", value=entry_data.get('journal'), key=f"journal_{i}")
                    entry_data['volume'] = cols_journal[1].text_input("Volume", value=entry_data.get('volume'), key=f"volume_{i}")
                    entry_data['pages'] = cols_journal[2].text_input("Pages", value=entry_data.get('pages'), key=f"pages_{i}")
                    entry_data['doi'] = st.text_input("DOI", value=entry_data.get('doi'), key=f"doi_{i}")
            
            st.markdown("---")
            
            # --- WIDGET DE SÉLECTION DU DÉLAI ---
            st.subheader("Options de la vérification")
            delay_option = st.radio(
                "Discrétion des requêtes (délai entre chaque appel)",
                options=["Rapide", "Prudent (Défaut)", "Très Prudent"],
                index=1, # "Prudent" est sélectionné par défaut
                captions=[
                    "1-3 secondes. Rapide mais plus risqué d'être bloqué par Google.",
                    "10-20 secondes. Bon équilibre pour ne pas être bloqué.",
                    "20-30 secondes. Très lent mais le plus sûr"
                ],
                horizontal=True,
            )

            submitted = st.form_submit_button(
                "Vérifier toutes les références", 
                type="primary", 
                use_container_width=True
            )

            if submitted:
                # --- LOGIQUE DE MISE À JOUR DYNAMIQUE DU DÉLAI ---
                if delay_option == "Rapide":
                    config.RANDOM_DELAY_RANGE = (1.0, 3.0)
                elif delay_option == "Prudent (Défaut)":
                    config.RANDOM_DELAY_RANGE = (10.0, 20.0)
                elif delay_option == "Très Prudent":
                    config.RANDOM_DELAY_RANGE = (20.0, 30.0)

                with st.spinner(f"Vérification en cours avec un délai de {delay_option}..."):
                    results = await verify_references(st.session_state.entries)
                    st.session_state.verification_results = results

    if st.session_state.verification_results:
        st.markdown("---")
        display_results(st.session_state.verification_results)

if __name__ == "__main__":
    asyncio.run(main())
