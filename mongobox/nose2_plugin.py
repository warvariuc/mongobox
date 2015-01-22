"""
nose2.cfg should contain:

[unittest]
plugins = mongobox.nose2_plugin

[mongobox]
always-on = True
# Optionally specify the path to the mongod executable
# bin =
# Optionally specify the port to run mongodb on
# port =
# Optionally enables mongodb script engine
# scripting = True
# Path to database files directory. Creates temporary directory by default
# dbpath =
# Optionally store the mongodb log here (default is /dev/null)
# logpath =
# Optionally preallocate db files
# prealloc = True
# Which environment variable port number will be exported to
port_envvar = MONGOBOX_PORT
"""
import logging
import os

from nose2.events import Plugin

from .mongobox import MongoBox


log = logging.getLogger('nose2.plugins.mongobox')


DEFAULT_PORT_ENVVAR = 'MONGOBOX_PORT'


class MongoBoxPlugin(Plugin):
    """A nose plugin that setups a sandboxed mongodb instance.
    """
    configSection = 'mongobox'

    def __init__(self):
        self.mongobox = MongoBox(
            mongod_bin=self.config.get('bin'),
            port=self.config.as_int('port'),
            log_path=self.config.get('logpath'),
            db_path=self.config.get('dbpath'),
            scripting=self.config.as_bool('scripting', False),
            prealloc=self.config.as_bool('prealloc', False),
        )

        self.port_envvar = self.config.get('port_envvar', DEFAULT_PORT_ENVVAR)

    def startTestRun(self, event):
        assert self.port_envvar not in os.environ, (
            '{} environment variable is already taken. '
            'Do you have other tests with mongobox running?'.format(self.port_envvar))

        self.mongobox.start()
        os.environ[self.port_envvar] = str(self.mongobox.port)

    def stopTestRun(self, event):
        self.mongobox.stop()
        del os.environ[self.port_envvar]
