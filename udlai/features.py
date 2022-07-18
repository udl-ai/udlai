"""
Copyright 2022 UrbanDataLab AG

MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy of this
software and associated documentation files (the "Software"), to deal in the Software
without restriction, including without limitation the rights to use, copy, modify,
merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT
OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

Contact: Martin Fleischmann <m.fleischmann@urbandatalab.net>, 2022

---

Definition of the main API.

"""

import warnings
from collections import defaultdict

import pandas as pd
import requests

API_URL = "https://dev-api.udl.ai/api/v1/public"


def _flatten_dict(d, parent_key="", sep="."):
    """recursive function to flatten the response"""
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, dict):
            items.extend(_flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            for i in v:
                items.extend(_flatten_dict(i, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


# Function attribute GET (Fetch the features list)
def attributes(token):
    """
    Returns the all of the attributes that user has access to. User is assigned to token
    on creation and the list of attributes is managed by the UDL administrator, if you
    would like to have access to other attributes, please contact UDL.

    See the documentation of the underlying REST API
    https://dev-api.udl.ai/api/v1/docs/public/attributes#operation/attributes_list

    Parameters
    ----------
    token : str
        API token assigned to a user

    Returns
    -------
    attributes : pandas.DataFrame
        pandas.DataFrame with attributes and their metadata
    """

    # calling the API
    response = requests.get(
        f"{API_URL}/attributes/",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )

    return pd.DataFrame([_flatten_dict(i) for i in response.json()])


# Function attributes GET (Fetch the attributes list)
def attribute_detail(token, attribute_id):
    """
    Fetch single entity of attribute based on the ID of the attribute provided as a
    parameter.

    See the documentation of the underlying REST API
    https://dev-api.udl.ai/api/v1/docs/public/attributes#operation/attributes_read

    Parameters
    ----------
    token : str
        API token assigned to a user
    attribute_id : int
        ID of the queried attribute. Use ``udlai.attributes`` to get a list of IDs

    Returns
    -------
    attribute_details : pandas.Series
    """

    # calling the API
    response = requests.get(
        f"{API_URL}/attributes/{attribute_id}/",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )

    return pd.Series(_flatten_dict(response.json()))


def features(token, latitude, longitude, attribute_id, index_by="id"):
    """
    An API Endpoint that will return the attributes for provided
    coordinates. The API expects the attribute IDs, that can be fetched using
    ``udlai.attributes`` function.

    You can pass individual coordinates or arrays of the same length.

    Parameters
    ----------
    token : str
        API token assigned to a user
    latitude : float or list-like
        latitude or list-like of latitudes denoting the location(s) for a query
    longitude : float or list-like
        longitude or list-like of longitudes denoting the location(s) for a query
    attribute_id : int or list-like
        ID(s) of the queried attribute. Use ``udlai.attributes`` to get a list of IDs.
    index_by : {"id", "name"}
        One of the ``{"id", "name"}`` denoting whether the output should be indexed
        using the original attribute ID or its name

    Returns
    -------
    features : pandas.Series or pandas.DataFrame
        returns Series for a single point or a DataFrame for multiple points

    """
    multi = pd.api.types.is_list_like(latitude)

    if not pd.api.types.is_list_like(attribute_id):
        attribute_id = [attribute_id]

    if not multi:
        json_data = {
            "coordinates": {
                "latitude": latitude,
                "longitude": longitude,
            },
            "attributes": [
                {
                    "id": x,
                }
                for x in attribute_id
            ],
        }

        # calling the API
        response = requests.post(
            f"{API_URL}/features/",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json=json_data,
        )

        dict_raw = response.json()

        if not dict_raw["values"]:
            warnings.warn("no match", stacklevel=1, category=UserWarning)
            # TODO: test this

        clean = {a["attribute"][index_by]: a["value"] for a in dict_raw["values"]}

        return pd.Series(clean, name=f"({latitude}, {longitude})", dtype=object)

    json_data = {
        "coordinates": [
            {
                "latitude": lat,
                "longitude": lon,
            }
            for lat, lon in zip(latitude, longitude)
        ],
        "attributes": [
            {
                "id": x,
            }
            for x in attribute_id
        ],
    }

    response = requests.post(
        f"{API_URL}/features/multi/",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json=json_data,
    )

    d = defaultdict(list)
    for pt in response.json()["results"]:
        d["latitude"].append(pt["coordinates"]["latitude"])
        d["longitude"].append(pt["coordinates"]["longitude"])
        if pt["values"]:
            for attr in pt["values"]:
                d[attr["attribute"][index_by]].append(attr["value"])
        else:
            for k in d.keys():
                if k not in ["latitude", "longitude"]:
                    d[k].append(None)

    return pd.DataFrame(d)
