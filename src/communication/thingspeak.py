#
#   Module for interacting with ThingSpeak.
#   Samuel Dewan - 2020
#

import requests
import re

class Channel:
    WRITE_URL = "https://api.thingspeak.com/update.json"
    READ_URL = "https://api.thingspeak.com/channels/{}/feeds.json"
    FIELD_REGEX = re.compile("^field([1-8]{1})$")

    def __init__(self, chan_num, read_key=None, write_key=None):
        self.chan_num = chan_num
        self.read_key = read_key
        self.write_key = write_key
        # Generate URLs specific to this channel
        self.write_url = Channel.WRITE_URL
        self.read_url = Channel.READ_URL.format(self.chan_num)
        # Fetch channel information
        self.info = None
        self._update_channel_info()

    def _update_channel_info(self):
        r = requests.get(self.read_url, params={"key": self.read_key,
                                                "results": 0})
        self.info = r.json()['channel']

    def _get_field_names(self):
        names = dict()
        for key, value in self.info.items():
            if Channel.FIELD_REGEX.match(key) is not None:
                names[value] = key
        return names

    def _get_fields_from_dict(self, data):
        fields = dict()
        field_names = self._get_field_names()
        for key,value in data.items():
            if Channel.FIELD_REGEX.match(key) is not None:
                # Key is already a valid field identifier
                fields[key] = value
            elif key in field_names:
                # Key is a field name from this channel
                fields[field_names[key]] = value
        return fields

    def write(self, data, timestamp=None):
        if timestamp is not None:
            timestamp = timestamp.astimezone().isoformat()
        fields = dict()
        if isinstance(data, list):
            # Data is a list, assign each item to a field sequentialy
            for index, value in enumerate(data):
                if i >= 8:
                    # Max of 8 fields in a thingspeak channel
                    return
                fields[f"field{index + 1}"] = value
        elif isinstance(data, dict):
            # Data is a dictionary, go through it and make sure that the keys
            # are valid
            fields = self._get_fields_from_dict(data)
        else:
            # Just try and send the data as field1
            fields["field1"] = data
        if len(fields) == 0:
            return None
        # Append key and timestamp to fields
        fields["key"] = self.write_key
        fields["created_at"] = timestamp
        # Do the request
        r = requests.post(self.write_url, params=fields)
        if r.ok:
            return r.json()
        else:
            return None

    def read(self, count=None, minutes=None, start=None):
        if start is not None:
            start = start.astimezone().isoformat()
        parameters = {  
                        "key": self.read_key,
                        "results": count,
                        "minutes": minutes,
                        "start": start
                     }
        r = requests.get(self.read_url, params=parameters)
        result = r.json()
        self.info = result['channel']
        return result["feeds"]

    def get_last_entry_id(self):
        self._update_channel_info()
        entry_id = self.info['last_entry_id']
        return 0 if entry_id is None else entry_id

