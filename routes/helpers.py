import requests
import config

def ack(cmd, args):
    """
    return formatted ack message
    """
    return f"""*INFO* Please wait, while we complete your request...
*REQ: * _{cmd} {args}_"""

def validate_req(cmd, authtoken):
    if (cmd == config._SLASH_CMD_SNAP and authtoken != config.SLASH_CAM_CMD_TOKEN):
        raise Exception("Untrusted command request.")
    elif (cmd == config._SLASH_CMD_LOG and authtoken != config.SLASH_LOG_CMD_TOKEN):
        raise Exception("Untrusted command request.")

def match_cmd(expected, cmd, argline):
    if (expected != cmd):
        return None
    if (cmd == config._SLASH_CMD_SNAP):
        return match_cmd_snap(argline)
    if (cmd == config._SLASH_CMD_LOG):
        return match_cmd_logs(argline)
    return None


def match_cmd_logs(argline):
    """
        Expects yard_name as argument
        example: /logs navkar (case insensitive)
    """
    yard = argline
    print(f'DEBUG {yard}')
    if (not yard in config.YARDS_URL):
        raise Exception(f'Command is not yet supported for yard {yard}')

    return [yard]

def match_cmd_snap(argline):
    """
        Expects yard_name, gate_name as arguments
        example: /cam navkar outgate-1 (case insensitive)
    """
    argline = argline.lower()
    args = argline.split(' ')
    if (len(args) !=2):
        raise Exception(f"""Invalid number of arguments are provided. Expected: 2, Found: {len(args)}""")
    
    yard = args[0]
    if (not yard in config.YARDS_URL):
        raise Exception(f'Command is not yet supported for yard {yard}')

    return args


def callback_slack(body, callback_url, yard_url):
    if (isinstance(body, str)):
        body = { 'text': body }
    else:
        body = _prepare_slack_webhook_body(body, yard_url)
        body = { 'blocks': body }

    resp = requests.post(callback_url, json=body)
    print(f"Slack response {resp.status_code}")
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
        callback_slack(gate_snaps, callback_url, yard_url)
    else:
        callback_slack(
            f"HAWK server did not respond properly, ERR CODE: {resp.status_code}", 
            callback_url,
            yard_url
        )

def execute_cmd_logs(args, callback_url):
    yard = args[0]
    yard_url = config.YARDS_URL[yard]
    api_url = f'{yard_url}/rest/enterprise/gate/ocr/logs'
    resp = requests.get(api_url)
    print(resp.status_code)
    callback_slack(_process_newlines(resp.text), callback_url, None)

def _process_newlines(text):
    return text.replace('\\n', '\n').replace('\'b\'', '')

def _prepare_slack_webhook_body(snaps, yard_url):
    blocks = []
    for snap in snaps:
        if snap is not None:
            blocks.append(
                {
                'type':'image', 
                'image_url': f"{yard_url}/rest/enterprise/gate/{snap['imagePath']}", 
                'alt_text': snap['camId'],
                'title': {
                    "type": "plain_text",
                    "text": snap['camId'],
			        }
                }
            )
    return blocks