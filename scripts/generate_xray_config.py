import os
import sys
import json
import re
from urllib.parse import urlparse, parse_qs

def parse_vless(url, tag):
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
    
    outbound = {
        "tag": tag,
        "protocol": "vless",
        "settings": {
            "vnext": [
                {
                    "address": host,
                    "port": int(port) if port else 443,
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
        }
    }
    
    if security == "reality":
        outbound["streamSettings"]["realitySettings"] = {
            "serverName": sni,
            "fingerprint": fp,
            "publicKey": pbk,
            "shortId": sid,
            "spiderX": spx
        }
    return outbound

def build_config(urls):
    outbounds = []
    for i, url in enumerate(urls):
        try:
            outbound = parse_vless(url.strip(), f"proxy-{i}")
            outbounds.append(outbound)
        except Exception as e:
            print(f"Failed to parse url {url}: {e}")
            
    if not outbounds:
        raise ValueError("No valid VLESS URLs parsed.")
        
    outbounds.append({
        "tag": "direct",
        "protocol": "freedom"
    })
    
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
        "outbounds": outbounds,
        "observatory": {
            "subjectSelector": ["proxy-"],
            "probeURL": "https://api.telegram.org",
            "probeInterval": "1m",
            "enableConcurrency": True
        },
        "routing": {
            "domainStrategy": "AsIs",
            "balancers": [
                {
                    "tag": "balancer",
                    "selector": ["proxy-"],
                    "strategy": {
                        "type": "leastPing"
                    }
                }
            ],
            "rules": [
                {
                    "type": "field",
                    "network": "tcp,udp",
                    "balancerTag": "balancer"
                }
            ]
        }
    }
    
    # If only 1 outbound, no need for balancer
    if sum(1 for o in outbounds if o["tag"].startswith("proxy-")) == 1:
        del config["observatory"]
        del config["routing"]
        
    return config

if __name__ == "__main__":
    vless_urls_raw = os.environ.get("VLESS_URL", "")
    
    # Extract all vless:// URLs by splitting on spaces, commas, or newlines
    splits = re.split(r'[\s,]+', vless_urls_raw)
    urls = [u for u in splits if u.strip().startswith("vless://")]
    
    if not urls:
        print("No valid VLESS_URL found in environment. Skipping proxy generation.")
        sys.exit(0)
        
    try:
        config = build_config(urls)
        with open("/app/xray_config.json", "w") as f:
            json.dump(config, f, indent=2)
        print(f"Xray configuration generated successfully with {len(urls)} fallback proxies.")
    except Exception as e:
        print(f"Error generating Xray config: {e}")
        sys.exit(1)
