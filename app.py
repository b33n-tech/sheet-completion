import streamlit as st
import pandas as pd
from faker import Faker
import random
from datetime import datetime, timedelta
import io
import re

# Initialiser Faker avec locale française
fake = Faker('fr_FR')

def detect_column_type(col_name, sample_values):
    """Détecte le type de données d'une colonne basé sur son nom et ses valeurs"""
    col_lower = col_name.lower()
    
    # Nettoyer les valeurs d'exemple
    clean_values = [str(v).strip() for v in sample_values if pd.notna(v) and str(v).strip()]
    
    if not clean_values:
        return 'text'
    
    # Détection par nom de colonne
    if any(keyword in col_lower for keyword in ['prénom', 'prenom', 'firstname', 'first_name']):
        return 'prenom'
    if any(keyword in col_lower for keyword in ['nom', 'lastname', 'last_name', 'surname']) and 'prénom' not in col_lower:
        return 'nom'
    if any(keyword in col_lower for keyword in ['email', 'e-mail', 'mail', 'courriel']):
        return 'email'
    if any(keyword in col_lower for keyword in ['téléphone', 'telephone', 'phone', 'tel', 'mobile', 'gsm']):
        return 'telephone'
    if any(keyword in col_lower for keyword in ['ville', 'city', 'commune']):
        return 'ville'
    if any(keyword in col_lower for keyword in ['adresse', 'address', 'rue', 'street']):
        return 'adresse'
    if any(keyword in col_lower for keyword in ['code postal', 'cp', 'zip', 'postal']):
        return 'code_postal'
    if any(keyword in col_lower for keyword in ['pays', 'country']):
        return 'pays'
    if any(keyword in col_lower for keyword in ['entreprise', 'company', 'société', 'societe', 'organisation']):
        return 'entreprise'
    if any(keyword in col_lower for keyword in ['poste', 'job', 'profession', 'métier', 'metier']):
        return 'profession'
    if any(keyword in col_lower for keyword in ['date', 'jour']):
        return 'date'
    if any(keyword in col_lower for keyword in ['année', 'annee', 'year']):
        return 'annee'
    if any(keyword in col_lower for keyword in ['age', 'âge']):
        return 'age'
    if any(keyword in col_lower for keyword in ['prix', 'price', 'montant', 'amount', 'cout', 'coût']):
        return 'prix'
    if any(keyword in col_lower for keyword in ['description', 'commentaire', 'comment', 'note', 'remarque']):
        return 'paragraphe'
    if any(keyword in col_lower for keyword in ['url', 'site', 'website', 'lien', 'link']):
        return 'url'
    if any(keyword in col_lower for keyword in ['sexe', 'genre', 'gender', 'sex']):
        return 'sexe'
    if any(keyword in col_lower for keyword in ['statut', 'status', 'état', 'etat']):
        return 'statut'
    
    # Analyse des valeurs d'exemple
    sample = clean_values[0]
    
    # Vérifier si c'est une date
    try:
        pd.to_datetime(sample)
        return 'date'
    except:
        pass
    
    # Vérifier si c'est un nombre
    try:
        float(sample)
        if '.' in sample or ',' in sample:
            return 'decimal'
        else:
            return 'entier'
    except:
        pass
    
    # Vérifier email
    if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', sample):
        return 'email'
    
    # Vérifier téléphone
    if re.match(r'^[\d\s\.\-\(\)\+]+$', sample) and len(sample.replace(' ', '')) >= 8:
        return 'telephone'
    
    # Par défaut selon la longueur
    if len(sample) > 50:
        return 'paragraphe'
    
    return 'text'


def generate_value(column_type):
    """Génère une valeur selon le type détecté"""
    generators = {
        'prenom': lambda: fake.first_name(),
        'nom': lambda: fake.last_name(),
        'email': lambda: fake.email(),
        'telephone': lambda: fake.phone_number(),
        'ville': lambda: fake.city(),
        'adresse': lambda: fake.street_address(),
        'code_postal': lambda: fake.postcode(),
        'pays': lambda: fake.country(),
        'entreprise': lambda: fake.company(),
        'profession': lambda: fake.job(),
        'date': lambda: fake.date_between(start_date='-5y', end_date='today').strftime('%Y-%m-%d'),
        'annee': lambda: random.randint(2000, 2025),
        'age': lambda: random.randint(18, 75),
        'prix': lambda: round(random.uniform(10, 5000), 2),
        'decimal': lambda: round(random.uniform(1, 1000), 2),
        'entier': lambda: random.randint(1, 10000),
        'paragraphe': lambda: fake.paragraph(nb_sentences=random.randint(3, 6)),
        'text': lambda: fake.sentence(nb_words=random.randint(3, 8)).rstrip('.'),
        'url': lambda: fake.url(),
        'sexe': lambda: random.choice(['M', 'F', 'Homme', 'Femme'][:2] if random.random() > 0.5 else ['M', 'F']),
        'statut': lambda: random.choice(['Actif', 'Inactif', 'En attente', 'Validé', 'Refusé']),
    }
    
    return generators.get(column_type, generators['text'])()


