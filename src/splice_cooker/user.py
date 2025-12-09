"""User class to handle unique user name and configuration."""

import yaml


class User(yaml.YAMLObject):
    """User class.

    Inherits from YAMLObject, which automatically creates an instance upon loading a
    yaml file.
    """

    yaml_tag = "!User"

    def __init__(self, name, config):
        """Initialize user."""
        self.name = name
        self.config = config

    def __repr__(self):
        """Printable representation."""
        return "%s(name=%r, config=%r)" % (
            self.__class__.__name__,
            self.name,
            self.config,
        )
