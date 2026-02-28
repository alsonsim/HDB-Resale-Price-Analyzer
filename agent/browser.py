import subprocess

def navigate_hdb_portal(town: str, flat_type: str):
    """Use ActionBook CLI to navigate HDB's dynamic resale portal"""
    url = f"https://services2.hdb.gov.sg/webapp/BB33RTIS/BB33PReslTrans.jsp"
    
    commands = [
        f'actionbook browser open "{url}"',
        f'actionbook browser select "#town" "{town}"',
        f'actionbook browser select "#flatType" "{flat_type}"',
        'actionbook browser click "#search-btn"',
        'actionbook browser screenshot ./data/hdb_portal.png',
        'actionbook browser extract "table.results" --output ./data/live_results.json'
    ]
    
    for cmd in commands:
        subprocess.run(cmd, shell=True, check=True)
        print(f"✅ Executed: {cmd}")
