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
from geopandas import GeoDataFrame
import requests
from geojson import Feature, Point, FeatureCollection

from topo import get_state, get_huc8, get_place, get_county


def rget(url, callback=None, recursive=True):
    items = []

    def _get(u):
        print('url={}'.format(u))
        resp = requests.get(u)
        print('resp={}'.format(resp))
        j = resp.json()

        if callback:
            callback(items, j)
        else:
            try:
                items.extend(j['value'])
            except KeyError:
                items.append(j)

        try:
            next = j['@iot.nextLink']
        except KeyError:
            return
        if recursive:
            _get(next)

    _get(url)
    return items


def nmbgmr_props_factory(loc, thing):
    props = thing['properties']
    props['id'] = loc['name']
    props['agency_id'] = thing['name']
    props.pop('@nmbgmr.point_id', None)
    try:
        wd = float(props.pop('welldepth', 0))
    except BaseException:
        wd = 0
    props['welldepth'] = float(wd)

    return props


def ose_props_factory(loc, thing):
    props = thing['properties']
    props['id'] = loc['name']
    props['agency_id'] = thing['name']
    return props


def get_geojson_features(url, factory):
    def feature_factory(loc, thing):
        props = factory(loc, thing)
        props['sta'] = '{}?$expand=Datastreams/Observations'.format(thing['@iot.selfLink'])
        props['state'] = get_state(loc)
        props['huc8'] = get_huc8(loc)
        props['place'] = get_place(loc)
        props['county'] = get_county(loc)

        print('construct: {}. properties={}'.format(thing['name'], props))
        return Feature(properties=props,
                       geometry=Point(loc['location']['coordinates']))

    items = rget(url, recursive=True)
    return FeatureCollection([feature_factory(i, thing) for i in items for thing in i['Things']])


def write_gpkg(fc, name='nmbgmr_wells'):
    # convert obj to a GeoDataFrame
    gdf = GeoDataFrame.from_features(fc['features'])

    # write to gpkg
    gdf.to_file('{}.gpkg'.format(name), driver='GPKG')


def main():
    # write nmbgmr wells
    # url = 'https://st.newmexicowaterdata.org/FROST-Server/v1.1/Locations?$expand=Things'
    # fs = get_geojson_features(url, nmbgmr_props_factory)
    # write_gpkg(fs)

    url = 'https://ose.newmexicowaterdata.org/FROST-Server/v1.1/Locations?$expand=Things'
    fs = get_geojson_features(url, ose_props_factory)
    write_gpkg(fs, 'ose_wells')


if __name__ == '__main__':
    main()
# ============= EOF =============================================
