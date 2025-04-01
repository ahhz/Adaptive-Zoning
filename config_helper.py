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
