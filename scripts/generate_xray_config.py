import os
import sys
import json
from urllib.parse import urlparse, parse_qs

def parse_vless(url):
    parsed = urlparse(url)
    if parsed.scheme != 'vless':
        raise ValueError("Only vless:// URLs are supported")
    
    uuid = parsed.username
    host = parsed.hostname
    port = parsed.port
    qs = parse_qs(parsed.query)
    
    flow = qs.get("flow", [""])[0]
    security = qs.get("security", [""])[0]
    network = qs.get("type", ["tcp"])[0]
    sni = qs.get("sni", [""])[0]
    fp = qs.get("fp", [""])[0]
    pbk = qs.get("pbk", [""])[0]
    sid = qs.get("sid", [""])[0]
    spx = qs.get("spx", [""])[0]
    
    config = {
        "log": {"loglevel": "warning"},
        "inbounds": [
            {
                "port": 10809,
                "listen": "127.0.0.1",
                "protocol": "http",
                "settings": {"allowTransparent": False}
            }
        ],
        "outbounds": [
            {
                "protocol": "vless",
                "settings": {
                    "vnext": [
                        {
                            "address": host,
                            "port": port,
                            "users": [
                                {
                                    "id": uuid,
                                    "encryption": "none",
                                    "flow": flow
                                }
                            ]
                        }
                    ]
                },
                "streamSettings": {
                    "network": network,
                    "security": security,
                    "realitySettings": {
                        "serverName": sni,
                        "fingerprint": fp,
                        "publicKey": pbk,
                        "shortId": sid,
                        "spiderX": spx
                    } if security == "reality" else None
                }
            }
        ]
    }
    
    if security != "reality":
        del config["outbounds"][0]["streamSettings"]["realitySettings"]

    return config

if __name__ == "__main__":
    vless_url = os.environ.get("VLESS_URL")
    if not vless_url:
        print("VLESS_URL environment variable is not set. Skipping proxy generation.")
        sys.exit(0)
        
    try:
        config = parse_vless(vless_url)
        with open("/app/xray_config.json", "w") as f:
            json.dump(config, f, indent=2)
        print("Xray configuration generated successfully.")
    except Exception as e:
        print(f"Error generating Xray config: {e}")
        sys.exit(1)
