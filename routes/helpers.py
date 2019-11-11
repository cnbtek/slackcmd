import requests
import config

def _prepare_slack_webhook_body(snaps, yard_url):
    blocks = []
    for snap in snaps:
        if snap is not None:
            blocks.append(
                {
                'type':'image', 
                'image_url': f"{yard_url}/{snap['imagePath']}", 
                'alt_text': snap['camId'],
                'title': {
                    "type": "plain_text",
                    "text": snap['camId'],
			        }
                }
            )
    return blocks

def callback_slack(body, callback_url, yard_url):
    if (isinstance(body, str)):
        body = { 'text': body }
    else:
        body = _prepare_slack_webhook_body(body, yard_url)
        body = { 'blocks': body }

    resp = requests.post(callback_url, json=body)
    resp.raise_for_status()

def execute_cmd_snap(args, callback_url):
    yard = args[0].lower()
    gate = args[1].lower()
    yard_url = config.YARDS_URL[yard]
    api_url = f'{yard_url}/rest/enterprise/gate/ipcam/capture'

    resp = requests.get(api_url)
    if (resp.status_code == 200):
        all_snaps = resp.json()
        gate_snaps = [s for s in all_snaps if (s is not None) and (s['camId'].lower().startswith(gate))]
        print(f"DEBUG {gate_snaps}")
        callback_slack(gate_snaps, callback_url, yard_url)
    else:
        callback_slack(
            f"HAWK server did not respond properly, ERR CODE: {resp.status_code}", 
            callback_url,
            yard_url
        )