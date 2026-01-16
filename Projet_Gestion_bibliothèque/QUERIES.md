 # Création des requetes : Logique 1 query pattern = 1 table

Ce document décrit les patterns de requêtes utilisés par l’application ainsi que la justification du schéma Cassandra associé.Afin de respecter les consignes, nous avons crées 8 tables présentes ci dessous: 

1. **Recherche d’un livre par ISBN** :
```bash
SELECT * FROM books_by_id WHERE isbn = ?;
```
Table utilisée : books_by_id
Clé : Partition key : isbn

**Justification**
Permet une recherche directe par l'identifiant unique ISBN permettant un accès très rapide (O(1)), adaptée à un cas d’usage fréquent comme la consultation d’un livre, sans besoin de jointures.

2. **Navigation des livres par catégorie** :
```bash
SELECT * FROM books_by_category WHERE category = ?;
```
Table utilisée : books_by_category
Clé : Partition key : category
      Clustering key : isbn

**Justification**
Permet de lister facilement tous les livres d’une même catégorie, avec des données regroupées et triées naturellement par ISBN, 

3. **Recherche de livres par auteur** :
```bash
SELECT * FROM books_by_author WHERE author = ?;
```
Table utilisée : books_by_author
Clé : Partition key : author
      Clustering key : isbn

**Justification**
Permet une recherche rapide des livres par auteur grâce à un accès direct à la partition.Il est basé sur un modèle volontairement dénormalisé pour améliorer les performances, 

4. **Consultation du profil utilisateur** :
```bash
SELECT * FROM users_by_id WHERE user_id = ?;
```
Table utilisée : users_by_id
Clé : Partition key : user_id

**Justification**
Permet un accès direct au profil utilisateur pour vérifier rapidement les emprunts et l’état du compte, à l’aide d’une requête simple et très fréquente, 

5. **Historique des emprunts d'un utilisateur** :
```bash
SELECT * FROM borrows_by_user WHERE user_id = ?;
```
Table utilisée : borrows_by_user
Clé : Partition key : user_id
      Clustering key : borrow_date DESC

**Justification**
Permet d’afficher l’historique complet des emprunts d’un utilisateur, avec des résultats automatiquement triés par date décroissante, grâce à une lecture séquentielle efficace sans filtrage côté serveur, 

6. **Suivi des emprunts par livre** :
```bash
SELECT * FROM borrows_by_book WHERE isbn = ?;
```
Table utilisée : borrows_by_book
Clé : Partition key : isbn
      Clustering key : borrow_date, user_id

**Justification**
Permet d’identifier rapidement qui a emprunté un livre à partir de son ISBN, ce qui facilite la gestion des emprunts et des retours grâce à un accès direct aux données, 

7. **Gestion des réservations d’un livre** :
```bash
SELECT * FROM reservations WHERE isbn = ?;
```
Table utilisée : reservations
Clé : Partition key : isbn
      Clustering key : reservation_date

**Justification**
Permet de gérer une file d’attente par livre en respectant l’ordre chronologique des réservations, ce qui est adapté aux scénarios de forte demande, 

8. **Consultation des statistiques globales** :
```bash
SELECT value FROM statistics WHERE metric_name = ?;
```
Table utilisée : statistics
Clé : Partition key : metric_name

**Justification**
Stockage de compteurs globaux pour suivre les statistiques du système, en utilisant le type counter de Cassandra afin d’assurer des mises à jour atomiques et performantes, 

**CONCLUSION**
Le modèle Cassandra est conçu à partir des query patterns de l’application, avec une table dédiée par type d’accès afin de garantir performance et scalabilité. Le schéma est conçu de manière query‑driven, avec une table par requête, sans jointure ni ALLOW FILTERING, en s’appuyant sur une dénormalisation volontaire respectant les bonnes pratiques Cassandra. 