from src.streeteasymonitor.monitor import Monitor
from src.streeteasymonitor.config import Config
from src.streeteasymonitor.email_notifier import EmailNotifier
from src.streeteasymonitor.utils import get_datetime


def main(**kwargs):
    try:
        with Monitor(**kwargs) as monitor:
            listings = monitor.run()
            
            if listings:
                print(f'{get_datetime()} Found {len(listings)} listings')
                # Insert all listings into database FIRST to prevent duplicates on retry
                for listing in listings:
                    monitor.db.insert_new_listing(listing)
                
                # Send batch email notification with all listings
                email_notifier = EmailNotifier(monitor.config.get_email_config())
                if email_notifier.send_batch_notification(listings):
                    print(f'{get_datetime()} Email sent and listings saved to database\n')
                else:
                    print(f'{get_datetime()} Email failed but listings were saved to prevent duplicate emails\n')
    except Exception as e:
        print(f'Fatal error in main: {e}')
        import traceback
        traceback.print_exc()
        raise


if __name__ == '__main__':
    cfg = Config()
    main(**cfg.get_search_params())
