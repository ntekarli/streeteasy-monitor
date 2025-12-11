import json
import re

from bs4 import BeautifulSoup

from .config import Config
from .utils import build_url, get_datetime, get_area_map


class Search:
    """A search based on the current session, database instance, and keyword arguments for constructing a StreetEasy search URL.

    Attributes:
        area_map (dict[str, str]): A mapping of StreetEasy's neighborhood names and corresponding codes used for URL construction.
    """

    area_map: dict[str, str] = get_area_map()

    def __init__(self, monitor) -> None:
        """Initializes the search.

        Args:
            monitor (Monitor): A Monitor instance encapsulating a session, a database connection, and keyword arguments for constructing a search URL.

        Attributes:
            session (requests.Session): The session instance.
            db (Database): The database instance.
            kwargs (dict[str, str]): The search parameter components.
            codes (list[str, str]): The StreetEasy neighborhood codes corresponding to selected neighborhood names.

            price (str): The price range component of the search URL.
            area (str): The neighborhood code component of the search URL.
            beds (str): The number of beds component of the search URL.

            parameters (dict[str, str]): Dictionary mapping query components for URL construction.
            url (str): Search URL for the current query.
            listings (list[dict[str, str]]): Listings corresponding to the current search - initially empty.
        """

        self.session = monitor.session
        self.db = monitor.db
        self.kwargs = monitor.kwargs

        self.codes = [Search.area_map[area] for area in self.kwargs['areas']]

        self.area = ','.join(self.codes)
        self.price = f"{self.kwargs['min_price']}-{self.kwargs['max_price']}"
        self.beds = f"{self.kwargs['min_beds']}-{self.kwargs['max_beds']}"
        self.baths = f">={self.kwargs['baths']}"
        self.amenities = f"{','.join(self.kwargs['amenities'])}"
        self.no_fee = f"{1 if self.kwargs['no_fee'] == True else ''}"


        self.parameters = {
            'status': 'open',
            'price': self.price,
            'area': self.area,
            'beds': self.beds,
            'baths': self.baths,
            'amenities': self.amenities,
            'no_fee': self.no_fee,
        }

        self.url = build_url(**self.parameters)
        self.listings = []

    def fetch(self) -> list[dict[str, str]]:
        """Check the search URL for new listings."""
        print(f'Running script with parameters:\n{json.dumps(self.parameters, indent=2)}\n')
        print(f'URL: {self.url}')
        try:
            self.r = self.session.get(self.url, timeout=30)
            if self.r.status_code == 200:
                parser = Parser(self.r.content, self.db)
                self.listings = parser.listings
            else:
                print(f'{get_datetime()} Error: Received status code {self.r.status_code}\n')
        except Exception as e:
            print(f'{get_datetime()} Error fetching listings: {e}\n')
            self.listings = []

        if not self.listings:
            print(f'{get_datetime()} No new listings.\n')

        return self.listings


class Parser:
    """Separates parsing functionality from search.

    Attributes:
        price_pattern (re.Pattern): Regular expression used for stripping commas and dollar signs from listing price.
    """

    price_pattern = re.compile(r'[$,]')

    def __init__(self, content: bytes, db) -> None:
        """Initialize the parse object.

        Args:
            content (bytes): HTML content of a successful GET request to the search URL.
            db (Database): Database instance used for fetching listing IDs that already exist in the database.

        Attributes:
            soup (bs4.BeautifulSoup): Beautiful Soup object for parsing HTML contents.
            existing_ids (list[str]): Listing IDs that have already been stored in the database.
        """

        self.soup = BeautifulSoup(content, 'html.parser')
        self.existing_ids = db.get_existing_ids()

    def parse(self, card) -> dict[str, str]:
        """Parse the contents of one listing."""
        # Find the link to get URL and extract listing ID from it
        link = card.find('a', href=re.compile(r'/building/[^/]+/\w+'))
        if not link:
            return None
        
        url = link['href']
        # Extract building slug and unit ID from URL (e.g., /building/foo-bar/123)
        match = re.search(r'/building/([^/]+)/(\w+)', url)
        if match:
            building_slug = match.group(1)
            unit_id = match.group(2)
            listing_id = f"{building_slug}_{unit_id}"
        else:
            return None
        
        # Find price (look for span with $ symbol)
        price_elem = None
        for elem in card.find_all('span'):
            text = elem.get_text(strip=True)
            if text.startswith('$') and text[1:].replace(',', '').isdigit():
                price_elem = elem
                break
        
        if not price_elem:
            return None
        
        price = Parser.price_pattern.sub('', price_elem.get_text())
        
        # Get all text from card
        all_text = list(card.stripped_strings)
        
        # Find address (look for text with street/avenue and apartment number like "#4A")
        address = 'N/A'
        for text in all_text:
            # Skip "in [Neighborhood]" pattern
            if text.startswith('in '):
                continue
            # Look for street addresses or building names with unit numbers
            if ('#' in text or any(word in text.lower() for word in ['street', 'avenue', 'road', 'st ', 'ave '])) and len(text) > 10 and len(text) < 80:
                address = text
                break
        
        # If no address with # found, look for any address-like text
        if address == 'N/A':
            for text in all_text:
                if text.startswith('in '):
                    continue
                if any(word in text for word in ['East', 'West', 'North', 'South']) and any(char.isdigit() for char in text) and len(text) > 10 and len(text) < 80:
                    address = text
                    break
        
        # Find neighborhood (usually appears after "in" in the text)
        neighborhood = 'N/A'
        full_text = ' '.join(all_text)
        neighborhood_match = re.search(r' in ([A-Z][^|$]+?)(?:\s+\d+|\||$)', full_text)
        if neighborhood_match:
            neighborhood = neighborhood_match.group(1).strip()
        
        # Find listed by (broker/management company)
        listed_by = 'N/A'
        for i, text in enumerate(all_text):
            if text.lower() == 'listing by' and i + 1 < len(all_text):
                listed_by = all_text[i + 1]
                break

        return {
            'listing_id': listing_id,
            'url': f"https://streeteasy.com{url}" if not url.startswith('http') else url,
            'price': price,
            'address': address,
            'neighborhood': neighborhood,
            'listed_by': listed_by,
        }

    def filter(self, target) -> bool:
        """Filter a listing based on attributes not captured by StreetEasy's interface natively."""
        if target['listing_id'] in self.existing_ids:
            return False

        for key, substrings in Config.filters.items():
            target_value = target.get(key, '')
            if any(substring in target_value for substring in substrings):
                return False

        return True

    @property
    def listings(self) -> dict[str, str]:
        """Return all parsed and filtered listings."""
        # Updated selector for new CSS modules-based class names
        cards = self.soup.find_all('li', class_=re.compile(r'ListingCardsList_listCardWrapper'))
        parsed = [self.parse(card) for card in cards if self.parse(card) is not None]
        filtered = [card for card in parsed if self.filter(card)]
        return filtered
