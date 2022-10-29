#!/usr/bin/env python3
# Copyright 2022 Erik Lönroth
# See LICENSE file for licensing details.
#
# Learn more at: https://juju.is/docs/sdk

""" The Loki service:

API: https://grafana.com/docs/loki/latest/api/

"""

import logging
import os
import subprocess
import base64

from ops.charm import CharmBase
from ops.main import main
from ops.model import ActiveStatus, BlockedStatus, WaitingStatus
from loki_ops_manager import LokiManager

# Log messages can be retrieved using juju debug-log
logger = logging.getLogger(__name__)

class LokiCharm(CharmBase):
    """Charm the service."""

    def __init__(self, *args):
        super().__init__(*args)
        self.loki_ops_manager = LokiManager()
        self.framework.observe(self.on.install, self._on_install)
        self.framework.observe(self.on.config_changed, self._on_config_changed)
        self.framework.observe(self.on.start, self._on_start)
        self.framework.observe(self.on.update_status, self._update_status)
        self.framework.observe(self.on.set_config_action, self._on_set_config_action)

    def _on_install(self, event):
        """Handle install event."""
        logger.info("Installing loki...")
        zip_resource = self.model.resources.fetch('loki-zipfile')
        self.loki_ops_manager.install(zip_resource) # Prepares OS, installs binary and unitfile

    def _on_config_changed(self, event):
        """Handle changed configuration."""
        logger.info("Configuring loki...")
        pass

    def _on_start(self, event):
        """Handle start event."""
        logger.info("Starting loki...")
        self.loki_ops_manager.start_loki()
        self._set_status()
    
    def _update_status(self, event):
        """Handle update-status event."""
        self._set_status()

    def _on_set_config_action(self,event):
        """
        This action allows a user to upload a completely new config.
        
        juju run-action loki/0 set-config config="$(base64 /tmp/loki.yaml)" --wait

        The config is checked for errors before getting installed.

        Service is restarted if the config is OK.

        """
        base64_cfg = event.params['config']
        base64_bytes = base64_cfg.encode('ascii')
        cfg_bytes = base64.b64decode(base64_bytes)
        cfg = cfg_bytes.decode('ascii')

        with open('/tmp/_tmp_loki_cfg.yaml', 'w') as f:
            f.write(cfg)
        
        if self.loki_ops_manager.verify_config(filename='/tmp/_tmp_loki_cfg.yaml'):
            logger.info("Writing new config.")
            self.loki_ops_manager.loki_cfg.write_text(cfg)
            event.log("Successfully wrote new config.")
            os.remove("/tmp/_tmp_loki_cfg.yaml")
            self.loki_ops_manager.restart_loki()
        else:
            event.fail("loki -verify-config said config is bougs. No config was written")

    def _set_status(self):
        """
        Manage the status of the service.
        """
        stat = subprocess.call(["systemctl", "is-active", "--quiet", "loki"])
        if(stat == 0):  # if 0 (active), print "Active"
            v = self.loki_ops_manager.loki_version()
            self.unit.set_workload_version(v)
            self.unit.status = ActiveStatus("Active")
        else:
            self.unit.status = WaitingStatus("Loki service inactive.")


if __name__ == "__main__":  # pragma: nocover
    main(LokiCharm)