def main():
    st.set_page_config(page_title="Générateur de données Excel", page_icon="📊", layout="wide")
    
    st.title("📊 Générateur intelligent de données Excel")
    st.markdown("""
    **Mode d'emploi :**
    1. Uploadez votre fichier Excel avec au moins **2 lignes d'exemple** remplies
    2. L'outil détecte automatiquement le type de chaque colonne
    3. Choisissez le nombre de lignes à générer
    4. Téléchargez votre fichier complété !
    """)
    
    uploaded_file = st.file_uploader("📁 Uploadez votre fichier Excel (.xlsx)", type=['xlsx'])
    
    if uploaded_file:
        # Lire le fichier
        df = pd.read_excel(uploaded_file)
        
        st.success(f"✅ Fichier chargé : {len(df)} lignes, {len(df.columns)} colonnes")
        
        # Afficher les données d'origine
        with st.expander("👀 Aperçu des données d'origine"):
            st.dataframe(df.head(10))
        
        # Analyse des colonnes
        st.subheader("🔍 Analyse et validation des colonnes")
        st.info("👉 Vérifiez les types détectés et corrigez-les si nécessaire")
        
        # Liste de tous les types disponibles
        available_types = [
            'prenom', 'nom', 'email', 'telephone', 'ville', 'adresse', 
            'code_postal', 'pays', 'entreprise', 'profession', 'date', 
            'annee', 'age', 'prix', 'decimal', 'entier', 'paragraphe', 
            'text', 'url', 'sexe', 'statut'
        ]
        
        column_types = {}
        
        # Initialiser session state pour conserver les choix
        if 'column_types_modified' not in st.session_state:
            st.session_state.column_types_modified = {}
        
        for col in df.columns:
            # Prendre les 2 premières valeurs non-nulles
            sample_values = df[col].dropna().head(2).tolist()
            detected_type = detect_column_type(col, sample_values)
            
            # Utiliser le type modifié si existe, sinon le type détecté
            if col in st.session_state.column_types_modified:
                default_type = st.session_state.column_types_modified[col]
            else:
                default_type = detected_type
            
            col1, col2, col3 = st.columns([3, 2, 3])
            
            with col1:
                st.text(f"📋 {col}")
            
            with col2:
                selected_type = st.selectbox(
                    "Type",
                    options=available_types,
                    index=available_types.index(default_type),
                    key=f"type_{col}",
                    label_visibility="collapsed"
                )
                column_types[col] = selected_type
                st.session_state.column_types_modified[col] = selected_type
            
            with col3:
                example_text = str(sample_values[0])[:50] if sample_values else 'N/A'
                st.text(f"Ex: {example_text}")
        
        st.divider()
        
        # Options de génération
        st.subheader("⚙️ Paramètres de génération")
        
        col1, col2 = st.columns(2)
        
        with col1:
            nb_lignes = st.selectbox(
                "Nombre de lignes à générer",
                options=[100, 500, 1000, 2000, 5000, 10000],
                index=0
            )
        
        with col2:
            keep_originals = st.checkbox("Conserver les lignes d'origine", value=True)
        
        # Bouton de génération
        if st.button("🚀 Générer les données", type="primary", use_container_width=True):
            with st.spinner(f"Génération de {nb_lignes} lignes en cours..."):
                # Créer le nouveau dataframe
                new_rows = []
                
                for _ in range(nb_lignes):
                    new_row = {}
                    for col in df.columns:
                        new_row[col] = generate_value(column_types[col])
                    new_rows.append(new_row)
                
                df_generated = pd.DataFrame(new_rows)
                
                # Combiner avec les données d'origine si demandé
                if keep_originals:
                    df_final = pd.concat([df, df_generated], ignore_index=True)
                else:
                    df_final = df_generated
                
                st.success(f"✅ {len(df_final)} lignes générées avec succès !")
                
                # Aperçu
                with st.expander("👀 Aperçu des données générées (10 premières lignes)"):
                    st.dataframe(df_final.head(10))
                
                # Export
                st.subheader("💾 Téléchargement")
                
                # Créer le fichier Excel en mémoire
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df_final.to_excel(writer, index=False, sheet_name='Données')
                output.seek(0)
                
                st.download_button(
                    label="📥 Télécharger le fichier Excel complété",
                    data=output,
                    file_name=f"donnees_generees_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
    
    # Informations supplémentaires
    with st.sidebar:
        st.header("ℹ️ Types supportés")
        st.markdown("""
        - **Identité** : Nom, Prénom
        - **Contact** : Email, Téléphone, Adresse
        - **Localisation** : Ville, Code postal, Pays
        - **Professionnel** : Entreprise, Profession
        - **Temporel** : Date, Année, Age
        - **Numérique** : Prix, Décimal, Entier
        - **Texte** : Paragraphe, Texte court
        - **Autre** : URL, Sexe, Statut
        """)
        
        st.header("💡 Astuce")
        st.info("Remplissez au moins 2 lignes d'exemple pour une meilleure détection automatique !")


if __name__ == "__main__":
    main()
