# ===============================================================================
# Copyright 2020 ross
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ===============================================================================
import os

import geojson
from shapely.geometry import shape, Point


def within(loc, regions, targetkey):
    locpt = Point(loc['location']['coordinates'])
    for feature in regions:
        p = shape(feature['geometry'])
        if p.contains(locpt):
            return feature['properties'][targetkey]


__cache__ = {}


def get_boundaries(name):
    if name not in __cache__:
        path = os.path.join('data', 'boundaries', name)
        with open(path, 'r') as rfile:
            __cache__[name] = geojson.load(rfile)['features']

    return __cache__[name]


def get_huc8(loc):
    regions = get_boundaries('wbdhu8_a_nm.geojson')
    return within(loc, regions, 'HUC8')


def get_place(loc):
    regions = get_boundaries('tl_2015_35_place.geojson')
    return within(loc, regions, 'GEOID')


def get_county(loc):
    regions = get_boundaries('tl_2018_nm_county.geojson')
    return within(loc, regions, 'GEOID')


def get_state(loc):
    return 35
# ============= EOF =============================================
