# Built-in packages
from configparser import ConfigParser
from dataclasses import asdict, dataclass
from os import mkdir, path

# Outside packages
from dacite import exceptions as dacite_exceptions
from dacite import from_dict

# Constants
import constants as c


@dataclass
class General:
    suppress_game_debug_output: str = "False"

    @staticmethod
    def defaultConfig():
        return General(suppress_game_debug_output="False")


@dataclass
class FileHistory:
    game_exe: list
    data_win: list
    movie: list
    maxhistoryentries: str = "10"

    @staticmethod
    def defaultConfig():
        return FileHistory(game_exe=[], data_win=[], movie=[], maxhistoryentries="10")


@dataclass
class Configuration:
    # ini sections go here. Each section gets its own class with the options. Options must be lowercase
    General: General
    File_History: FileHistory

    @staticmethod
    def defaultConfig():
        return Configuration(General=General.defaultConfig(), File_History=FileHistory.defaultConfig())


class myConfigParser(ConfigParser):
    # Class for ConfigParser with some extra functionality to work with what we need

    def as_dict(self):
        # Method to return the ini file as a dict, for additional parsing with dacite
        d = dict(self._sections)
        for k in d:
            d[k] = dict(self._defaults, **d[k])
            d[k].pop("__name__", None)
            for key, value in d[k].items():
                # Run conversions here
                d[k][key] = self.strToList(value)
        return d

    def strToList(self, value):
        # Function to convert to lists
        if value.startswith("\n"):
            # indicator for a list
            return value.strip()[1:].split("\n")
            # Add a character to the front so that the entire value isn't all whitespace when empty
        else:
            return value

    def read_dict(self, dictionary, source="<dict>"):
        # Overrides the built-in method of the same name in order to include our listToStr method
        # Takes as input a nested dictionary and sets the corresponding headers/options/values
        for section in dictionary:
            if not self.has_section(section):
                # then add the section
                self.add_section(section)
            for option in dictionary[section]:
                self.set(section, option, self.listToStr(dictionary[section][option]))

    def listToStr(self, value):
        if isinstance(value, list):
            return "\n+" + "\n".join(value)
        else:
            # otherwise do nothing and return the input value
            return value


def configLoad(configFilePath):
    """
    Load all from the given configuration file

    Args:
        configFilePath (str): Path to the config.ini file

    Returns:
        Configuration: Configuration object with the loaded config data
    """

    if path.isfile(configFilePath):
        # Use config parser to read the ini file into a dictionary
        configParserObj = myConfigParser()
        configParserObj.read(configFilePath)
        configDict = configParserObj.as_dict()

        try:
            # use dacite's from_dict to create the configuration object from the dict
            config = from_dict(data_class=Configuration, data=configDict)
            return config

        except (dacite_exceptions.WrongTypeError, dacite_exceptions.MissingValueError):
            # indicate a data error (malformed key, etc.)
            print(c.CONFIG_DATA_ERROR_STRING)

            # Return and save a default config if one couldn't be loaded
            config = Configuration.defaultConfig()
            configSave(config, configFilePath)
            return config

    else:
        print(c.CONFIG_FILE_NOT_FOUND_STRING)
        # Return a default config if one couldn't be loaded
        config = Configuration.defaultConfig()

        # Also save the default config because file does not exist
        if not path.isdir(c.APPDATA_PATH):
            mkdir(c.APPDATA_PATH)
            # Ensure the appdata folder has been created
        configSave(config, configFilePath)
        return config


def configSave(config, configFilePath):
    """
    Saves the Configuration to the given file path

    Args:
        config (Configuration): Configuration with the data to save
        configFilePath (str): Path to the file to save the config
    """
    # Create configParser object
    configParserObj = myConfigParser()

    # Read the config object into configParserObj
    configParserObj.read_dict(asdict(config))

    # Write to file
    with open(configFilePath, "w") as fid:
        configParserObj.write(fid)
