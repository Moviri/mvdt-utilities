import logging
import os
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

log = logging.getLogger(__name__)

def get_config_dir() -> Path:
    config_dir_base = os.path.expandvars("%PROGRAMDATA%") if os.name == "nt" else "/var/lib"
    config_dir = Path(config_dir_base) / "dynatrace" / "oneagent" / "agent" / "config"
    if config_dir.exists():
        return config_dir
    file_path = Path(__file__).resolve()

    while file_path.parent != file_path:
        file_path = file_path.parent
        if file_path.name == "agent":
            return file_path / "config"

    raise Exception("Could not find the OneAgent config directory")

def get_communication_endpoint() -> str:
    config_dir = get_config_dir()
    log.info(f"Using config dir: {config_dir}")
    deployment_conf_path = (config_dir / "deployment.conf").absolute()
    if not deployment_conf_path.exists():
        raise Exception(f"File deployment.conf was not found at: {deployment_conf_path}")

    servers: Optional[str] = None
    environment_id: Optional[str] = None
    try:
        with open(deployment_conf_path) as dc:
            for line in dc.readlines():
                if "Server={" in line:
                    _, content = line.split("=")
                    servers = content
                elif "Tenant=" in line:
                    _, content = line.split("=")
                    environment_id = content.strip()
        if servers is None:
            raise Exception("Missing mandatory 'Server=' section of the file")
        if environment_id is None:
            raise Exception("Missing mandatory 'Tenant=' section of the file")
    except Exception as e:
        raise Exception(f"Could not read deployment.conf at {deployment_conf_path}: {e}")

    main_server: Optional[str] = None
    server_sections = [p.strip().rstrip("}") for p in servers.split("{") if p]
    for part in server_sections:
        server_list = [s.strip() for s in part.split(";") if s]
        for candidate in server_list:
            if candidate.startswith("*"):
                main_server = candidate.lstrip("*")

                # Split into parts and reassemble without path
                # https://lwp00649.dynatrace.com:443/communication -> https://lwp00649.dynatrace.com:443
                # https://sg-us.dynatracelabs.com/communication -> https://sg-us.dynatracelabs.com
                parsed = urlparse(main_server)
                main_server = f"{parsed.scheme}://{parsed.netloc}/e/{environment_id}"

    if not main_server:
        raise Exception("Could not identify communication endpoint in deployment.conf")
    else:
        log.info(f"Identified server communication endpoint to be: {main_server}")

    return main_server
