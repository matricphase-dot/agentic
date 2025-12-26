"""
Web Scraper Tool - Extract data from websites
"""

import requests
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class WebScraper:
    """Tool for scraping data from websites"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Agentic-Workflow-Engine/1.0'
        })
        logger.info("WebScraper initialized")
    
    def scrape_url(self, url: str, selector: Optional[str] = None) -> Dict[str, Any]:
        """Scrape content from a URL with optional CSS selector"""
        try:
            logger.info(f"Scraping URL: {url}")
            
            # Make request
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Parse HTML - use lxml if available, otherwise html.parser
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.content, 'lxml')
            except:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract content based on selector
            if selector:
                elements = soup.select(selector)
                content = [elem.get_text(strip=True) for elem in elements]
            else:
                # Get main content
                for tag in ['script', 'style', 'nav', 'footer', 'header']:
                    for element in soup.find_all(tag):
                        element.decompose()
                content = soup.get_text(separator='\n', strip=True)
                content = '\n'.join([line for line in content.split('\n') if line.strip()])
            
            return {
                "success": True,
                "url": url,
                "title": soup.title.string if soup.title else "No title",
                "content": content if isinstance(content, str) else content[:10],  # Limit for demo
                "element_count": len(content) if isinstance(content, list) else 1,
                "status_code": response.status_code,
                "timestamp": datetime.now().isoformat()
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return {
                "success": False,
                "error": f"Request failed: {e}",
                "url": url,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            return {
                "success": False,
                "error": f"Scraping failed: {e}",
                "url": url,
                "timestamp": datetime.now().isoformat()
            }
    
    def scrape_multiple(self, urls: List[str], selector: Optional[str] = None) -> Dict[str, Any]:
        """Scrape multiple URLs"""
        results = []
        for url in urls:
            result = self.scrape_url(url, selector)
            results.append(result)
        
        success_count = sum(1 for r in results if r.get("success"))
        
        return {
            "success": success_count > 0,
            "total_urls": len(urls),
            "successful": success_count,
            "failed": len(urls) - success_count,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }

# Test
if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    
    scraper = WebScraper()
    
    # Test simple scrape
    result = scraper.scrape_url("https://httpbin.org/html")
    print(f"Scrape successful: {result.get('success')}")
    if result.get("success"):
        print(f"Title: {result.get('title')}")
        print(f"Content preview: {str(result.get('content'))[:200]}...")
