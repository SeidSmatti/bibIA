# bibIA/src/parser.py

"""
Module de parsing avancé pour les entrées bibliographiques.
"""
import re
from typing import List, Dict, Any, Optional

class AdvancedBibParser:
    """
    Analyse une chaîne de référence bibliographique en essayant plusieurs stratégies
    correspondant à des normes de citation communes (ex: APA pour articles, ouvrages).
    """

    def __init__(self):
        # Regex communes
        self.YEAR_REGEX = re.compile(r'[\(\[]?((?:19|20)\d{2})[\)\]\.]?')
        self.DOI_REGEX = re.compile(r'10\.\d{4,9}/[-._;()/:A-Z0-9]+', re.IGNORECASE)
        self.AUTHORS_REGEX = re.compile(
            r'^((?:[A-Z][\w\'-]+,\s(?:[A-Z]\.\s?)+)(?:et al\.|,?\s(?:and|&)\s)?\s?)+',
            re.IGNORECASE
        )
        
        # Regex pour les informations de journal
        self.JOURNAL_INFO_REGEX = re.compile(
            r"""
            (?P<journal>.+?),\s* # Nom du journal (non-greedy)
            (?P<volume_issue>[\d\w\s\(\)-]+?)?  # Volume et numéro (très flexible)
            (?:,\s*(?:pp?\.?\s*)?(?P<pages>\d+-\d+))? # Pages (optionnel)
            """,
            re.VERBOSE | re.IGNORECASE
        )
        
        # Regex de pré-classification : cherche des motifs numériques propres aux articles
        self.IS_ARTICLE_REGEX = re.compile(r',\s*\d+.*,\s*\d+-\d+')

    def _parse_as_article(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Tente de parser le texte comme un article. Doit être stricte et échouer
        si la structure n'est pas clairement celle d'un article.
        """
        try:
            authors_match = self.AUTHORS_REGEX.match(text)
            if not authors_match: return None
            authors = authors_match.group(0).strip().rstrip(',')
            
            remaining_text = text[len(authors):].strip()

            year_match = self.YEAR_REGEX.search(remaining_text)
            if not year_match: return None
            year = year_match.group(1)
            
            after_year_part = remaining_text.split(year_match.group(0), 1)[1].strip().lstrip('.')

            # Le titre de l'article est séparé de la revue par un point.
            if '. ' not in after_year_part:
                return None # Structure non conforme à un article
                
            title, journal_part = after_year_part.split('. ', 1)

            journal_info_match = self.JOURNAL_INFO_REGEX.search(journal_part)
            
            # --- CONDITION DE FIABILITÉ ---
            # Si on ne trouve pas de structure "journal, volume, pages", on considère que ce n'est pas un article.
            if not journal_info_match or not journal_info_match.group('volume_issue'):
                return None

            return {
                'type': 'article', 'author': authors, 'year': year, 'title': title.strip(),
                'journal': journal_info_match.group('journal').strip(),
                # On ne sépare plus volume et issue, c'est trop source d'erreurs.
                'volume': journal_info_match.group('volume_issue').strip() if journal_info_match.group('volume_issue') else None,
                'pages': journal_info_match.group('pages'),
            }
        except (AttributeError, IndexError):
            return None

    def _parse_as_book(self, text: str) -> Optional[Dict[str, Any]]:
        """Tente de parser le texte comme un livre. Plus permissif."""
        try:
            authors_match = self.AUTHORS_REGEX.match(text)
            if not authors_match: return None
            authors = authors_match.group(0).strip().rstrip(',')

            remaining_text = text[len(authors):].strip()

            year_match = self.YEAR_REGEX.search(remaining_text)
            if not year_match: return None
            year = year_match.group(1)

            after_year_part = remaining_text.split(year_match.group(0), 1)[1].strip().lstrip('.')
            
            # Stratégie pour livre : Titre. Editeur.
            # On sépare par le dernier point pour isoler l'éditeur.
            if '. ' in after_year_part:
                title, publisher = after_year_part.rsplit('. ', 1)
            else:
                # Si pas de point, on suppose que tout est le titre.
                title = after_year_part
                publisher = None
            
            return {
                'type': 'book', 'author': authors, 'year': year,
                'title': title.strip().rstrip('.'), 'publisher': publisher.strip().rstrip('.') if publisher else None
            }
        except (AttributeError, IndexError):
            return None

    def _fallback_parse(self, text: str) -> Dict[str, Any]:
        """Analyse générique si les stratégies spécifiques échouent."""
        authors_match = self.AUTHORS_REGEX.match(text)
        authors = authors_match.group(0).strip().rstrip(',') if authors_match else None
        
        year_match = self.YEAR_REGEX.search(text)
        year = year_match.group(1) if year_match else None
        
        # Tente d'isoler un titre simple
        title = None
        if year and authors:
            try:
                after_year_part = text.split(year_match.group(0), 1)[1].strip().lstrip('.')
                title = after_year_part.split('. ')[0].strip()
            except IndexError:
                pass
        
        return {
            'type': 'unknown', 'author': authors, 'year': year, 'title': title
        }

    def parse(self, entry_text: str) -> Dict[str, Any]:
        """Point d'entrée principal pour parser une référence."""
        cleaned_text = entry_text.replace('\n', ' ').strip()
        
        # --- NOUVELLE STRATÉGIE DE DISPATCH ---
        # On essaie d'abord le parseur le plus strict (article), puis le plus souple (livre).
        parsed_data = self._parse_as_article(cleaned_text)
        
        if not parsed_data:
            parsed_data = self._parse_as_book(cleaned_text)
        
        if not parsed_data:
            parsed_data = self._fallback_parse(cleaned_text)
            
        # Ajout du DOI et du texte original à la fin
        parsed_data['doi'] = self.DOI_REGEX.search(cleaned_text).group(0) if self.DOI_REGEX.search(cleaned_text) else None
        parsed_data['original_text'] = entry_text
                    
        return parsed_data

# --- INTERFACE PUBLIQUE DU MODULE (inchangée) ---
def parse_entry(entry_text: str) -> Dict[str, Any]:
    parser = AdvancedBibParser()
    return parser.parse(entry_text)

def split_bibliography(raw_text: str) -> List[str]:
    if not raw_text or not raw_text.strip(): return []
    entries = re.split(r'\n\s*\n', raw_text.strip())
    return [entry.strip() for entry in entries if entry.strip()]
