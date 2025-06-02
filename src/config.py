# bibIA/src/config.py
"""
Fichier de configuration pour les constantes et paramètres de l'application.
Version simplifiée avec uniquement les sources fiables.
"""

# Headers pour les requêtes HTTP. Un User-Agent réaliste est crucial pour le scraping.
HTTP_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
    'Connection': 'keep-alive'
}

# Temps d'attente maximum pour une requête HTTP en secondes
REQUEST_TIMEOUT = 30.0 

# --- MODIFICATION ICI ---
# Délais aléatoires (en secondes) pour ne pas se faire bloquer par Google.
RANDOM_DELAY_RANGE = (10.0, 20.0)

# --- Configuration des Fournisseurs de Vérification ---

# Crossref (API)
CROSSREF_API_URL = "https://api.crossref.org/works/{doi}"
CROSSREF_MAILTO = "bibia.user@example.com" # Adresse email polie pour l'API Crossref

# Google Scholar (Scraping)
SCHOLAR_SEARCH_URL = "https://scholar.google.com/scholar"
