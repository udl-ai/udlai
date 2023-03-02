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

import pandas as pd
import pytest
from shapely.geometry import shape

import udlai

token = os.environ.get("TOKEN")


def test_attributes():
    df = udlai.attributes(token)
    assert isinstance(df, pd.DataFrame)
    assert not df["id"].isna().any()
    assert df.shape[0] > 200
    assert df.shape[1] > 20


@pytest.mark.parametrize("attr_id", [113, 172, 0])
def test_attribute_detail(attr_id):
    if attr_id != 0:
        r = udlai.attribute_detail(token, attr_id)
        assert isinstance(r, pd.Series)
        assert r["id"] == attr_id
    else:
        with pytest.raises(ValueError, match="NotFound"):
            udlai.attribute_detail(token, attr_id)


class TestFeatures:
    @pytest.mark.parametrize("attr_id", [113, 172])
    def test_single(self, attr_id):
        r = udlai.features(token, 47.37, 8.54, attr_id)
        assert isinstance(r, pd.Series)
        assert attr_id in r.index
        assert r.shape == (1,)
        assert not pd.isna(r[attr_id])

    def test_missing(self):
        with pytest.raises(ValueError, match="Attribute `0` not assigned to the user."):
            udlai.features(token, 47.37, 8.54, 0)

    def test_location_empty(self):
        with pytest.warns(UserWarning, match="The location is not within the udl.ai"):
            r = udlai.features(token, 47.37, 10.54, 113)
            assert r.empty

    def test_more_attributes(self):
        r = udlai.features(token, 47.37, 8.54, [113, 172], index_by="name")
        assert isinstance(r, pd.Series)
        assert "net_betw_speed" in r.index
        assert "freiz_300" in r.index
        assert r.shape == (2,)
        assert not pd.isna(113)

    def test_multi(self):
        lats = [47.3769267, 47.3769267, 48.3769267]
        lons = [8.5497381, 8.5417981, 8.9417981]
        with pytest.warns(UserWarning, match="Some of the locations are not within"):
            r = udlai.features(token, lats, lons, 113)
        assert isinstance(r, pd.DataFrame)
        assert r.shape == (3, 3)
        for c in ["latitude", "longitude", 113]:
            assert c in r.columns
        assert r[113].notna().sum() == 2

    def test_multi_attr(self):
        lats = [47.3769267, 47.3769267, 48.3769267]
        lons = [8.5497381, 8.5417981, 8.9417981]
        with pytest.warns(UserWarning, match="Some of the locations are not within"):
            r = udlai.features(token, lats, lons, [113, 172], index_by="name")
        assert isinstance(r, pd.DataFrame)
        assert r.shape == (3, 4)
        for c in ["latitude", "longitude", "net_betw_speed", "freiz_300"]:
            assert c in r.columns
        assert r["net_betw_speed"].notna().sum() == 2


class TestAggregate:
    def setup_method(self):
        self.geojson = {
            "type": "Polygon",
            "coordinates": [
                [
                    [8.5367, 47.3712],
                    [8.5406, 47.3712],
                    [8.5406, 47.3739],
                    [8.5367, 47.3739],
                    [8.5367, 47.3712],
                ]
            ],
        }
        self.shapely_geom = shape(self.geojson)

    def test_single_shapely(self):
        r = udlai.aggregates(token, self.shapely_geom, 113)
        assert isinstance(r, pd.DataFrame)
        assert r.shape == (1, 6)
        for c in ["max", "mean", "median", "min", "std", "sum"]:
            assert c in r.columns
        assert r.loc[113].notna().sum() == 6

    def test_single_shapely_name(self):
        r = udlai.aggregates(token, self.shapely_geom, 113, index_by="name")
        assert isinstance(r, pd.DataFrame)
        assert r.shape == (1, 6)
        for c in ["max", "mean", "median", "min", "std", "sum"]:
            assert c in r.columns
        assert r.loc["net_betw_speed"].notna().sum() == 6

    def test_multi_shapely(self):
        r = udlai.aggregates(token, self.shapely_geom, [113, 172])
        assert isinstance(r, pd.DataFrame)
        assert r.shape == (2, 6)
        for c in ["max", "mean", "median", "min", "std", "sum"]:
            assert c in r.columns
        assert r.loc[113].notna().sum() == 6

    def test_multi_shapely_name(self):
        r = udlai.aggregates(token, self.shapely_geom, [113, 172], index_by="name")
        assert isinstance(r, pd.DataFrame)
        assert r.shape == (2, 6)
        for c in ["max", "mean", "median", "min", "std", "sum"]:
            assert c in r.columns
        assert r.loc["net_betw_speed"].notna().sum() == 6
        assert r.loc["freiz_300"].notna().sum() == 6

    def test_single_geojson(self):
        r = udlai.aggregates(token, self.geojson, 113)
        assert isinstance(r, pd.DataFrame)
        assert r.shape == (1, 6)
        for c in ["max", "mean", "median", "min", "std", "sum"]:
            assert c in r.columns
        assert r.loc[113].notna().sum() == 6


def test_error_propagation():
    with pytest.raises(ValueError, match="AuthenticationFailed"):
        udlai.attributes("wrong_token")

    with pytest.raises(ValueError, match="AuthenticationFailed"):
        udlai.attribute_detail("wrong_token", 113)

    with pytest.raises(ValueError, match="AuthenticationFailed"):
        udlai.features("wrong_token", 47.37, 8.54, 0)
