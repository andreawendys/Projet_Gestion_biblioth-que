# Guide d'Architecture Technique
Ce document constitue un référentiel évolutif visant à fournir une vision claire et synthétique de l’architecture du système et de son modèle de données. Il a pour objectif de faciliter la compréhension globale du projet ainsi que la navigation dans la base de code .

# 1. Structure du Projet :
L'arborescence suit une architecture modulaire pour séparer les configurations, les modèles de données et les scripts d'exécution :

Projet_Gestion_bibliothèque/
├── cli/                        # Interface en ligne de commande (Click)
│   └── main.py                 # Point d'entrée principal du CLI
├── config/                     # Paramètres de connexion
│   ├── database.py             # Classe CassandraConnection pour le Singleton de session
│   └── __init__.py             # Initialisation du module config
├── diagrammes/                 # Images du schéma des tables et des flux de données
├── models/                     # Logique métier et accès aux données (Repositories)
│   ├── book.py                 # Repository pour la gestion des tables de livres
│   ├── user.py                 # Repository pour la gestion des utilisateurs
│   └── borrow.py               # Repository pour les emprunts, retours et batchs
├── schema/                     # Définition de la base de données
│   └── schema.cql              # Script SQL-like pour la création du Keyspace et des tables
├── scripts/                    # Utilitaires de maintenance et tests
│   ├── init_schema.py          # Script d'automatisation de la création du schéma
│   ├── generate_data.py        # Peuplement de la base avec Faker (50 users / 100 books)
│   └── benchmark.py            # Script de mesure des performances d'écriture
├── tests/                      # Tests automatisés
│   └── test_repository.py      # Tests unitaires avec Pytest 
├── app_web.py                  # Dashboard interactif Streamlit 
├── ARCHITECTURE.md             # Referentiel explicatif du modèle de données
├── docker-compose.yml          # Orchestration du cluster Cassandra (3 nœuds)
├── QUERIES.md                  # Liste des query patterns et justifications
├── README.md                   # Guide d'installation et d'utilisation
└── requirements.txt            # Liste des dépendances Python (Cassandra-driver, Streamlit, etc.)


# 2. Modélisation et Infrastructure du Cluster:
Pour ce projet, nous avons appliqué les principes fondamentaux du NoSQL Cassandra :

    -Dénormalisation :
Les données sont volontairement dupliquées dans plusieurs tables afin d’éviter les jointures, coûteuses dans un environnement distribué. Ainsi, les informations des livres sont répliquées dans des tables dédiées comme books_by_category et books_by_author, optimisées pour les besoins applicatifs.

    -Query-First Design : 
Chaque table correspond à une fonctionnalité précise du CLI. Le modèle de données a été conçu à partir des requêtes, de sorte que chaque table réponde directement à une question spécifique (par exemple : « Quels livres sont disponibles dans cette catégorie ? ») en accédant efficacement à la partition concernée.

    -Haute Disponibilité : 
Le système repose sur un cluster Cassandra distribué de trois nœuds, orchestré via Docker Compose. Grâce à l’utilisation de trois conteneurs (cassandra1, cassandra2, cassandra3), le service reste opérationnel même en cas de défaillance d’un nœud. Un Replication Factor de 3 a été configuré, garantissant que chaque donnée (livres, utilisateurs, emprunts) est répliquée sur l’ensemble des nœuds afin d’assurer tolérance aux pannes et sécurité des données.

NB : Pour les opérations complexes telles que l'emprunt d'un livre, nous utilisons des BatchStatements pour garantir que toutes les tables liées sont mises à jour simultanément, évitant ainsi toute incohérence.

# 3. Organisation clé du projet
L'organisation de notre base de code suit une séparation stricte des responsabilités pour garantir la maintenabilité et l'évolution du système :

-L'Interface (CLI & Web) : Située dans cli/ et app_web.py, ces interfaces constituent les uniques points d'interaction entre l'utilisateur et le système (logique métier).

-Le Cœur Logique (Models/Repositories) : Le dossier models/ contient l'intelligence du système. C'est ici que les requêtes sont préparées et que la cohérence des données est gérée.

-La Configuration & Le Schéma : Les dossiers config/ et schema/ définissent comment l'application se connecte au cluster et comment la base de données est structurée physiquement.

-Qualité & Performance : Les dossiers tests/ et scripts/ assurent que chaque modification est validée par des tests unitaires et des benchmarks de performance.
