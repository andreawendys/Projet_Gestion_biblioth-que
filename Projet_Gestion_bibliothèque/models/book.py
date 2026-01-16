import uuid
from loguru import logger

class BookRepository:
    def __init__(self, session):
        self.session = session
        self._prepare_queries()

    def _prepare_queries(self):
        """Préparation des requêtes pour optimiser les performances de l'interface"""
        # Pour l'onglet "Catalogue Complet"
        self.prep_get_all = self.session.prepare("""
            SELECT isbn, title, author, available_copies, category FROM books_by_id
        """)
        
        # Pour la recherche par ISBN (Nécessaire pour l'emprunt)
        self.prep_get_by_isbn = self.session.prepare("""
            SELECT isbn, title, author, available_copies FROM books_by_id WHERE isbn = ?
        """)
        
        # Pour le filtrage par catégorie
        self.prep_get_by_cat = self.session.prepare("""
            SELECT isbn, title, author, available_copies FROM books_by_category WHERE category = ?
        """)

    def get_all_books(self):
        """Récupère tous les livres pour l'affichage initial du Dashboard"""
        try:
            return self.session.execute(self.prep_get_all)
        except Exception as e:
            logger.error(f"❌ Erreur lecture catalogue: {e}")
            return []

    def get_book_by_isbn(self, isbn):
        """Récupère un livre spécifique pour obtenir son titre avant l'emprunt"""
        try:
            return self.session.execute(self.prep_get_by_isbn, [isbn]).one()
        except Exception as e:
            logger.error(f"❌ Erreur recherche ISBN {isbn}: {e}")
            return None

    def get_books_by_category(self, category):
        """Recherche filtrée par catégorie"""
        try:
            return self.session.execute(self.prep_get_by_cat, [category])
        except Exception as e:
            logger.error(f"❌ Erreur recherche catégorie {category}: {e}")
            return []