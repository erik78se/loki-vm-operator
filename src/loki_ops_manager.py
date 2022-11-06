"""DataPlaneAPIOpsManager Class"""
import re
import sys
import subprocess
from urllib import request
import zipfile
import shutil
from pathlib import Path
import requests


class LokiManager:
    """
    Mangages the Loki service, such as installing, configuring, etc.

    This class should work independently from juju, such as that it can
    be tested without lauching a full juju environment.
    """

    def __init__(self):
        self.loki_home = Path('/opt/loki')
        self.loki = Path('/opt/loki/loki-linux-amd64')
        self.loki_cfg = self.loki_home.joinpath('loki-local-config.yaml')
        self.loki_unitfile = Path('/etc/systemd/system/loki.service')
        
    def _prepareOS(self):
        """ sudo mkdir /opt/loki """
        try:
            subprocess.run(['mkdir', '-p', self.loki_home], check = True)
            print(f"Prepared OS for loki installation {self.loki_home}")
        except:
            print(f"Error preparing OS for loki installation {self.loki_home}")

    def _install_from_resource(self, resource_path):
        """
        Install from a resource.
        """
        # Remove the loki home dir if exists
        if self.loki_home.exists():
            shutil.rmtree(self.loki_home)

        # Unzip the juju resource into the build dir
        with zipfile.ZipFile(resource_path,"r") as zip_ref:
            zip_ref.extractall(self.loki_home)

        try:
            subprocess.run(['chmod','a+x',self.loki], check = True) 
        except:
            print("Error installing loki binary")
            sys.exit(1)

    def _install_config(self):
        """
        Install the config from template.
        """
        if self.loki_cfg.exists():
            self.loki_cfg.unlink()
        lokiconfig_tmpl = Path('templates/loki-local-config.yaml.tmpl').read_text()
        self.loki_cfg.write_text(lokiconfig_tmpl)

    def _install_systemd_unitfile(self):
        """ Install the systemd unit file."""
        if self.loki_unitfile.exists():
            self.loki_unitfile.unlink()
        systemdunitfile_tmpl = Path('templates/loki.service.tmpl').read_text()
        self.loki_unitfile.write_text(systemdunitfile_tmpl)

    def stop_loki(self):
        """Stop loki"""
        try:
            subprocess.run(['systemctl','stop','loki'], check = True)
        except Exception as e:
            print("Error stopping loki", str(e))

    def start_loki(self):
        """Start loki"""
        try:
            subprocess.run(['systemctl','start','loki'], check = True)            
        except Exception as e:
            print("Error starting loki", str(e))
    
    def restart_loki(self):
        """Restart loki"""
        try:
            subprocess.run(['systemctl','restart','loki'], check = True)            
        except Exception as e:
            print("Error starting loki", str(e))


    def install(self, resource_file):
        """ Installs from a supplied zip file resource """
        self._prepareOS()
        self._install_from_resource(resource_file)
        self._install_config()
        self._install_systemd_unitfile()

    def loki_version(self):
        """ Return the version of loki as a string or None"""
        try:
            r = subprocess.run(
                [
                    self.loki.resolve(), 
                    '-config.file', self.loki_cfg.resolve(),
                    '-version'
                ],capture_output=True
            ).stdout.decode()            
            ver = re.search(r'version\s*([\d.]+)', r).group(1)
            return ver
        except Exception as e:
            print("Error getting version from loki", e)
            return None

    def verify_config(self, filename=None):
        """ Use loki to verify a loki config. E.g. look for msg="config is valid" """
        if filename:
            filetocheck = Path(filename)
        else:
            filetocheck = self.loki_cfg
        try:
            r = subprocess.run(
                [
                    self.loki.resolve(), 
                    '-config.file', filetocheck.resolve(),
                    '-verify-config'
                ],capture_output=True
            )
            s = r.stderr.decode()
            return re.search(r'config is valid', s)

        except Exception as e:
            print("Error verifying config", e)
            return None

    def is_ready(self):
        """
        Checks the status of loki service by calling the api on localhost. 
        Manually: curl -G -s http://localhost:3100/ready
        """
        url = "http://localhost:3100/ready"
        r = requests.get(url, timeout=2.50)
        return r.text.strip() == "ready"




    def _purge(self):
        """ Whipes the installation and remove all traces of Loki """
        try:
            subprocess.run(['rm', self.loki], check = True)
            print("Success removing loki bin", self.loki)
            subprocess.run(['rm', self.loki_unitfile], check = True)
            print("Success removing loki unitfile", self.loki_unitfile)
            subprocess.run(['rm', '-rf', self.loki_home], check = True)
            print("Success purging loki home dir", self.loki_home)
        except:
            print("Error purging loki")