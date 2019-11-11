import requests
from flask import Blueprint
from flask import request
from multiprocessing import Pool
from itertools import product

import json
import config
from . import helpers

smartgate_api = Blueprint('smartgate_api', __name__)
_SLASH_CMD_SNAP = '/cam'
_WORKERS = Pool(3)

@smartgate_api.route("/snap", methods=["POST"])
def cam_snap():
    """
    Get current snapshot of all cams of particular gate.
    """
    req_body = request.form
    try:
        validate_req(req_body['token'])
        args = match_cmd(
                    _SLASH_CMD_SNAP, 
                    req_body['command'], 
                    req_body['text']
                )
        callback_url = req_body['response_url']
        #execute_cmd_snap(args, callback_url)
        packed_args = [args, callback_url]
        _WORKERS.starmap_async(helpers.execute_cmd_snap, product(packed_args, repeat=2))
    except Exception as e:
        return "`ERROR` " + str(e)
    return '*INFO* Please wait, while we complete your request...'


def validate_req(authtoken):
    if (authtoken != config.SLASH_CAM_CMD_TOKEN):
        raise Exception("Untrusted command request.")

def match_cmd(expected, cmd, argline):
    if (expected != cmd):
        return None
    if (cmd == _SLASH_CMD_SNAP):
        return match_cmd_snap(argline)
    
    return None

def match_cmd_snap(argline):
    """
        Expects yard_name, gate_name as arguments
        example: /snap navkar outgate-1 (case insensitive)
    """
    argline = argline.lower()
    args = argline.split(' ')
    if (len(args) !=2):
        raise Exception(f"""Invalid number of arguments are provided. Expected: 2, Found: {len(args)}""")
    
    yard = args[0]
    if (not yard in config.YARDS_URL):
        raise Exception(f'Command is not yet supported for yard {yard}')

    return args