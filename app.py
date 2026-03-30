
import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="PRO-BTP : Devis & Factures", layout="centered")

# --- STYLE PROFESSIONNEL ---
st.markdown("""
    <style>
    .reportview-container { background: #f0f2f6; }
    .stButton>button { width: 100%; border-radius: 5px; background-color: #004a99; color: white; }
    .invoice-box { padding: 20px; border: 1px solid #eee; background-color: white; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALISATION DES DONNÉES ---
if 'prix_db' not in st.session_state:
    st.session_state.prix_db = {
        "Électricité": {"Prise": 12.0, "Interrupteur": 15.0, "Gaine(m)": 2.5, "Tableau": 450.0},
        "Plomberie": {"PER(m)": 3.5, "Raccord": 7.0, "WC Suspendu": 420.0, "Mitigeur": 110.0},
        "Chauffage/PAC": {"Unité PAC": 3800.0, "Split": 600.0, "Liaison(m)": 28.0, "Chaudière Gaz": 2500.0}
    }

if 'panier' not in st.session_state:
    st.session_state.panier = []

# --- MENU PRINCIPAL ---
menu = st.sidebar.selectbox("Navigation", ["Calculateur Chantier", "Gestion des Prix", "Édition Devis/Facture"])

# --- 1. CALCULATEUR DE CHANTIER ---
if menu == "Calculateur Chantier":
    st.title("🏗️ Calculateur de Matériel")
    metier = st.selectbox("Domaine de travaux", ["Électricité", "Plomberie", "Chauffage/PAC"])
    
    with st.container():
        if metier == "Électricité":
            nb_p = st.number_input("Nombre de prises", min_value=0)
            nb_i = st.number_input("Nombre d'interrupteurs", min_value=0)
            if st.button("Ajouter au devis"):
                st.session_state.panier.append({"Article": "Prises", "Qté": nb_p, "PU": st.session_state.prix_db["Électricité"]["Prise"]})
                st.session_state.panier.append({"Article": "Interrupteurs", "Qté": nb_i, "PU": st.session_state.prix_db["Électricité"]["Interrupteur"]})
                st.session_state.panier.append({"Article": "Gaine/Câbles", "Qté": (nb_p+nb_i)*7, "PU": st.session_state.prix_db["Électricité"]["Gaine(m)"]})

        elif metier == "Plomberie":
            points = st.number_input("Nombre de points d'eau", min_value=0)
            if st.button("Ajouter au devis"):
                st.session_state.panier.append({"Article": "Tubes PER", "Qté": points*12, "PU": st.session_state.prix_db["Plomberie"]["PER(m)"]})
                st.session_state.panier.append({"Article": "Raccords", "Qté": points*5, "PU": st.session_state.prix_db["Plomberie"]["Raccord"]})

        elif metier == "Chauffage/PAC":
            type_inst = st.radio("Type", ["PAC Air-Air", "Chaudière Gaz"])
            surface = st.number_input("Surface (m²)", min_value=0)
            if st.button("Ajouter au devis"):
                if type_inst == "PAC Air-Air":
                    st.session_state.panier.append({"Article": "Groupe PAC", "Qté": 1, "PU": st.session_state.prix_db["Chauffage/PAC"]["Unité PAC"]})
                    st.session_state.panier.append({"Article": "Splits", "Qté": (surface//30)+1, "PU": st.session_state.prix_db["Chauffage/PAC"]["Split"]})
                else:
                    st.session_state.panier.append({"Article": "Chaudière Gaz", "Qté": 1, "PU": st.session_state.prix_db["Chauffage/PAC"]["Chaudière Gaz"]})

    if st.session_state.panier:
        st.write("---")
        st.write("🛒 **Contenu actuel du devis :**")
        st.table(pd.DataFrame(st.session_state.panier))
        if st.button("Vider le panier"):
            st.session_state.panier = []
            st.rerun()

# --- 2. GESTION DES PRIX ---
elif menu == "Gestion des Prix":
    st.title("⚙️ Réglage des Tarifs HT")
    for cat, items in st.session_state.prix_db.items():
        with st.expander(f"Modifier {cat}"):
            for art, p in items.items():
                new_p = st.number_input(f"{art} (€)", value=float(p), key=f"edit_{cat}_{art}")
                st.session_state.prix_db[cat][art] = new_p

# --- 3. ÉDITION DEVIS / FACTURE ---
elif menu == "Édition Devis/Facture":
    st.title("📄 Facturation")
    
    col1, col2 = st.columns(2)
    with col1:
        type_doc = st.radio("Type de document", ["DEVIS", "FACTURE"])
        num_doc = st.text_input("Numéro du document", "2023-001")
    with col2:
        nom_client = st.text_input("Nom du Client", "M. Dupont")
        adresse_client = st.text_area("Adresse Client", "123 Rue de la Paix, 75000 Paris")

    if st.session_state.panier:
        st.markdown("---")
        st.markdown(f"### {type_doc} n° {num_doc}")
        
        # Affichage Pro
        df = pd.DataFrame(st.session_state.panier)
        df['Total HT'] = df['Qté'] * df['PU']
        st.table(df)
        
        total_ht = df['Total HT'].sum()
        tva_taux = st.selectbox("Taux de TVA", [0.055, 0.10, 0.20], index=2)
        total_tva = total_ht * tva_taux
        total_ttc = total_ht + total_tva
        
        st.markdown(f"""
        **Total HT :** {total_ht:.2f} €  
        **TVA ({tva_taux*100}%) :** {total_tva:.2f} €  
        ## TOTAL TTC : {total_ttc:.2f} €
        """)
        
        st.markdown("---")
        st.info("💡 **Mentions légales :** Paiement sous 30 jours. Auto-entrepreneur (TVA non applicable le cas échéant) ou SIRET : 123 456 789 00012")
        
        # Boutons d'export
        if st.button("✅ Valider et Générer le document"):
            st.success(f"{type_doc} généré avec succès !")
            # Ici on télécharge un CSV mais on pourrait générer un PDF
            st.download_button("Télécharger au format Excel/CSV", df.to_csv().encode('utf-8'), f"{type_doc}_{num_doc}.csv")
    else:
        st.warning("Le panier est vide. Ajoutez du matériel dans le Calculateur.")
