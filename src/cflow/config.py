class ConnectorConfig:
    """Global configurations for connectors."""

    # Default messages
    CONNECTING_MESSAGE = "Connecting to {} ..."
    DISCONNECTING_MESSAGE = "Disconnecting from {} ..."
    VALIDATING_CONNECTION_MESSAGE = "Validating connection for {} ..."
    RETRY_ATTEMPT_MESSAGE = "Attempt {} of connection for {}"
    NO_DESCRIPTION_PROVIDED = "No description provided"

    # Default timeouts (in seconds)
    DEFAULT_TIMEOUT = 30
    DEFAULT_RETRY_ATTEMPTS = 3

    # Flags
    ENABLE_RETRY_DEFAULT = True