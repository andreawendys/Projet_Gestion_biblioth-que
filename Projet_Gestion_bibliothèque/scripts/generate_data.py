import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from faker import Faker
from uuid import uuid4
from random import randint, choice
from models.book import BookRepository, Book
from models.user import UserRepository
from config.database import CassandraConnection
from loguru import logger

fake = Faker('fr_FR')

def generate_books(book_repo, count=100):
    """Générer des livres aléatoires"""
    categories = ['Science Fiction', 'Fantasy', 'Thriller', 'Romance',
                  'Histoire', 'Science', 'Biographie', 'Philosophie']

    publishers = ['Gallimard', 'Flammarion', 'Hachette', 'Albin Michel', 'Seuil']

    logger.info(f"🎲 Génération de {count} livres...")

    for i in range(count):
        isbn = f"978-{randint(0,9)}-{randint(100000,999999)}-{randint(10,99)}-{randint(0,9)}"

        book = Book(
            isbn=isbn,
            title=fake.sentence(nb_words=4)[:-1],  # Titre aléatoire
            author=fake.name(),
            category=choice(categories),
            publisher=choice(publishers),
            publication_year=randint(1950, 2024),
            total_copies=randint(1, 10),
            available_copies=randint(0, 10),
            description=fake.text(max_nb_chars=200)
        )

        book_repo.add_book(book)

        if (i + 1) % 10 == 0:
            logger.info(f"  ✅ {i+1}/{count} livres créés")

    logger.success(f"✅ {count} livres générés!")

def generate_users(user_repo, count=50):
    """Générer des utilisateurs aléatoires"""
    logger.info(f"👥 Génération de {count} utilisateurs...")

    user_ids = []

    for i in range(count):
        email = fake.email()
        first_name = fake.first_name()
        last_name = fake.last_name()
        phone = fake.phone_number()
        address = fake.address().replace('\n', ', ')

        user_id = user_repo.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            address=address
        )

        user_ids.append(user_id)

        if (i + 1) % 10 == 0:
            logger.info(f"  ✅ {i+1}/{count} utilisateurs créés")

    logger.success(f"✅ {count} utilisateurs générés!")
    return user_ids

if __name__ == "__main__":
    db = CassandraConnection()
    session = db.connect()

    
    session.set_keyspace('library_system')

    book_repo = BookRepository(session)
    user_repo = UserRepository(session)

    # Générer des données
    generate_books(book_repo, count=100)
    user_ids = generate_users(user_repo, count=50)

    logger.success("🎉 Base de données peuplée!")
    db.close()