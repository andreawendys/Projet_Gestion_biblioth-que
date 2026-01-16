# Projet :Système de Gestion de Bibliothèque Numérique
Ce fichier README détaille les procédures d'installation, de configuration et d'utilisation du système de gestion de bibliothèque numérique. La solution permet de gérer les livres, les utilisateurs et les emprunts en utilisant un cluster Cassandra distribué.


## Guide d'Installation rapide

1. **Lancer le cluster (Docker)** :
   ```bash
   docker-compose up -d
  ```
2. **Vérifier le cluster** :  
 ```bash
   docker exec -it cassandra1 nodetool status
 ```
3. **Installer les dépendances Python** :  
 ```bash
pip install -r requirements.txt
```
4. **Initialiser le schéma(Creation Tables)** :  
 ```bash
 python -m scripts.init_schema
 ```
5. **Générer des données** :  
```bash
 python scripts/generate_data.py 
```
6. **Utilisation CLI (Pour tests)** :  
 ```bash
# Lister par catégorie
python cli/main.py books list-by-category --category "Science Fiction"
# Inscrire un utilisateur
python cli/main.py users register
# Rechercher un livre
python cli/main.py books search --isbn "978-0-123456-78-9"
 ```
7. **Lancer l'Interface Web Streamlit** :    
 ```bash
 streamlit run app_web.py
  ```
8. **Test et performance** :   
  -Pour réaliser les tests unitaires avec pytest (Statut : ✅ PASS)
 ```bash
 python -m pytest  
   ```
  -Pour réaliser le benchmark de performance
  ```bash
   python -m scripts.benchmark
    ```




