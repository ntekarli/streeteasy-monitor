import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib.parse import quote
from .utils import get_datetime


class EmailNotifier:
    def __init__(self, smtp_config):
        self.smtp_server = smtp_config['server']
        self.smtp_port = smtp_config['port']
        self.sender_email = smtp_config['username']
        self.sender_password = smtp_config['password']
        self.recipient_email = smtp_config['recipient']
        self.maps_api_key = smtp_config.get('maps_api_key', '')

    def send_batch_notification(self, listings):
        """Send one email with all listings in HTML format."""
        if not listings:
            return False
            
        subject = f"StreetSweeper: {len(listings)} New Rental{'s' if len(listings) != 1 else ''} Found"
        html_body = self._format_html_email(listings)
        text_body = self._format_text_email(listings)
        
        try:
            self._send_email(subject, html_body, text_body)
            print(f'{get_datetime()} Batch email sent successfully with {len(listings)} listings\n')
            return True
        except Exception as e:
            print(f'{get_datetime()} Error sending batch email: {e}\n')
            return False

    def _format_html_email(self, listings):
        """Format all listings as HTML email with photos and cards."""
        # Build map image URL if API key is available
        map_img_html = ''
        if self.maps_api_key:
            map_url = self._build_static_map_url(listings)
            if map_url:
                map_img_html = f'<img src="{map_url}" alt="Map" style="width: 100%; max-width: 600px; height: auto; margin-bottom: 20px; border-radius: 8px;">'
        
        # Build listing cards
        cards_html = ''
        for listing in listings:
            photo_url = self._get_listing_photo(listing['url'])
            
            cards_html += f'''
            <div style="background: white; border-radius: 12px; overflow: hidden; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <img src="{photo_url}" alt="{listing['address']}" style="width: 100%; height: 250px; object-fit: cover;">
                <div style="padding: 20px;">
                    <h2 style="margin: 0 0 10px 0; font-size: 24px; color: #2c3e50;">
                        <a href="{listing['url']}" style="color: #2c3e50; text-decoration: none;">{listing['address']}</a>
                    </h2>
                    <p style="margin: 5px 0; color: #7f8c8d; font-size: 14px;">📍 {listing['neighborhood']}</p>
                    <p style="margin: 15px 0; font-size: 32px; font-weight: bold; color: #27ae60;">${listing['price']}</p>
                    <a href="{listing['url']}" style="display: inline-block; background: #3498db; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; margin-top: 10px;">View Listing</a>
                </div>
            </div>
            '''
        
        # Complete HTML email
        html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #2c3e50; margin: 0 0 10px 0;">🏠 StreetSweeper</h1>
                    <p style="color: #7f8c8d; margin: 0;">Found {len(listings)} new rental listing{'s' if len(listings) != 1 else ''} matching your criteria</p>
                </div>
                
                {map_img_html}
                
                {cards_html}
                
                <div style="text-align: center; margin-top: 30px; padding: 20px; color: #95a5a6; font-size: 12px;">
                    <p>StreetSweeper - Automated Rental Monitoring</p>
                </div>
            </div>
        </body>
        </html>
        '''
        return html
    
    def _format_text_email(self, listings):
        """Format all listings as plain text email (fallback)."""
        text = f"StreetSweeper - Found {len(listings)} new listing{'s' if len(listings) != 1 else ''}\n\n"
        
        for i, listing in enumerate(listings, 1):
            text += f"{i}. {listing['address']}\n"
            text += f"   Price: ${listing['price']}\n"
            text += f"   Neighborhood: {listing['neighborhood']}\n"
            text += f"   URL: {listing['url']}\n\n"
        
        text += "---\nStreetSweeper - Automated Rental Monitoring"
        return text
    
    def _get_listing_photo(self, listing_url):
        """Extract the first photo URL from a StreetEasy listing page."""
        try:
            import requests
            from fake_useragent import UserAgent
            from bs4 import BeautifulSoup
            
            ua = UserAgent()
            headers = {
                'user-agent': ua.random,
                'accept-language': 'en-US,en;q=0.9',
                'referer': 'https://streeteasy.com/',
            }
            
            # Fetch the listing page
            response = requests.get(listing_url, headers=headers, timeout=10)
            if response.status_code != 200:
                return self._get_placeholder_image()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try multiple selectors for images
            # Look for meta og:image tag (most reliable)
            og_image = soup.find('meta', property='og:image')
            if og_image:
                return og_image.get('content', self._get_placeholder_image())
            
            # Look for photo gallery images
            img = soup.find('img', class_=lambda x: x and 'photo' in str(x).lower())
            if img and img.get('src'):
                return img['src']
            
            # Look for any Zillow static image
            img = soup.find('img', src=lambda x: x and 'photos.zillowstatic.com' in x)
            if img:
                return img['src']
            
            return self._get_placeholder_image()
            
        except Exception as e:
            print(f"  Warning: Could not fetch photo for listing: {e}")
            return self._get_placeholder_image()
    
    def _get_placeholder_image(self):
        """Return a placeholder image URL."""
        return 'https://via.placeholder.com/600x400/3498db/ffffff?text=No+Image+Available'
    
    def _get_full_address_with_zip(self, listing_url):
        """Extract full address including ZIP code from listing page."""
        try:
            import requests
            from fake_useragent import UserAgent
            from bs4 import BeautifulSoup
            import re
            
            ua = UserAgent()
            headers = {
                'user-agent': ua.random,
                'accept-language': 'en-US,en;q=0.9',
                'referer': 'https://streeteasy.com/',
            }
            
            response = requests.get(listing_url, headers=headers, timeout=10)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for address with ZIP in the page text
            # StreetEasy typically shows full address like "123 Main St, Brooklyn, NY 11201"
            page_text = soup.get_text()
            
            # Match pattern: Address, Borough, NY ZIP
            zip_pattern = r'([^\n]+),\s*(Brooklyn|Manhattan|Queens|Bronx|Staten Island),\s*NY\s*(\d{5})'
            match = re.search(zip_pattern, page_text)
            
            if match:
                return f"{match.group(1).strip()}, {match.group(2)}, NY {match.group(3)}"
            
            return None
            
        except Exception as e:
            print(f"  Warning: Could not fetch full address: {e}")
            return None
    
    def _build_static_map_url(self, listings):
        """Build Google Static Maps URL with markers for all listing addresses."""
        if not self.maps_api_key or not listings:
            return None
        
        # Take up to 8 listings for the map
        map_listings = listings[:8]
        
        # Build markers parameter
        markers = []
        for listing in map_listings:
            # Get full address with ZIP from listing page for accurate geocoding
            full_address = self._get_full_address_with_zip(listing['url'])
            
            if full_address:
                markers.append(f"markers=color:red%7C{quote(full_address)}")
            elif listing['address'] and listing['address'] != 'N/A':
                # Fallback to basic address if full address extraction fails
                address_clean = listing['address'].replace('#', '').strip()
                markers.append(f"markers=color:red%7C{quote(address_clean + ', New York, NY')}")
        
        if not markers:
            return None
        
        # Build complete URL
        markers_str = '&'.join(markers)
        map_url = f"https://maps.googleapis.com/maps/api/staticmap?size=600x300&zoom=14&maptype=roadmap&{markers_str}&key={self.maps_api_key}"
        
        return map_url

    def _send_email(self, subject, html_body, text_body):
        """Send email via SMTP with HTML and plain text alternatives."""
        message = MIMEMultipart('alternative')
        message['From'] = self.sender_email
        message['To'] = self.recipient_email
        message['Subject'] = subject
        
        # Attach both plain text and HTML versions
        message.attach(MIMEText(text_body, 'plain'))
        message.attach(MIMEText(html_body, 'html'))

        with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30) as server:
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.send_message(message)
