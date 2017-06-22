import requests
import os
import tabulate

main_url = 'http://prod.ivtr-od.tpg.ch/v1/'

class tpg_client:
    '''Client for obtaining information from the TPG (Geneva Transport) API

         Arguments:
       
         key    API required to access the data feed
    '''
    def __init__(self, key):
        r = requests.get(os.path.join(main_url, 'GetNextDepartures?key={}&stopCode=BHET'.format(key)))
        assert r.status_code == 200, "ERROR: Invalid API key"
        self._api_key    = key
        self._stops_dict = requests.get(os.path.join(main_url, 'GetStops?key={}'.format(self._api_key))).json()['stops']

    def get_stop_code(self, req_stop):
        '''Return designated code for a given stop used for requests'''
        for stop in self._stops_dict:
            if req_stop.upper() in stop['stopName']:
                return stop['stopCode']
        return None

    def get_lines(self, req_stop):
        '''Returns the lines and terminal destinations for a given stop'''
        output_str = ''
        stop_template='''
Stop Name: {name}
-------------------------------

{lines}
-------------------------------
'''
        lines_tuples = {}
        for stop in self._stops_dict:
            if req_stop.upper() in stop['stopName']:
               lines_tuples[stop['stopName']] = []
               lines = []
               for connection in stop['connections']:
                  lines.append([connection['lineCode'], connection['destinationName']])
               lines_tuples[stop['stopName']].append((connection['lineCode'],
                                                    connection['destinationName']))
               output_str += stop_template.format(name=stop['stopName'], lines=tabulate.tabulate(lines, headers=['Line', 'Destination']))
        print(output_str)
        return lines_tuples, output_str

    def get_departures(self, req_stop, details=False):
        '''Returns the live departures for a given stop'''
        output_str = ''
        if details is False:
            headers = ['Time', 'Line', 'Destination']
            stop_template='''
Stop Name: {name}
-------------------------------

{lines}
-------------------------------
'''
        else:
            headers = ['Time', 'Line', 'Destination', 'Reliabilty', 'Vehicle Number']
            stop_template='''
Stop Name: {name}
-------------------------------

{lines}
-------------------------------
'''
        try:
            code = self.get_stop_code(req_stop)
        except:
            print("ERROR: Could not find stop code for request '{}",format(req_stop))
            return
        url = os.path.join(main_url, 'GetNextDepartures?key={}&stopCode={}'.format(self._api_key, code))
        assert requests.get(url).status_code == 200, "ERROR: Invalid Departures Request"
        listing = requests.get(url).json()['departures']
        name = requests.get(url).json()['stop']['stopName']
        output_strs = []
        output_tuples = []
        if details:
            for entry in listing:
                output_tuples.append((entry['waitingTime'].replace('&gt;',''), entry['line']['lineCode'], entry['line']['destinationName'], 
                                     'Reliable' if entry['reliability'] == 'F' else 'Theoretical', entry['vehiculeNo']))
                output_strs.append(list(output_tuples[-1]))
        else:
            for entry in listing:
                output_tuples.append((entry['waitingTime'].replace('&gt;',''), entry['line']['lineCode'], entry['line']['destinationName']))
                output_strs.append(list(output_tuples[-1]))
        output = stop_template.format(name=name, lines=tabulate.tabulate(output_strs, headers=headers))
        print(output)
        return output_tuples, output

    def get_disruptions(self):
        '''Return current disruption information'''
        url = os.path.join(main_url, 'GetDisruptions?key={}'.format(self._api_key))
        listing = requests.get(url).json()['disruptions']
        output_strs = ''
        output_tuples = []
        try:
            assert len(listing) > 0, "No disruptions found."
        except:
            print('No disruptions found')
            return (), 'No disruptions found' 
        for disruption in listing['disruptions']:
            output_strs += '----------------------------\n'
            output_strs += 'LINE {} - {}\n\n'.format(disruption['lineCode'], disruption['place'])
            output_strs += 'Affecting Services From: {}'.format(disruption['stopName'])
            output_strs += 'Summary: {}\n'.format(disruption['nature'])
            output_strs += '{}\n'.format(disruption['consequence'])
            output_tuples.append(disruption['lineCode'], disruption['place'], disruption['stopName'], disruption['nature'], disruption['consequence'])
        print(output_strs)
        return output_tuples, output_strs
