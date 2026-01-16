import uuid
from datetime import datetime
from loguru import logger

class User:
    def __init__(self, user_id, first_name, last_name, email, registration_date, total_borrows=0, active_borrows=0):
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.registration_date = registration_date
        self.total_borrows = total_borrows
        self.active_borrows = active_borrows

class UserRepository:
    def __init__(self, session):
        self.session = session
        # ✅ Préparation des requêtes au démarrage pour la performance
        self._prepare_queries()

    def _prepare_queries(self):
        """Préparation des statements pour la sécurité et la vitesse"""
        # Insertion
        self.prep_insert_user = self.session.prepare("""
            INSERT INTO users_by_id (user_id, email, first_name, last_name, registration_date)
            VALUES (?, ?, ?, ?, ?)
        """)
        
        # Lecture unitaire
        self.prep_get_user = self.session.prepare("""
            SELECT * FROM users_by_id WHERE user_id = ?
        """)

        # Lecture de tous les membres (Table demandée par Streamlit)
        self.prep_get_all = self.session.prepare("""
            SELECT user_id, first_name, last_name, email, registration_date FROM users_by_id
        """)

    def create_user(self, email, first_name, last_name):
        """Inscrire un utilisateur avec un UUID automatique"""
        user_id = uuid.uuid4()
        now = datetime.now()
        
        try:
            self.session.execute(self.prep_insert_user, (
                user_id, email, first_name, last_name, now
            ))
            logger.success(f"✅ Utilisateur créé : {first_name} {last_name} ({user_id})")
            return user_id
        except Exception as e:
            logger.error(f"❌ Erreur création user: {e}")
            return None

    def get_user(self, user_id):
        """
        Récupère un objet User complet.
        Indispensable pour récupérer le nom/prénom lors d'un emprunt.
        """
        try:
            # Conversion en UUID si l'ID vient de Streamlit sous forme de texte
            u_id = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
            
            row = self.session.execute(self.prep_get_user, [u_id]).one()
            if row:
                return User(
                    user_id=row.user_id, 
                    first_name=row.first_name, 
                    last_name=row.last_name,
                    email=row.email, 
                    registration_date=row.registration_date,
                    total_borrows=getattr(row, 'total_borrows', 0), 
                    active_borrows=getattr(row, 'active_borrows', 0)
                )
            return None
        except Exception as e:
            logger.error(f"❌ Erreur récupération user {user_id}: {e}")
            return None

    def get_all_users(self):
        """Récupérer la liste complète pour l'affichage du Dashboard"""
        try:
            return self.session.execute(self.prep_get_all)
        except Exception as e:
            logger.error(f"❌ Erreur récupération liste users: {e}")
            return []