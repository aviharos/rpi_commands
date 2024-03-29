﻿# -*- coding: utf-8 -*-
"""
A set of modules for interacting with the Orion broker

The Orion host and port are read from the environment variables

Environment variables:
    ORION_HOST: the URL of the Orion broker
    ORION_PORT: the port of the Orion broker

Raises:
    RuntimeError: if the Orion_HOST is not set
"""
# Standard Library imports
import os

# PyPI packages
import requests

# Custom imports
# from modules.log_it import log_it
from Logger import getLogger

logger_Orion = getLogger(__name__)

# environment variables
ORION_HOST = os.environ.get("ORION_HOST")
if ORION_HOST is None:
    raise RuntimeError("Critical: ORION_HOST environment variable is not set")

ORION_PORT = os.environ.get("ORION_PORT")
if ORION_PORT is None:
    default_port = 1026
    logger_Orion.warning(
        f"Warning: ORION_PORT environment variable not set, using default value: {default_port}"
    )
    ORION_PORT = default_port


def getRequest(url: str):
    """Send a GET request to Orion

    Args:
        url (str): any Orion that is suitable for GET requests

    Returns:
        the response status code and the json

    Raises:
        RuntimeError: when the request fails for any reason
        ValueError: if the json parsing fails
    """
    try:
        response = requests.get(url)
        response.close()
    except Exception as error:
        raise RuntimeError(f"Get request failed to URL: {url}") from error

    else:
        try:
            response.json()
        except requests.exceptions.JSONDecodeError as error:
            raise ValueError(
                f"The JSON could not be decoded after GET request to {url}. Response:\n{response}"
            ) from error
        return response.status_code, response.json()

def is_reachable():
    """Return True if the OCB is reachable, False otherwise

    Args:
        None

    Returns:
        Boolean:
            True if the OCB is reachable
            False otherwise
    """
    url = f"http://{ORION_HOST}:{ORION_PORT}/version"
    try:
        status_code, _ = getRequest(url)
        return status_code == 200
    except Exception as error:
        logger_Orion.error(f"Error while trying to reach Orion: {error}")
        return False

def get(object_id: str, host: str=ORION_HOST, port: int =ORION_PORT):
    """Get an object from Orion identified by the ID

    Args:
        object_id (str): the Orion object id
        host (str): Orion host. Default: ORION_HOST environment variable
        port (int): Orion port. Default: ORION_PORT environment variable

    Returns:
        The object in JSON format idenfitied by object_id

    Raises:
        RuntimeError: if the get request's status code is not 200
    """
    url = f"http://{host}:{port}/v2/entities/{object_id}"
    logger_Orion.debug(f"Get: {url}")
    status_code, json_ = getRequest(url)
    if status_code != 200:
        raise RuntimeError(
            f"Failed to get object from Orion broker:{object_id}, status_code:{status_code}; no OEE data"
        )
    return json_


def exists(object_id: str):
    """Check if an object exists in Orion

    Args:
        object_id (str): the object's id in Orion

    Returns:
        True if the object idenfitied by object_id exists,
        False otherwise.
    """
    try:
        get(object_id)
        return True
    except RuntimeError:
        return False


def getWorkstations():
    """Download all Workstation objects at once from Orion

    Returns:
        A list of the Workstation objects

    Raises:
        RuntimeError: if the get request's status_code is not 200
    """
    url = f"http://{ORION_HOST}:{ORION_PORT}/v2/entities?type=i40Asset&q=i40AssetType==Workstation"
    status_code, workstations = getRequest(url)
    if status_code != 200:
        raise RuntimeError(
            f"Critical: could not get Workstations from Orion with GET request to URL: {url}"
        )
    return workstations


def update(objects: list):
    """Updates the objects in Orion

    This method takes an iterable (objects) that contain Orion objects
    then updates them in Orion.
    If an object already exists, it will be overwritten. More information:
    https://github.com/FIWARE/tutorials.CRUD-Operations#six-request

    Args:
        objects: an iterable containing Orion objects

    Raises:
        TypeError: if the objects does not contain an iterable
        RuntimeError: if the POST request's status code is not 204
    """
    logger_Orion.debug(f"update: objects: {objects}")
    url = f"http://{ORION_HOST}:{ORION_PORT}/v2/op/update"
    try:
        data = {"actionType": "append", "entities": list(objects)}
        logger_Orion.debug(f"update: data: {data}")
    except TypeError as error:
        raise TypeError(
            f"The objects {objects} are not iterable, cannot make a list. Please, provide an iterable object"
        ) from error
    response = requests.post(url, json=data)
    if response.status_code != 204:
        raise RuntimeError(
            f"Failed to update objects in Orion.\nStatus_code: {response.status_code}\nObjects:\n{objects}"
        )
    else:
        return response.status_code

def update_attribute(object_id: str, attribute_name: str, attribute_type: str, attribute_value):
    """Updates the object's given attribute in Orion

    This method takes an object id and an attribute name and value pair
    then updates the specified attribute with the given value in Orion.
    If the attribute already exists, it will be overwritten. More information:
    https://github.com/FIWARE/tutorials.CRUD-Operations#batch-create-new-data-entities-or-attributes

    Args:
        object_id (str): the object's id in Orion
        attribute_name (str): the specified attribute's name
        attribute_type (str): the specified attribute's type
        attribute_value (string or dict): the specified attribute's new value

    Raises:
        RuntimeError: if the POST request's status code is not 204
    """
    logger_Orion.debug(f"""update_attribute:
object_id: {object_id}
attribute_name: {attribute_name}
attribute_value: {attribute_value}""")
    if not exists(object_id=object_id):
        raise RuntimeError(f"Object {object_id} does not exist")
    url = f"http://{ORION_HOST}:{ORION_PORT}/v2/op/update"
    logger_Orion.debug(f"update_attribute: url: {url}")
    payload = {
        "id": object_id,
        attribute_name: {
            "type": attribute_type,
            "value": attribute_value
            }
        }
    data = {
        "actionType": "append",
        "entities": [payload]
        }
    logger_Orion.debug(f"update_attribute: data: {data}")
    response = requests.post(url, json=data)
    if response.status_code != 204:
        raise RuntimeError(
            f"Failed to update attribute in Orion. Status_code: {response.status_code}"
        )
    else:
        return response.status_code

