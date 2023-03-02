"""
Copyright 2023- UrbanDataLab AG

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

Contact: Martin Fleischmann <m.fleischmann@urbandatalab.net>, 2023

---

Definition of the geocoding API.

"""
import pandas as pd
import requests

from .feature_api import _propagate_error

API_URL = "https://api.udl.ai/api/v1/public"


def geocode_structured(token, df):
    """Geocode addresses from a semantically structured DataFrame.

    The DataFrame must have four columns ``["street", "number", "postcode", "town"]``
    (no more, no less) following this example:

    .. code-block::

                  street  number  postcode    town
        0  Riedgrabenweg      15      8050  Zurich
        1  Butzenstrasse      35      8038  Zurich

    It returns the addresses as they are known in the database with a score
    denoting the quality of match between the original and the geocoded address. Score
    1 means 1:1 match, score 0 means no match.

    Parameters
    ----------
    token : str
        API token assigned to a user
    df : DataFrame
        DataFrame containing the structured addresses following the example above.

    Returns
    -------
    pandas.DataFrame
        DataFrame with the geocoded address (not the original) and the matching score

    Examples
    --------
    >>> df = pd.DataFrame(
    ...     {
    ...         "street": {0: "Riedgrabenweg", 1: "Butzenstrasse"},
    ...         "number": {0: 15, 1: 35},
    ...         "postcode": {0: 8050, 1: 8038},
    ...         "town": {0: "Zurich", 1: "Zurich"},
    ...     }
    ... )
    >>> df
              street  number  postcode    town
    0  Riedgrabenweg      15      8050  Zurich
    1  Butzenstrasse      35      8038  Zurich

    >>> udlai.geocode_structured(token, df)
              street number postcode     town   latitude  longitude     score
    0  riedgrabenweg     15     8050  zuerich  47.406742   8.558574  0.980769
    1  butzenstrasse     35     8038  zuerich  47.340733   8.526516  0.980769

    """
    json_data = {"addresses": df.to_dict("records")}
    response = requests.post(
        f"{API_URL}/geocoding/structured/",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json=json_data,
    )
    if response.status_code == 200:
        return pd.DataFrame([r["address"] for r in response.json()["addresses"]])

    _propagate_error(response)


def geocode_unstructured(token, addresses):
    """Geocode addresses from an unstructred string

    If you have a single string representing the whole address, use this function.

    It returns the addresses as they are known in the database with a score
    denoting the quality of match between the original and the geocoded address. Score
    1 means 1:1 match, score 0 means no match.


    Parameters
    ----------
    token : str
        API token assigned to a user
    addresses : list
        list of strings representing addresses

    Returns
    -------
    pandas.DataFrame
        DataFrame with the geocoded address (not the original) and the matching score

    Examples
    --------
    >>> addresses = [
    ...     "Riedgrabenweg 15, 8050 Zürich",
    ...     "Butzenstrasse 35, 8038 Zürich, Switzerland",
    ... ]
    >>> udlai.geocode_unstructured(token, addresses)
              street number postcode     town   latitude  longitude     score
    0  riedgrabenweg     15     8050  zuerich  47.406742   8.558574  0.942308
    1  butzenstrasse     35     8038  zuerich  47.340733   8.526516  0.942308
    """
    json_data = {"addresses": [{"address": a} for a in addresses]}
    response = requests.post(
        f"{API_URL}/geocoding/unstructured/",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json=json_data,
    )
    if response.status_code == 200:
        return pd.DataFrame([r["address"] for r in response.json()["addresses"]])

    _propagate_error(response)
