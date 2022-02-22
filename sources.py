from lumen.sources.base import Source
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from lumen.sources.base import cached
import os
from pathlib import Path
import hashlib

class IkonReport(Source):
    url = 'https://www.onthesnow.com/ikon-pass/skireport'
    source_type = 'ski'

    def _get_ikon_table(self):
        page=requests.get(self.url)
        soup = BeautifulSoup(page.text, 'lxml')
        tbodies = soup.find_all('tbody')
        tbody = tbodies[0]
        spots = []
        for row in tbody.findChildren(recursive=False)[:-1]:
            res = {}
            row_items = row.findChildren(recursive=False)
            if len(row_items) < 5:
                continue
            for i in range(len(row_items)):
                if i == 0:
                    res['name'] = row_items[0].find('span').getText()
                    res['last_update'] = row_items[0].find('time').getText()
                    res['report_link'] = 'https://www.onthesnow.com' + row_items[0].find('a', href=True)['href']
                if i==1:
                    res['snowfall_amount'] = row_items[1].find('span', {'class': 'h4 styles_h4__318ae'}).getText()
                    res['last_snowfall'] = row_items[1].find('time').getText()
                if i==2:
                    res['base_depth'] = row_items[2].find('span', {'class', 'h4 styles_h4__318ae'}).getText()
                    res['main_surface'] = row_items[2].find('div').getText()
                if i==3:
                    open_trails = row_items[3].find('span', {'class', 'h4 styles_h4__318ae'}).getText()
                    res['open_trails'], res['total_trails'] = open_trails.split('/')
                if i==4:
                    open_lifts = row_items[4].find('span', {'class', 'h4 styles_h4__318ae'} ).getText()
                    res['open_lifts'], res['total_lifts'] = open_lifts.split('/')
            spots.append(res)

        return pd.DataFrame(spots)

    @cached(with_query=True)
    def get(self, table, **kwargs):
        if table == 'ikon':
            return self._get_ikon_table()

    def _get_key(self, table, **query):
        key = super()._get_key(table, **query)
        now = datetime.now()
        return str(key) + now.strftime('%Y %M %d')

    def get_tables(self):
        return ['ikon']

    def _get_cache(self, table, **query):
        query.pop('__dask', None)
        key = self._get_key(table, **query)
        if key in self._cache:
            return self._cache[key], not bool(query)
        elif self.cache_dir:
            sha = hashlib.sha256(str(key).encode('utf-8')).hexdigest()
            filename = f'{sha}_{table}.parq'
            path = os.path.join(self.root, self.cache_dir, filename)
            if os.path.isfile(path) or os.path.isdir(path):
                if 'dask.dataframe' in sys.modules:
                    import dask.dataframe as dd
                    return dd.read_parquet(path), not bool(query)
                return pd.read_parquet(path), not bool(query)
        return None, not bool(query)

    def _set_cache(self, data, table, write_to_file=True, **query):
        query.pop('__dask', None)
        key = self._get_key(table, **query)
        self._cache[key] = data
        if self.cache_dir and write_to_file:
            path = os.path.join(self.root, self.cache_dir)
            Path(path).mkdir(parents=True, exist_ok=True)
            sha = hashlib.sha256(str(key).encode('utf-8')).hexdigest()
            filename = f'{sha}_{table}.parq'
            try:
                data.to_parquet(os.path.join(path, filename))
            except Exception as e:
                self.param.warning(f"Could not cache '{table}' to parquet"
                                   f"file. Error during saving process: {e}")