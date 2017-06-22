import requests
import os

main_url = 'http://prod.ivtr-od.tpg.ch/v1/'

class tpgScraper:
    def __init__(self, key):
        r = requests.get(os.path.join(main_url, 'GetNextDepartures?key={}&stopCode=BHET'.format(key)))
        assert r.status_code == 200, "ERROR: Invalid API key"
        self._api_key    = key
        self._stops_dict = requests.get(os.path.join(main_url, 'GetStops?key={}'.format(self._api_key))).json()['stops']

    def get_stop_code(self, req_stop):
        for stop in self._stops_dict:
            if req_stop.upper() in stop['stopName']:
                return stop['stopCode']
        return None

    def get_lines(self, req_stop):
        output_str = ''
        stop_template='''
Stop Name: {name}
-------------------------------
Line\t\tDestination

{lines}
-------------------------------
'''
        lines_tuples = {}
        for stop in self._stops_dict:
            if req_stop.upper() in stop['stopName']:
               lines_tuples[stop['stopName']] = []
               lines = []
               for connection in stop['connections']:
                  lines.append('{}\t\t{}'.format(connection['lineCode'],
                                              connection['destinationName']))
               lines_tuples[stop['stopName']].append((connection['lineCode'],
                                                    connection['destinationName']))
               output_str += stop_template.format(name=stop['stopName'], lines='\n'.join(lines))
        print(output_str)
        return lines_tuples, output_str

    def get_departures(self, req_stop):
        output_str = ''
        stop_template='''
Stop Name: {name}
-------------------------------
Time\tLine\t\tDestination

{lines}
-------------------------------
'''
        code = self.get_stop_code(req_stop)
        url = os.path.join(main_url, 'GetNextDepartures?key={}&stopCode={}'.format(self._api_key, code))
        listing = requests.get(url).json()['departures']
        name = requests.get(url).json()['stop']['stopName']
        output_strs = []
        output_tuples = []
        for entry in listing:
            output_tuples.append((entry['waitingTime'].replace('&gt;',''), entry['line']['lineCode'], entry['line']['destinationName']))
            output_strs.append('{}\t{}\t\t{}'.format(*output_tuples[-1]))
        output = stop_template.format(name=name, lines='\n'.join(output_strs))
        print(output)
        return output_tuples, output
