import uuid
from datetime import datetime
from loguru import logger
from cassandra.query import BatchStatement

class BorrowRepository:
    def __init__(self, session):
        self.session = session
        self._prepare_queries()

    def _prepare_queries(self):
        """Préparation des requêtes CQL pour optimiser les performances"""
        
        # Lecture du stock actuel
        self.prep_get_stock = self.session.prepare("""
            SELECT available_copies FROM books_by_id WHERE isbn = ?
        """)

        # Insertion emprunt (Dénormalisation du titre)
        self.prep_insert_user = self.session.prepare("""
            INSERT INTO borrows_by_user (user_id, borrow_date, isbn, book_title, status) 
            VALUES (?, ?, ?, ?, 'ACTIVE')
        """)
        
        # Insertion emprunt (Dénormalisation du nom d'utilisateur)
        self.prep_insert_book = self.session.prepare("""
            INSERT INTO borrows_by_book (isbn, borrow_date, user_id, user_name) 
            VALUES (?, ?, ?, ?)
        """)
        
        # Mise à jour du stock 
        self.prep_update_stock = self.session.prepare("""
            UPDATE books_by_id SET available_copies = ? WHERE isbn = ?
        """)

        # Retour livre (Mise à jour du statut)
        self.prep_return_user = self.session.prepare("""
            UPDATE borrows_by_user SET status = 'RETURNED' 
            WHERE user_id = ? AND borrow_date = ?
        """)

        # Lecture historique par utilisateur
        self.prep_get_history = self.session.prepare("""
            SELECT * FROM borrows_by_user WHERE user_id = ?
        """)

    def borrow_book(self, user_id, user_name, isbn, book_title):
        """Exécute l'emprunt en Batch pour garantir l'atomicité sur 3 tables."""
        try:
            u_id = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
            
            row = self.session.execute(self.prep_get_stock, [isbn]).one()
            if not row or row.available_copies <= 0:
                logger.error(f"❌ Stock insuffisant pour l'ISBN {isbn}")
                return False

            new_stock = row.available_copies - 1
            now = datetime.now()

            batch = BatchStatement()
            batch.add(self.prep_insert_user, (u_id, now, isbn, book_title))
            batch.add(self.prep_insert_book, (isbn, now, u_id, user_name))
            batch.add(self.prep_update_stock, (new_stock, isbn))
            
            self.session.execute(batch)
            logger.success(f"✅ Emprunt réussi pour : {book_title}")
            return True

        except Exception as e:
            logger.error(f"❌ Erreur borrow_book: {e}")
            return False

    def return_book(self, user_id, isbn, borrow_date):
        """Gère le retour et incrémente le stock"""
        try:
            u_id = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
            if isinstance(borrow_date, str):
                b_date = datetime.strptime(borrow_date, '%Y-%m-%d %H:%M:%S')
            else:
                b_date = borrow_date

            row = self.session.execute(self.prep_get_stock, [isbn]).one()
            new_stock = (row.available_copies if row else 0) + 1

            batch = BatchStatement()
            batch.add(self.prep_return_user, (u_id, b_date))
            batch.add(self.prep_update_stock, (new_stock, isbn))
            
            self.session.execute(batch)
            logger.success(f"✅ Retour réussi pour l'ISBN {isbn}")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur return_book: {e}")
            return False

    # ✅ CORRECTION : Ajout du nom attendu par Streamlit
    def get_user_borrows(self, user_id):
        """
        Méthode appelée par l'onglet Historique de Streamlit.
        Résout l'erreur AttributeError: 'BorrowRepository' object has no attribute 'get_user_borrows'
        """
        try:
            u_id = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
            return self.session.execute(self.prep_get_history, [u_id])
        except Exception as e:
            logger.error(f"❌ Erreur lecture historique pour {user_id}: {e}")
            return []

    # Gardé par compatibilité si d'autres parties du code l'utilisent
    def get_all_borrows(self, user_id):
        return self.get_user_borrows(user_id)