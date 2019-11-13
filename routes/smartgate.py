import requests
from flask import Blueprint
from flask import request
from multiprocessing import Pool
from itertools import product

import json
import config
from . import helpers

smartgate_api = Blueprint('smartgate_api', __name__)
_WORKERS = Pool(3)

@smartgate_api.route("/snap", methods=["POST"])
def cam_snap():
    """
    Get current snapshot of all cams of particular gate.
    """
    req_body = request.form
    try:
        helpers.validate_req(config._SLASH_CMD_SNAP, req_body['token'])
        args = helpers.match_cmd(
                    config._SLASH_CMD_SNAP, 
                    req_body['command'], 
                    req_body['text']
                )
        callback_url = req_body['response_url']
        #execute_cmd_snap(args, callback_url)
        packed_args = [args, callback_url]
        _WORKERS.starmap_async(helpers.execute_cmd_snap, product(packed_args, repeat=2))
    except Exception as e:
        return "`ERROR` " + str(e)

    return helpers.ack(req_body['command'], req_body['text'])


@smartgate_api.route("/logs", methods=["POST"])
def ocr_logs():
    """
    Get ocr logs for particular yard as attachment
    """
    req_body = request.form
    try:
        helpers.validate_req(config._SLASH_CMD_LOG, req_body['token'])
        args = helpers.match_cmd(
                    config._SLASH_CMD_LOG, 
                    req_body['command'], 
                    req_body['text']
                )
        callback_url = req_body['response_url']
        packed_args = [args, callback_url]
        _WORKERS.starmap_async(helpers.execute_cmd_logs, product(packed_args, repeat=2))
    except Exception as e:
        return f"`Error` {e}"
    
    return helpers.ack(req_body['command'], req_body['text'])