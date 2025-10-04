"""
Web Scraping Service - Fallback content retrieval
Scrapes NCERT website and educational portals when RAG doesn't find content
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import logging
import re

logger = logging.getLogger(__name__)


class WebScrapingService:
    """Service for scraping educational content as fallback"""
    
    def __init__(self):
        self.ncert_base_url = "https://ncert.nic.in"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.timeout = 10
    
    def search_ncert_website(
        self,
        query: str,
        grade: int,
        subject: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Search NCERT website for relevant content
        
        Args:
            query: Search query
            grade: Student's grade level
            subject: Optional subject filter
        
        Returns:
            Dict with scraped content and sources
        """
        try:
            # Build search URL (this is a simplified example)
            search_url = f"{self.ncert_base_url}/textbook.php"
            
            results = {
                'found': False,
                'content': [],
                'sources': [],
                'links': []
            }
            
            # Try to fetch content
            response = requests.get(search_url, headers=self.headers, timeout=self.timeout)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract relevant textbook links
                links = self._extract_ncert_links(soup, grade, subject)
                results['links'] = links
                
                # Try to fetch actual content from links
                if links:
                    content = self._scrape_ncert_content(links[0])
                    if content:
                        results['found'] = True
                        results['content'] = [content]
                        results['sources'] = [links[0]]
            
            return results
            
        except Exception as e:
            logger.error(f"Error scraping NCERT website: {e}")
            return {
                'found': False,
                'content': [],
                'sources': [],
                'links': [],
                'error': str(e)
            }
    
    def search_educational_portals(
        self,
        query: str,
        grade: int
    ) -> Dict[str, any]:
        """
        Search other educational portals for content
        
        Args:
            query: Search query
            grade: Student's grade level
        
        Returns:
            Dict with scraped content and sources
        """
        results = {
            'found': False,
            'content': [],
            'sources': [],
            'links': []
        }
        
        # Define educational portals to search
        portals = [
            {
                'name': 'Khan Academy',
                'search_url': f"https://www.khanacademy.org/search?page_search_query={query}",
                'base_url': 'https://www.khanacademy.org'
            },
            {
                'name': 'BYJU\'S',
                'search_url': f"https://byjus.com/?s={query}",
                'base_url': 'https://byjus.com'
            }
        ]
        
        for portal in portals:
            try:
                content = self._scrape_portal(portal, query, grade)
                if content:
                    results['found'] = True
                    results['content'].append(content['text'])
                    results['sources'].append(portal['name'])
                    results['links'].append(content['url'])
                    break  # Stop after first successful scrape
                    
            except Exception as e:
                logger.warning(f"Failed to scrape {portal['name']}: {e}")
                continue
        
        return results
    
    def _extract_ncert_links(
        self,
        soup: BeautifulSoup,
        grade: int,
        subject: Optional[str]
    ) -> List[str]:
        """Extract relevant NCERT textbook links"""
        links = []
        
        try:
            # Find links that match grade level
            grade_keywords = [f"class {grade}", f"class-{grade}", f"{grade}th"]
            
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                text = link.get_text().lower()
                
                # Check if link is relevant to grade
                if any(keyword in text for keyword in grade_keywords):
                    full_url = href if href.startswith('http') else f"{self.ncert_base_url}/{href}"
                    links.append(full_url)
            
        except Exception as e:
            logger.error(f"Error extracting NCERT links: {e}")
        
        return links[:5]  # Return top 5 links
    
    def _scrape_ncert_content(self, url: str) -> Optional[str]:
        """Scrape content from a specific NCERT page"""
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Remove script and style elements
                for element in soup(['script', 'style', 'nav', 'header', 'footer']):
                    element.decompose()
                
                # Extract text content
                text = soup.get_text(separator='\n', strip=True)
                
                # Clean up text
                text = re.sub(r'\n+', '\n', text)
                text = re.sub(r' +', ' ', text)
                
                return text[:2000]  # Limit to 2000 characters
            
        except Exception as e:
            logger.error(f"Error scraping content from {url}: {e}")
        
        return None
    
    def _scrape_portal(
        self,
        portal: Dict,
        query: str,
        grade: int
    ) -> Optional[Dict]:
        """Scrape content from an educational portal"""
        try:
            response = requests.get(
                portal['search_url'],
                headers=self.headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find first article or main content
                content_div = soup.find('article') or soup.find('main') or soup.find('div', class_=re.compile('content'))
                
                if content_div:
                    # Remove unwanted elements
                    for element in content_div(['script', 'style', 'nav', 'header', 'footer']):
                        element.decompose()
                    
                    text = content_div.get_text(separator='\n', strip=True)
                    text = re.sub(r'\n+', '\n', text)
                    text = re.sub(r' +', ' ', text)
                    
                    return {
                        'text': text[:1500],
                        'url': portal['search_url']
                    }
            
        except Exception as e:
            logger.error(f"Error scraping portal: {e}")
        
        return None
    
    def get_youtube_recommendations(
        self,
        topic: str,
        grade: int
    ) -> List[Dict[str, str]]:
        """
        Get YouTube video recommendations for a topic
        
        Args:
            topic: Topic to search for
            grade: Student's grade level
        
        Returns:
            List of video recommendations
        """
        # This would ideally use YouTube Data API
        # For now, return curated recommendations
        recommendations = [
            {
                'title': f"{topic} - Class {grade} Explanation",
                'url': f"https://www.youtube.com/results?search_query={topic}+class+{grade}+NCERT",
                'description': f"Video explanation for {topic}"
            },
            {
                'title': f"{topic} - Khan Academy",
                'url': f"https://www.youtube.com/results?search_query={topic}+Khan+Academy",
                'description': f"Khan Academy video on {topic}"
            }
        ]
        
        return recommendations


# Singleton instance
_scraping_service_instance = None


def get_scraping_service() -> WebScrapingService:
    """Get or create web scraping service singleton"""
    global _scraping_service_instance
    if _scraping_service_instance is None:
        _scraping_service_instance = WebScrapingService()
    return _scraping_service_instance
