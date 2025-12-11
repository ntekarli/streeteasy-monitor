from src.streeteasymonitor.monitor import Monitor
from src.streeteasymonitor.config import Config


def main(**kwargs):
    with Monitor(**kwargs) as monitor:
        monitor.run()


if __name__ == '__main__':
    cfg = Config()
    main(**cfg.get_search_params())
