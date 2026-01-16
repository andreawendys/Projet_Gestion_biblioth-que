import sys
import os
from datetime import datetime

# Configuration du chemin pour trouver les modules locaux
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

import click
from uuid import UUID
from tabulate import tabulate
from config.database import CassandraConnection
from models.book import BookRepository, Book
from models.user import UserRepository
from models.borrow import BorrowRepository

# Initialisation de la connexion et des repositories
db = CassandraConnection()
session = db.connect()

book_repo = BookRepository(session)
user_repo = UserRepository(session)
borrow_repo = BorrowRepository(session)

@click.group()
def cli():
    """📚 Système de Gestion de Bibliothèque (Architecture Distribuée)"""
    pass

# ================== GESTION DES LIVRES ==================

@cli.group()
def books():
    """Opérations sur les livres"""
    pass

@books.command()
@click.option('--isbn', prompt='ISBN', help='ISBN du livre')
@click.option('--title', prompt='Titre', help='Titre du livre')
@click.option('--author', prompt='Auteur', help='Auteur')
@click.option('--category', prompt='Catégorie', help='Catégorie')
@click.option('--publisher', prompt='Éditeur', help='Éditeur')
@click.option('--year', prompt='Année', type=int, help='Année de publication')
@click.option('--copies', prompt='Copies', type=int, default=1)
def add(isbn, title, author, category, publisher, year, copies):
    """Ajouter un livre (Mise à jour multi-tables via BATCH)"""
    book = Book(
        isbn=isbn, title=title, author=author, category=category,
        publisher=publisher, publication_year=year,
        total_copies=copies, available_copies=copies
    )
    if book_repo.add_book(book):
        click.echo(click.style(f"✅ Livre ajouté dans toutes les vues : {title}", fg='green'))
    else:
        click.echo(click.style("❌ Échec de l'ajout", fg='red'))

@books.command()
@click.option('--isbn', prompt='ISBN')
def search(isbn):
    """Rechercher par ISBN (books_by_id)"""
    book = book_repo.get_book_by_isbn(isbn)
    if book:
        data = [
            ["ISBN", book.isbn], ["Titre", book.title],
            ["Auteur", book.author], ["Catégorie", book.category],
            ["Disponibles", book.available_copies]
        ]
        click.echo("\n" + tabulate(data, tablefmt="grid"))
    else:
        click.echo(click.style("❌ Livre introuvable", fg='red'))

@books.command()
@click.option('--category', prompt='Catégorie')
def list_by_category(category):
    """Lister par catégorie (books_by_category)"""
    rows = book_repo.get_books_by_category(category)
    results = list(rows)
    if results:
        data = [[r.isbn, r.title, r.author, r.available_copies] for r in results]
        headers = ['ISBN', 'Titre', 'Auteur', 'Disponibles']
        click.echo("\n" + tabulate(data, headers=headers, tablefmt="grid"))
    else:
        click.echo(click.style("Aucun livre dans cette catégorie", fg='yellow'))

# ================== GESTION DES UTILISATEURS ==================

@cli.group()
def users():
    """Opérations sur les utilisateurs"""
    pass

@users.command()
@click.option('--email', prompt='Email')
@click.option('--first-name', prompt='Prénom')
@click.option('--last-name', prompt='Nom')
def register(email, first_name, last_name):
    """Inscrire un utilisateur"""
    user_id = user_repo.create_user(email, first_name, last_name)
    if user_id:
        click.echo(click.style(f"✅ Utilisateur créé : {user_id}", fg='green'))

@users.command()
@click.option('--user-id', prompt='User ID')
def profile(user_id):
    """Voir le profil utilisateur"""
    try:
        user = user_repo.get_user(UUID(user_id))
        if user:
            data = [
                ["ID", user.user_id], ["Nom", f"{user.first_name} {user.last_name}"],
                ["Email", user.email], ["Date Inscription", user.registration_date],
                ["Emprunts Totaux", user.total_borrows], ["Actifs", user.active_borrows]
            ]
            click.echo("\n" + tabulate(data, tablefmt="grid"))
        else:
            click.echo(click.style("❌ Utilisateur introuvable", fg='red'))
    except ValueError:
        click.echo(click.style("❌ Format UUID invalide", fg='red'))

# ================== GESTION DES EMPRUNTS ==================

@cli.group()
def borrows():
    """Logique d'emprunt et de retour"""
    pass

@borrows.command()
@click.option('--user-id', prompt='User ID')
@click.option('--isbn', prompt='ISBN')
def borrow(user_id, isbn):
    """Emprunter un livre (Utilise borrow_book)"""
    try:
        u_id = UUID(user_id)
        user = user_repo.get_user(u_id)
        book = book_repo.get_book_by_isbn(isbn)

        if not user or not book:
            click.echo(click.style("❌ Utilisateur ou livre inexistant", fg='red'))
            return

        user_name = f"{user.first_name} {user.last_name}"
        
        if borrow_repo.borrow_book(u_id, user_name, isbn, book.title):
            click.echo(click.style(f"✅ Emprunt réussi : {book.title}", fg='green'))
        else:
            click.echo(click.style("❌ Erreur lors de l'emprunt", fg='red'))
    except ValueError:
        click.echo(click.style("❌ Format UUID invalide", fg='red'))

@borrows.command(name="return")
@click.option('--user-id', prompt='User ID')
@click.option('--isbn', prompt='ISBN')
@click.option('--date', prompt='Date emprunt (YYYY-MM-DD HH:MM:SS.mmmmmm)')
def return_book_cmd(user_id, isbn, date):
    """Retourner un livre (Utilise return_book)"""
    try:
        u_id = UUID(user_id)
        # Gestion du format de date précis de Cassandra pour la Primary Key
        try:
            b_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f')
        except ValueError:
            b_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')

        if borrow_repo.return_book(u_id, isbn, b_date):
            click.echo(click.style("✅ Livre retourné avec succès", fg='green'))
        else:
            click.echo(click.style("❌ Échec du retour", fg='red'))
    except Exception as e:
        click.echo(click.style(f"❌ Erreur : {e}", fg='red'))

@borrows.command()
@click.option('--user-id', prompt='User ID')
def history(user_id):
    """Consulter l'historique des emprunts"""
    try:
        rows = borrow_repo.get_user_borrows(UUID(user_id))
        borrows_list = list(rows)
        if borrows_list:
            data = [[r.isbn, r.book_title, r.borrow_date, r.status] for r in borrows_list]
            headers = ['ISBN', 'Titre', 'Date', 'Statut']
            click.echo("\n" + tabulate(data, headers=headers, tablefmt="grid"))
        else:
            click.echo(click.style("Aucun emprunt trouvé", fg='yellow'))
    except ValueError:
        click.echo(click.style("❌ Format UUID invalide", fg='red'))

if __name__ == '__main__':
    try:
        cli()
    finally:
        db.close()