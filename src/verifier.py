# bibIA/src/verifier.py
"""
Module de vérification des références.
"""
import asyncio
import random
import httpx
from typing import List, Dict, Any
from urllib.parse import quote_plus
from bs4 import BeautifulSoup

from .config import *

async def random_delay():
    """Applique un délai aléatoire."""
    await asyncio.sleep(random.uniform(*RANDOM_DELAY_RANGE))

def get_main_author_lastname(entry: Dict[str, Any]) -> str:
    """Extrait le nom de famille du premier auteur."""
    author = entry.get('author')
    if not author: return ""
    if ',' in author: return author.split(',')[0].strip()
    parts = author.split()
    return parts[-1] if parts else ""

# --- Fournisseurs de Vérification ---

async def verify_crossref(entry: Dict[str, Any], client: httpx.AsyncClient) -> Dict[str, Any]:
    source_name = "Crossref"
    if not entry.get('doi'):
        return {'source': source_name, 'status': 'skipped', 'reason': 'DOI manquant'}
    
    await random_delay()
    url = CROSSREF_API_URL.format(doi=quote_plus(entry['doi']))
    params = {'mailto': CROSSREF_MAILTO}
    try:
        response = await client.get(url, params=params, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            return {'source': source_name, 'status': 'found', 'link': f"https://doi.org/{entry['doi']}"}
        return {'source': source_name, 'status': 'not_found'}
    except httpx.RequestError as e:
        return {'source': source_name, 'status': 'error', 'details': str(e)}

async def verify_scholar(entry: Dict[str, Any], client: httpx.AsyncClient) -> Dict[str, Any]:
    source_name = "Google Scholar"
    if not entry.get('title'):
        return {'source': source_name, 'status': 'skipped', 'reason': 'Titre manquant'}
        
    await random_delay()
    # Requête précise avec le titre entre guillemets et le nom de l'auteur
    search_query = f'"{entry["title"]}" {get_main_author_lastname(entry)}'
    params = {'q': search_query}
    try:
        response = await client.get(SCHOLAR_SEARCH_URL, params=params, headers=HTTP_HEADERS)
        soup = BeautifulSoup(response.text, 'lxml')
        result_div = soup.find('div', class_='gs_r')
        if result_div:
            link_tag = result_div.find('h3', class_='gs_rt').find('a')
            if link_tag and link_tag.has_attr('href'):
                return {'source': source_name, 'status': 'found', 'link': link_tag['href']}
        return {'source': source_name, 'status': 'not_found'}
    except Exception as e:
        return {'source': source_name, 'status': 'error', 'details': str(e)}

# --- Orchestrateur ---

async def _verify_single_entry(entry: Dict[str, Any], client: httpx.AsyncClient) -> Dict[str, Any]:
    """Orchestre la vérification pour une seule entrée."""
    
    provider_tasks = [
        verify_crossref(entry, client),
        verify_scholar(entry, client),
    ]
    
    verification_results = await asyncio.gather(*provider_tasks)
    
    entry['verification_details'] = verification_results
    found_sources = [res for res in verification_results if res['status'] == 'found']
    
    if found_sources:
        entry['status'] = 'found'
        entry['found_in'] = found_sources
    else:
        entry['status'] = 'not_found'
        
    return entry

async def verify_references(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Point d'entrée principal."""
    async with httpx.AsyncClient(headers=HTTP_HEADERS, follow_redirects=True) as client:
        verification_tasks = [_verify_single_entry(entry, client) for entry in entries]
        results = await asyncio.gather(*verification_tasks)
    return results
