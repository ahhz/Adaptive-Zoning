# Copyright (c) 2025 Alex Hagen-Zanker
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import os
import configparser

def write_api_key_to_config(api_key, section, keyname, config_file):
    config = configparser.ConfigParser()

    # Check if the config file already exists
    if os.path.exists(config_file):
        config.read(config_file)

    if section not in config:
        config.add_section(section)

    config.set(section, keyname, api_key)

    try:
        with open(config_file, "w") as configfile:
            config.write(configfile)
        print(f"API key written to {config_file}")
    except IOError as e:
        print(f"Error writing to config file: {e}")

def read_api_key_from_config(section, keyname, config_file):
    config = configparser.ConfigParser()
    try:
        config.read(config_file)
        return config.get(section, keyname)
    except (configparser.NoSectionError, configparser.NoOptionError, FileNotFoundError):
        return None

def get_key(section, keyname, config_file):
    apikey = read_api_key_from_config(section, keyname, config_file)
    if not apikey:
        print("Enter your " + section + " " + keyname)
        apikey = input()
        write_api_key_to_config(apikey,section,keyname, config_file)
    return apikey
