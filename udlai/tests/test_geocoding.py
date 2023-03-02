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

Unit tests for UDL.AI Python API.

"""
import os

import numpy as np
import pandas as pd

import udlai

token = os.environ.get("TOKEN")


def test_geocode_structured():
    df = pd.DataFrame(
        {
            "street": {0: "Bielstrasse", 1: "Quellenstrasse"},
            "number": {0: "49", 1: "5"},
            "postcode": {0: 3273, 1: 9240},
            "town": {0: "Kappelen", 1: "Uzwil"},
        }
    )
    r = udlai.geocode_structured(token, df)
    assert r.shape == (2, 7)
    assert np.all(
        r.columns
        == ["street", "number", "postcode", "town", "latitude", "longitude", "score"]
    )
    assert not r.isna().any().any()


def test_geocode_unstructured():
    addresses = [
        "Klosbachstrasse 67, 8032 Zürich",
        "Dorfstrasse 40, 3184 Wünnewil-Flamatt, Switzerland",
    ]
    r = udlai.geocode_unstructured(token, addresses)
    assert r.shape == (2, 7)
    assert np.all(
        r.columns
        == ["street", "number", "postcode", "town", "latitude", "longitude", "score"]
    )
    assert not r.isna().any().any()
