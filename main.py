from src.streeteasymonitor.monitor import Monitor
from src.streeteasymonitor.config import Config
from src.streeteasymonitor.email_notifier import EmailNotifier


def main(**kwargs):
    with Monitor(**kwargs) as monitor:
        listings = monitor.run()
        
        if listings:
            # Send email notification for each listing
            email_notifier = EmailNotifier(monitor.config.get_email_config())
            for listing in listings:
                if email_notifier.send_listing_notification(listing):
                    monitor.db.insert_new_listing(listing)


if __name__ == '__main__':
    cfg = Config()
    main(**cfg.get_search_params())
