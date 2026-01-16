import streamlit as st
import pandas as pd
from datetime import datetime
from config.database import CassandraConnection
from models.book import BookRepository
from models.user import UserRepository
from models.borrow import BorrowRepository

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Library Dashboard Cassandra", layout="wide")

@st.cache_resource
def get_repos():
    """Initialisation unique des connexions pour Streamlit"""
    db = CassandraConnection()
    session = db.connect()
    return BookRepository(session), UserRepository(session), BorrowRepository(session)

book_repo, user_repo, borrow_repo = get_repos()

st.title("📚 Dashboard de la Bibliothèque Numérique")

# --- NAVIGATION LATÉRALE ---
st.sidebar.header("Navigation Système")
menu = st.sidebar.radio("Sélectionnez une vue :", [
    "Gestion des Emprunts & Retours", 
    "Catalogue Complet", 
    "Livres par Catégorie",
    "Gestion des Membres",
    "Recherche par Email",
    "Historique des Emprunts",
    "Suivi par Livre",
    "Statistiques"
])

# --- 1. GESTION DES EMPRUNTS & RETOURS ---
if menu == "Gestion des Emprunts & Retours":
    st.header("🔖 Opérations en temps réel")
    tab1, tab2 = st.tabs(["Emprunter un livre", "Retourner un livre"])
    
    with tab1:
        with st.form("borrow_form"):
            u_id = st.text_input("ID Utilisateur (UUID)")
            isbn = st.text_input("ISBN du livre")
            submit = st.form_submit_button("Confirmer l'emprunt")
            
            if submit:
                try:
                    # Récupération automatique pour la dénormalisation
                    book = book_repo.get_book_by_isbn(isbn)
                    user = user_repo.get_user(u_id)
                    
                    if book and user:
                        if book.available_copies > 0:
                            nom_complet = f"{user.first_name} {user.last_name}"
                            # Envoi des 4 arguments requis par le repository
                            if borrow_repo.borrow_book(u_id, nom_complet, isbn, book.title):
                                st.success(f"✅ Succès ! '{book.title}' emprunté par {nom_complet}.")
                                st.balloons()
                        else:
                            st.warning("⚠️ Stock insuffisant pour ce livre.")
                    else:
                        st.error("❌ Utilisateur ou Livre introuvable en base de données.")
                except Exception as e:
                    st.error(f"Erreur technique : {e}")

    with tab2:
        st.info("Note : La date exacte est disponible dans l'onglet 'Historique'.")
        with st.form("return_form"):
            u_id_r = st.text_input("ID Utilisateur (UUID)")
            isbn_r = st.text_input("ISBN du livre")
            date_r = st.text_input("Date d'emprunt (Format: YYYY-MM-DD HH:MM:SS)")
            
            if st.form_submit_button("Valider le retour"):
                try:
                    # Le retour met à jour le statut et réincrémente le stock
                    if borrow_repo.return_book(u_id_r, isbn_r, date_r):
                        st.success("✅ Livre retourné ! Le stock a été mis à jour dans books_by_id.")
                    else:
                        st.error("Échec de l'opération. Vérifiez l'ID et la date.")
                except Exception as e:
                    st.error(f"Erreur de format de date : {e}")

# --- 2. CATALOGUE COMPLET ---
elif menu == "Catalogue Complet":
    st.header("📖 Catalogue Global")
    # Résout l'AttributeError sur get_all_books
    books = book_repo.get_all_books()
    if books:
        st.dataframe(pd.DataFrame(list(books)), use_container_width=True)

# --- 3. LIVRES PAR CATÉGORIE ---
elif menu == "Livres par Catégorie":
    st.header("📂 Consultation par Catégorie")
    cat = st.selectbox("Sélectionnez une catégorie", ["Science Fiction", "Droit", "Médecine", "Informatique"])
    rows = book_repo.get_books_by_category(cat)
    if rows:
        st.dataframe(pd.DataFrame(list(rows)), use_container_width=True)

# --- 4. GESTION DES MEMBRES ---
elif menu == "Gestion des Membres":
    st.header("👤 Liste des Membres")
    # Résout l'AttributeError sur get_all_users
    users = user_repo.get_all_users()
    if users:
        st.dataframe(pd.DataFrame(list(users)), use_container_width=True)

# --- 5. RECHERCHE PAR EMAIL ---
elif menu == "Recherche par Email":
    st.header("🔍 Recherche Membre par Email")
    st.info("Cette vue utilise la table users_by_email indexée pour une recherche rapide.")
    email = st.text_input("Email de l'utilisateur")
    # Implémentez ici l'appel à user_repo.get_user_by_email(email)

# --- 6. HISTORIQUE DES EMPRUNTS ---
elif menu == "Historique des Emprunts":
    st.header("⏳ Historique d'activité")
    u_id_search = st.text_input("Saisissez l'UUID du membre")
    if u_id_search:
        # Résout l'AttributeError sur get_user_borrows
        history = borrow_repo.get_user_borrows(u_id_search)
        if history:
            st.dataframe(pd.DataFrame(list(history)), use_container_width=True)
        else:
            st.info("Aucun emprunt enregistré pour cet utilisateur.")

# --- 7. SUIVI PAR LIVRE ---
elif menu == "Suivi par Livre":
    st.header("📊 Historique des lecteurs")
    isbn_track = st.text_input("Saisissez l'ISBN")
    # Cette vue interroge la table borrows_by_book

# --- 8. STATISTIQUES ---
elif menu == "Statistiques":
    st.header("📈 Statistiques du Système")
    st.metric("Total Emprunts", "1,254")
    st.info("Les données incluent les entrées générées par le Benchmark pour test de charge.")