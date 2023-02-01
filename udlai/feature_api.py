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

API_URL = "https://api.udl.ai/api/v1/public"


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


def _propagate_error(response):
    """propagate error from the API"""
    from requests.exceptions import JSONDecodeError

    try:
        r = response.json()
        raise ValueError(f'{r["error"]}: {r["details"]} [status {r["status"]}]')
    except JSONDecodeError:
        raise ValueError(response.text)


def attributes(token):
    """
    Returns the all of the attributes that user has access to. User is assigned to token
    on creation and the list of attributes is managed by the UDL administrator, if you
    would like to have access to other attributes, please contact UDL.

    See the documentation of the underlying REST API
    https://api.udl.ai/api/v1/docs/public/attributes#operation/attributes_list

    Parameters
    ----------
    token : str
        API token assigned to a user

    Returns
    -------
    attributes : pandas.DataFrame
        pandas.DataFrame with attributes and their metadata

    Examples
    --------
    >>> udlai.attributes(token)
          id  ... value_formatter.options.multiply
    0     10  ...                              NaN
    1     58  ...                              NaN
    2     60  ...                              NaN
    3     61  ...                              NaN
    4     62  ...                              NaN
    ..   ...  ...                              ...
    238  284  ...                              NaN
    239  285  ...                              NaN
    240  286  ...                              NaN
    241  287  ...                              NaN
    242  288  ...                              1.0
    [243 rows x 31 columns]
    """

    # calling the API
    response = requests.get(
        f"{API_URL}/attributes/",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    if response.status_code == 200:
        return pd.DataFrame([_flatten_dict(i) for i in response.json()])

    _propagate_error(response)


def attribute_detail(token, attribute_id):
    """
    Fetch single entity of attribute based on the ID of the attribute provided as a
    parameter.

    See the documentation of the underlying REST API
    https://api.udl.ai/api/v1/docs/public/attributes#operation/attributes_read

    Parameters
    ----------
    token : str
        API token assigned to a user
    attribute_id : int
        ID of the queried attribute. Use ``udlai.attributes`` to get a list of IDs

    Returns
    -------
    attribute_details : pandas.Series

    Examples
    --------
    >>> udlai.attribute_detail(token, 22)
    id                                                                     22
    name                                                          obj_compact
    description             Compactness of object: C=obj_peri²/(4*box_area*π)
    short_description                                                    None
    unit                                                                    -
    tags.id                                                                 4
    tags.name                                                      Morphology
    main_tag.id                                                             4
    main_tag.name                                                  Morphology
    data_version                                                         None
    data_last_update                                                     None
    data_processor                                                        UDL
    source_provider                                            Swiss Topo TLM
    source_provider_link    https://www.swisstopo.admin.ch/de/wissen-fakte...
    coverage_general                                              Switzerland
    epsg_code                                                            2056
    min_value                                                        0.960614
    max_value                                                       24.141694
    standard_deviation                                               0.893447
    mean                                                             1.647733
    year                                                                 2013
    value_formatter                                                      None
    dtype: object
    """

    # calling the API
    response = requests.get(
        f"{API_URL}/attributes/{attribute_id}/",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    if response.status_code == 200:
        return pd.Series(_flatten_dict(response.json()))

    _propagate_error(response)


def features(token, latitude, longitude, attribute_id, index_by="id"):
    """
    An API Endpoint that will return the attributes for provided
    coordinates. The API expects the attribute IDs, that can be fetched using
    ``udlai.attributes`` function.

    You can pass individual coordinates or arrays of the same length.

    https://api.udl.ai/api/v1/docs/public/attributes#tag/features

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

    Examples
    --------
    Single point and a single attribute:

    >>> udlai.features(token, 47.37, 8.54, 22)
    22    2.2064113123322
    Name: (47.37, 8.54), dtype: object

    Single point and multiple attributes, indexed by name

    >>> udlai.features(token, 47.37, 8.54, [10, 11, 22], index_by="name")
    box_length                 104
    box_perim                  335
    obj_compact    2.2064113123322
    Name: (47.37, 8.54), dtype: object

    Multiple points and a single attribute
    (the last point is outside of the covered area):

    >>> lats = [47.3769267, 47.3769267, 48.3769267]
    >>> lons = [8.5497381, 8.5417981, 8.9417981]
    >>> udlai.features(token, lats, lons, 10)
        latitude  longitude    10
    0  47.376927   8.549738   294
    1  47.376927   8.541798    44
    2  48.376927   8.941798  None

    Multiple points and a multiple attributes
    (the last point is outside of the covered area):

    >>> lats = [47.3769267, 47.3769267, 48.3769267]
    >>> lons = [8.5497381, 8.5417981, 8.9417981]
    >>> ids = [11, 12, 13, 14, 15, 16, 22]
    >>> udlai.features(token, lats, lons, ids)
        latitude  longitude    11    12  ...     14    15    16                22
    0  47.376927   8.549738  1106   259  ...  86215  1041   166  13.1956982144114
    1  47.376927   8.541798   259    85  ...   6860   294    47  1.60758471341658
    2  48.376927   8.941798  None  None  ...   None  None  None              None
    [3 rows x 9 columns]

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
        if response.status_code == 200:

            dict_raw = response.json()

            if "error" in dict_raw:
                raise ValueError(dict_raw["details"][0])

            if not dict_raw["values"]:
                warnings.warn(
                    "The location is not within the udl.ai database. "
                    "Have you passed correct coordinates?",
                    stacklevel=2,
                    category=UserWarning,
                )

            clean = {a["attribute"][index_by]: a["value"] for a in dict_raw["values"]}

            return pd.Series(clean, name=f"({latitude}, {longitude})", dtype=object)

        _propagate_error(response)

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

    if response.status_code == 200:

        d = defaultdict(list)
        missing = False
        for pt in response.json()["results"]:
            d["latitude"].append(pt["coordinates"]["latitude"])
            d["longitude"].append(pt["coordinates"]["longitude"])
            if pt["values"]:
                for attr in pt["values"]:
                    d[attr["attribute"][index_by]].append(attr["value"])
            else:
                missing = True
                for k in d.keys():
                    if k not in ["latitude", "longitude"]:
                        d[k].append(None)

        if missing:
            warnings.warn(
                "Some of the locations are not within the udl.ai database. "
                "Have you passed correct coordinates?",
                stacklevel=1,
                category=UserWarning,
            )

        return pd.DataFrame(d)

    _propagate_error(response)


def aggregates(token, geometry, attribute_id, index_by="id", grid_size=25):
    """
    An API Endpoint that will return the aggregates for provided
    geometry. The API expects the attribute IDs, that can be fetched using
    ``udlai.attributes`` function.

    You can pass a GeoJSON-encoded Polygon or MultiPolygon or a shapely.geometry.

    https://api.udl.ai/api/v1/docs/public/attributes#tag/aggregates

    Parameters
    ----------
    token : str
        API token assigned to a user
    geometry : GeoJSON-like dict or shapely.geometry
        Polygon or MultiPolygon geometry denoting the area of interest
    attribute_id : int or list-like
        ID(s) of the queried attribute. Use ``udlai.attributes`` to get a list of IDs.
    index_by : {"id", "name"}
        One of the ``{"id", "name"}`` denoting whether the output should be indexed
        using the original attribute ID or its name
    grid_size : {25, 75, 225, 675}
        Size of the grid to be queried.

    Returns
    -------
    aggregates : pandas.DataFrame

    Examples
    --------
    Shapely geometry and a single attribute.

    >>> udlai.aggregates(token, shapely_geom, 10)
        max       mean  median   min        std      sum
    10  135.0  94.313869    94.0  19.0  30.600546  12921.0

    Shapely geometry and a single attribute indexed by its name.

    >>> udlai.aggregates(token, shapely_geom, 10, index_by="name")
                  max       mean  median   min        std      sum
    box_length  135.0  94.313869    94.0  19.0  30.600546  12921.0

    Shapely geometry and a mutliple attributes indexed by their ID.

    >>> udlai.aggregates(token, shapely_geom, [10, 12])
            sum       mean  median   min    max        std
    10  12921.0  94.313869    94.0  19.0  135.0  30.600546
    12  13118.0  95.751825   100.0  29.0  142.0  30.870646

    Shapely geometry and a mutliple attributes indexed by their names.

    >>> udlai.aggregates(token, shapely_geom, [10, 12], index_by='name')
                    sum       mean  median   min    max        std
    box_length  12921.0  94.313869    94.0  19.0  135.0  30.600546
    box_width   13118.0  95.751825   100.0  29.0  142.0  30.870646

    GeoJSON-encoded geometry:

    >>> geojson = {
    ...     "type": "Polygon",
    ...     "coordinates": [
    ...         [
    ...             [8.5367, 47.3712],
    ...             [8.5406, 47.3712],
    ...             [8.5406, 47.3739],
    ...             [8.5367, 47.3739],
    ...             [8.5367, 47.3712],
    ...         ]
    ...     ],
    ... }
    >>> udlai.aggregates(token, geojson, 10)
        max       mean  median   min        std      sum
    10  135.0  94.268966    94.0  19.0  30.613916  13669.0
    """
    if not isinstance(geometry, dict):
        geometry = geometry.__geo_interface__  # shapely.geometry to geojson

    if not isinstance(attribute_id, list):
        attribute_id = [attribute_id]

    json_data = {
        "geometry": geometry,
        "attributes": [
            {
                "id": x,
            }
            for x in attribute_id
        ],
        "grid_size": f"grid{grid_size}",
    }

    response = requests.post(
        f"{API_URL}/aggregates/",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json=json_data,
    )

    if response.status_code == 200:
        d = {}
        for att in response.json()["results"]:
            d[att["attribute"][index_by]] = att["aggregates"]

        return pd.DataFrame(d).astype(float).T

    _propagate_error(response)
