DROP KEYSPACE IF EXISTS library_system;

CREATE KEYSPACE library_system WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};
USE library_system;

-- 1. Recherche par ISBN
CREATE TABLE books_by_id (
    isbn text PRIMARY KEY,
    title text,
    author text,
    category text,
    publisher text,
    publication_year int,
    total_copies int,
    available_copies int,
    description text
);

-- 2. Navigation par catégorie
CREATE TABLE books_by_category (
    category text,
    isbn text,
    title text,
    author text,
    available_copies int, 
    PRIMARY KEY (category, isbn)
) WITH CLUSTERING ORDER BY (isbn ASC);

-- 3. Recherche par auteur
CREATE TABLE books_by_author (
    author text,
    isbn text,
    title text,
    PRIMARY KEY (author, isbn)
);

-- 4. Profil utilisateur
CREATE TABLE users_by_id (
    user_id uuid PRIMARY KEY,
    email text,
    first_name text,
    last_name text,
    registration_date timestamp
);

-- 5. Historique emprunts (Trié par date décroissante)
CREATE TABLE borrows_by_user (
    user_id uuid,
    borrow_date timestamp,
    isbn text,
    book_title text,
    status text,
    PRIMARY KEY (user_id, borrow_date)
) WITH CLUSTERING ORDER BY (borrow_date DESC);

-- 6. Suivi par livre
CREATE TABLE borrows_by_book (
    isbn text,
    borrow_date timestamp,
    user_id uuid,
    user_name text,
    PRIMARY KEY (isbn, borrow_date, user_id)
);

-- 7. Réservations
CREATE TABLE reservations (
    isbn text,
    reservation_date timestamp,
    user_id uuid,
    PRIMARY KEY (isbn, reservation_date)
);

-- 8. Compteurs globaux
CREATE TABLE statistics (
    metric_name text PRIMARY KEY,
    value counter
);