"""
Wikidata data ingestion module for CiteRight-Multiverse
"""
import requests
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class WikidataIngester:
    def __init__(self):
        """Initialize Wikidata ingester"""
        self.base_url = "https://www.wikidata.org/w/api.php"
        
    def search_entities(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search Wikidata for entities related to query"""
        try:
            params = {
                'action': 'wbsearchentities',
                'search': query,
                'language': 'en',
                'format': 'json',
                'limit': max_results
            }
            
            headers = {
                'User-Agent': 'CiteRight-Multiverse/1.0 (https://github.com/your-repo/citeright-multiverse)'
            }
            
            response = requests.get(self.base_url, params=params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            entities = []
            
            for item in data.get('search', []):
                try:
                    entity = self._get_entity_details(item['id'])
                    if entity:
                        entities.append(entity)
                except Exception as e:
                    logger.warning(f"Failed to get details for entity {item.get('id', 'unknown')}: {e}")
                    continue
                    
            return entities
            
        except Exception as e:
            logger.error(f"Wikidata search failed: {e}")
            return []
    
    def get_entity_by_id(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific Wikidata entity by ID"""
        try:
            return self._get_entity_details(entity_id)
        except Exception as e:
            logger.error(f"Failed to get entity {entity_id}: {e}")
            return None
    
    def _get_entity_details(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a Wikidata entity"""
        try:
            # Get entity data
            params = {
                'action': 'wbgetentities',
                'ids': entity_id,
                'format': 'json',
                'props': 'labels|descriptions|claims|sitelinks'
            }
            
            headers = {
                'User-Agent': 'CiteRight-Multiverse/1.0 (https://github.com/your-repo/citeright-multiverse)'
            }
            
            response = requests.get(self.base_url, params=params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            entity_data = data.get('entities', {}).get(entity_id)
            
            if not entity_data:
                return None
                
            # Extract labels and descriptions
            labels = entity_data.get('labels', {})
            descriptions = entity_data.get('descriptions', {})
            
            title = labels.get('en', {}).get('value', entity_id)
            description = descriptions.get('en', {}).get('value', '')
            
            # Extract key claims (properties)
            claims = entity_data.get('claims', {})
            key_properties = self._extract_key_properties(claims)
            
            # Get Wikipedia link if available
            sitelinks = entity_data.get('sitelinks', {})
            wikipedia_url = ""
            if 'enwiki' in sitelinks:
                wikipedia_url = f"https://en.wikipedia.org/wiki/{sitelinks['enwiki']['title'].replace(' ', '_')}"
            
            # Create content
            content_parts = [f"Entity: {title}"]
            if description:
                content_parts.append(f"Description: {description}")
            
            if key_properties:
                content_parts.append("Key Properties:")
                for prop, value in key_properties.items():
                    content_parts.append(f"  {prop}: {value}")
            
            content = "\n".join(content_parts)
            
            return {
                "title": title,
                "content": content,
                "summary": f"{title} - {description}" if description else title,
                "url": f"https://www.wikidata.org/wiki/{entity_id}",
                "source": entity_id,
                "origin": "Wikidata",
                "license": "CC0 1.0",
                "metadata": {
                    "entity_id": entity_id,
                    "labels": {lang: data['value'] for lang, data in labels.items()},
                    "descriptions": {lang: data['value'] for lang, data in descriptions.items()},
                    "wikipedia_url": wikipedia_url,
                    "sitelinks": list(sitelinks.keys()),
                    "property_count": len(claims)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get entity details for {entity_id}: {e}")
            return None
    
    def _extract_key_properties(self, claims: Dict[str, Any]) -> Dict[str, str]:
        """Extract key properties from Wikidata claims"""
        key_properties = {}
        
        # Property mappings for common properties
        property_mappings = {
            'P31': 'instance of',
            'P279': 'subclass of',
            'P106': 'occupation',
            'P569': 'date of birth',
            'P570': 'date of death',
            'P19': 'place of birth',
            'P20': 'place of death',
            'P27': 'country of citizenship',
            'P21': 'sex or gender',
            'P39': 'position held',
            'P108': 'employer',
            'P69': 'educated at',
            'P166': 'award received'
        }
        
        for prop_id, claim_list in claims.items():
            if prop_id in property_mappings:
                prop_name = property_mappings[prop_id]
                if claim_list:
                    # Get the first claim value
                    main_snak = claim_list[0].get('mainsnak', {})
                    if main_snak.get('snaktype') == 'value':
                        datavalue = main_snak.get('datavalue', {})
                        value = self._format_property_value(datavalue)
                        if value:
                            key_properties[prop_name] = value
        
        return key_properties
    
    def _format_property_value(self, datavalue: Dict[str, Any]) -> Optional[str]:
        """Format a Wikidata property value"""
        try:
            value_type = datavalue.get('type')
            value_data = datavalue.get('value')
            
            if value_type == 'wikibase-entityid':
                return f"Q{value_data['numeric-id']}"
            elif value_type == 'string':
                return value_data
            elif value_type == 'time':
                return value_data.get('time', '')
            elif value_type == 'quantity':
                return str(value_data.get('amount', ''))
            elif value_type == 'monolingualtext':
                return value_data.get('text', '')
            else:
                return str(value_data)
                
        except Exception as e:
            logger.warning(f"Failed to format property value: {e}")
            return None
    
    def get_entities_by_category(self, category_id: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Get entities that belong to a specific category"""
        try:
            # Use SPARQL query to find entities in a category
            sparql_query = f"""
            SELECT ?item ?itemLabel WHERE {{
                ?item wdt:P31 wd:{category_id} .
                SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" . }}
            }}
            LIMIT {max_results}
            """
            
            params = {
                'action': 'query',
                'format': 'json',
                'query': sparql_query
            }
            
            headers = {
                'User-Agent': 'CiteRight-Multiverse/1.0 (https://github.com/your-repo/citeright-multiverse)'
            }
            
            response = requests.get(self.base_url, params=params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            entities = []
            
            for binding in data.get('query', {}).get('results', {}).get('bindings', []):
                item_id = binding.get('item', {}).get('value', '').split('/')[-1]
                entity = self._get_entity_details(item_id)
                if entity:
                    entities.append(entity)
                    
            return entities
            
        except Exception as e:
            logger.error(f"Failed to get entities by category {category_id}: {e}")
            return []


def ingest_wikidata_content(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """Convenience function to ingest Wikidata content"""
    ingester = WikidataIngester()
    return ingester.search_entities(query, max_results)
