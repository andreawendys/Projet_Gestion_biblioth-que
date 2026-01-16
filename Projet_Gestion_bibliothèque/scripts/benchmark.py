import time
from config.database import CassandraConnection
from models.book import BookRepository, Book
from loguru import logger

def run_benchmark(count=1000):
    db = CassandraConnection()
    session = db.connect()
    repo = BookRepository(session)
    
    logger.info(f"🚀 Lancement du benchmark : Insertion de {count} livres...")
    start_time = time.time()
    
    for i in range(count):
        book = Book(
            isbn=f"BENCH-{i}",
            title=f"Livre de test {i}",
            author="Robot Benchmark",
            category="Science",
            publisher="DataGen",
            publication_year=2024,
            total_copies=10,
            available_copies=10
        )
        repo.add_book(book)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n" + "="*30)
    print(f"📊 RÉSULTATS DU BENCHMARK")
    print(f"Nombre d'insertions : {count}")
    print(f"Temps total         : {duration:.2f} secondes")
    print(f"Moyenne par livre   : {(duration/count)*1000:.2f} ms")
    print("="*30)
    
    db.close()

if __name__ == "__main__":
    run_benchmark(500) # Le test debutera par 500 afin de vérifier