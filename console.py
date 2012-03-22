import sys
import os


class Console:
    """
    Console app for SUSE Manager database control.

    Author: Bo Maryniuk <bo@suse.de>
    """

    # General
    VERSION = "1.0"
    DEFAULT_CONFIG = "/etc/rhn/rhn.conf"

    # Config
    DB_BACKEND = "db_backend"


    def __init__(self, configpath=None):
        """
        Constructor.
        """
        self.config_file = configpath
        self.get_config()
        self.load_db_backend()


    def load_db_backend(self):
        """
        Load required backend for the database.
        """
        try:
            self.gate = __import__(self.config.get(self.DB_BACKEND, "unknown") + "gate").getGate(self.config)
        except Exception, ex:
            print ex
            raise Exception("Unknown database backend. Please check %s configuration file." % self.config_file)


    def get_config(self):
        """
        Read rhn config for database type.
        """
        self.config = {}
        self.config_file = self.config_file and self.config_file or self.DEFAULT_CONFIG

        cfg = None
        if os.path.exists(self.config_file):
            cfg = open(self.config_file).readlines()
        else:
            raise Exception("Cannot open configuration file: " + self.config_file)

        for line in cfg:
            try:
                key, value = line.replace(" ", "").strip().split("=", 1)
                if key.startswith("db_"):
                    self.config[key] = value
            except:
                pass


    @staticmethod
    def usage_header():
        print >> sys.stderr, "SUSE Manager Database Control. Version", Console.VERSION
        print >> sys.stderr, "Copyright (c) by SUSE Linux Products GmbH\n"


    def usage(self):
        """
        Print usage.
        """
        Console.usage_header()
        print >> sys.stderr, "Available commands on %s database:" % self.gate.NAME.title()

        index_commands = []
        longest = 0
        for command, description in self.gate.get_gate_commands().items():
            command = self.translate_command(command)
            index_commands.append(command)
            longest = longest < len(command) and len(command) or longest

        index_commands.sort()

        for command in index_commands:
            print >> sys.stderr, "\t", (command + ((longest - len(command)) * " ")), \
                "\t", self.gate.get_gate_commands().get(self.translate_command(command))

        print >> sys.stderr


    def translate_command(self, command):
        """
        Translate from "do_something_like_this" as a method name
        to "something-like-this" for CLI. And vice versa.
        """

        return command.startswith("do_") and command[3:].replace("_", "-") or ("do_" + command.replace("-", "_"))


    def execute(self, command):
        """
        Execute one command.
        """
        method = self.translate_command(command)
        if self.gate.get_gate_commands().get(method):            
            getattr(self.gate, method)()
        else:
            raise Exception(("The parameter \"%s\" is an unknown command.\n\n"  % command) + 
                            "Hint: Try with no parameters first, perhaps?")
        


def main():
    """
    Main app runner.
    """
    try:
        console = Console()
        if len(sys.argv) < 2:
            console.usage()
        else:
            console.execute(sys.argv[1])
    except Exception, err:
        Console.usage_header()
        print >> sys.stderr, "General error:\n", err, "\n"
        sys.exit(1)


if __name__ == "__main__":
    main()