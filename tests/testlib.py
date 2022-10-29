from pathlib import Path
from src.loki_ops_manager import LokiManager

resource = "./loki.zip"

manager = LokiManager()
# manager.install(resource)

manager.loki_home = Path('/tmp/loki')
manager.loki = Path('/tmp/loki/loki-linux-amd64')

manager.loki_cfg = manager.loki_home.joinpath('loki-local-config.yaml')
manager.loki_unitfile = Path('/tmp/loki.service')

manager._prepareOS()
manager._install_from_resource(resource)
manager._install_config()
manager._install_systemd_unitfile()
if manager.verify_config():
    print("Config OK")
else:
    print("Config is error")

print("Version:", manager.loki_version )
# manager._purge()