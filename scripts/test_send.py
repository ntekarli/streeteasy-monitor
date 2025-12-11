from src.streeteasymonitor.config import Config
from src.streeteasymonitor.email_notifier import EmailNotifier

if __name__ == '__main__':
    cfg = Config()
    email_cfg = cfg.get_email_config()

    notifier = EmailNotifier(email_cfg)

    listing = {
        'address': '123 Test St',
        'price': 2500,
        'neighborhood': 'Testville',
        'url': 'https://example.com/listing/123',
    }

    print('Using SMTP config:')
    print({k: ('***' if k in ('password',) else v) for k, v in email_cfg.items()})

    ok = notifier.send_listing_notification(listing)
    print('RESULT:', 'OK' if ok else 'FAILED')
