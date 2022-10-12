# UDL.AI Python API

`udlai` is a way of interacting with the UDL.AI platform for location intelligence using a convenient Python API.

Note, that to use the `udlai`, you will need to obtain an access token. See [udl.ai](https://udl.ai) for details.

### Installation

`udlai` can be installed either from `PyPI` or `conda-forge`.

```sh
pip install udlai
```

Or

```sh
conda install -c conda-forge udlai
# or alternatively
mamba install -c conda-forge udlai
```

## Features

In the near future, `udlai` will offer a convenient interface to all parts of the UDL.AI platform. At the moment, only the feature API module is available, allowing you to retrieve data from the UDL.AI data warehouse.

### Feature API

Using the token received from UDL you will be able to perform the following tasks:

#### Fetch the list of attributes

Get a list of all of the attributes the user has access to, completed with their metadata and description.

```py
>>> udlai.attributes(token)
      id                       name  ...  year value_formatter
0      1       Buildings floorspace  ...  2013            None
1      2        Buildings footprint  ...  2013            None
2      3                     Height  ...  2013            None
3      4                    Stories  ...  2013            None
4      9                   box_area  ...  2013            None
..   ...                        ...  ...   ...             ...
234  283             usefit_ind_old  ...     0            None
235  288  Distance secondary school  ...  None            None
236  294            Price 2 bedroom  ...  None            None
237  295            Price 3 bedroom  ...  None            None
238  296           Price 4 bedrooms  ...  None            None

[239 rows x 22 columns]
```

#### Fetch specific feature details

Get the properties, description and summary statistics of a specific attribute.

```py
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
```

#### Fetch feature values for a given coordinate(s)

Get the feature values for a provided coordinate location or locations.

```py
>>> udlai.features(token, 47.37, 8.54, [10, 11, 22], index_by="name")
box_length                 104
box_perim                  335
obj_compact    2.2064113123322
Name: (47.37, 8.54), dtype: object
```

#### Fetch a summary over an area of interest

Get the summary statistics of an attribute within a specific area.

```py
>>> udlai.aggregates(token, shapely_geom, [10, 12], index_by='name')
                  sum       mean  median   min    max        std
box_length  12921.0  94.313869    94.0  19.0  135.0  30.600546
box_width   13118.0  95.751825   100.0  29.0  142.0  30.870646
```

## Contact person

**Martin Fleischmann** (@martinfleis)

m.fleischmann@urbandatalab.net
