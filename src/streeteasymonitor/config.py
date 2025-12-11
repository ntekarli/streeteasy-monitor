from environs import Env
from fake_useragent import UserAgent


class Config:
    defaults = {
        'min_price': 2000,
        'max_price': 4500,
        'min_beds': 1,
        'max_beds': 2,
        'baths': 1,
        'areas': [
            # 'Carroll Gardens',
            # 'Clinton Hill',
            # 'Cobble Hill',
            # 'Crown Heights',
            'East Village',
            # 'Fort Greene',
            # 'Gowanus',
            # 'Greenpoint',
            # 'Park Slope',
            # 'Prospect Heights',
            # 'Prospect Lefferts Gardens',
            # 'Williamsburg',
            # 'Bedford-Stuyvesant',
            # 'Boerum Hill',
            # 'DUMBO',
            # 'Downtown Brooklyn',
            # 'Ridgewood',
            # 'Brooklyn Heights',
            # 'Lower East Side',
            # 'Upper East Side',
        ],
        'amenities': [
            # 'pets',
            # 'doorman',
            'laundry',
            # 'elevator',
            # 'private_outdoor_space',
            'dishwasher',
            # 'washer_dryer',
            # 'gym',
        ],
        'no_fee': False,
    }

    filters = {
        'url': [
            '?featured=1',
            '?infeed=1',
        ],
        'address': [
            # 'Herkimer',
            # 'Fulton',
        ],
        'neighborhood': [
            # 'Ocean Hill',
            # 'Flatbush',
            # 'Bushwick',
            # 'Weeksville',
            # 'Stuyvesant Heights',
            # 'New Development',
        ],
    }

    def __init__(self):
        self.env = Env()
        self.env.read_env()

    def get_headers(self):
        self.ua = UserAgent()
        self.random_user_agent = self.ua.random
        self.default_user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
        self.user_agent = self.random_user_agent or self.default_user_agent

        return {
            'user-agent': self.user_agent,
            'accept-language': 'en-US,en;q=0.9',
            'referer': 'https://streeteasy.com/',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'origin': 'https://streeteasy.com',
        }

    def get_email_config(self):
        port_str = self.env('SMTP_PORT', default='587')
        port = int(port_str) if port_str else 587
        return {
            'server': self.env('SMTP_SERVER', default='smtp.gmail.com'),
            'port': port,
            'username': self.env('SMTP_USERNAME', default=''),
            'password': self.env('SMTP_PASSWORD', default=''),
            'recipient': self.env('EMAIL_RECIPIENT', default=''),
        }

    def get_field_values(self):
        return {
            'message': self.env('MESSAGE', default=''),
            'phone': self.env('PHONE', default=''),
            'email': self.env('EMAIL', default=''),
            'name': self.env('NAME', default=''),
            'search_partners': None,
        }

    def _parse_list(self, value: str):
        """Parse a CSV or JSON-style list from an environment string."""
        if not value:
            return []
        v = value.strip()
        if v.startswith('['):
            try:
                import json

                return json.loads(v)
            except Exception:
                pass
        return [item.strip() for item in v.split(',') if item.strip()]

    def get_search_params(self):
        """Load search parameters from environment (or fall back to defaults).

        Returns a dict suitable to pass into `main(**params)`.
        """
        # numeric fields - fall back to defaults if not set or empty
        def _int_env(name, default):
            s = self.env(name, default=str(default))
            return int(s) if s and str(s).strip() != '' else int(default)

        return {
            'min_price': _int_env('MIN_PRICE', self.defaults['min_price']),
            'max_price': _int_env('MAX_PRICE', self.defaults['max_price']),
            'min_beds': _int_env('MIN_BEDS', self.defaults['min_beds']),
            'max_beds': _int_env('MAX_BEDS', self.defaults['max_beds']),
            'baths': _int_env('BATHS', self.defaults['baths']),
            'areas': self._parse_list(self.env('AREAS', default=','.join(self.defaults['areas']))),
            'amenities': self._parse_list(self.env('AMENITIES', default=','.join(self.defaults['amenities']))),
            'no_fee': self.env('NO_FEE', default=str(self.defaults.get('no_fee', False))).lower() in ('1', 'true', 'yes'),
        }
