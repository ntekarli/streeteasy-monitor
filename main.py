from src.streeteasymonitor.monitor import Monitor
from src.streeteasymonitor.config import Config
from src.streeteasymonitor.email_notifier import EmailNotifier


def main(**kwargs):
    with Monitor(**kwargs) as monitor:
        listings = monitor.run()
        
        if listings:
            # Send batch email notification
            email_notifier = EmailNotifier(monitor.config.get_email_config())
            if email_notifier.send_batch_notification(listings):
                # Insert all listings into database after successful email
                for listing in listings:
                    monitor.db.insert_new_listing(listing)


if __name__ == '__main__':
    cfg = Config()
    main(**cfg.get_search_params())
