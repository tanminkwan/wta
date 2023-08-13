import os

#DEBUG
DEBUG = os.getenv("DEBUG", 'True').lower() in ('true', '1', 't')

#
COMMAND_RECEIVER_ENABLED = False
MESSAGE_RECEIVER_ENABLED = False

import __main__
AGENT_NAME = os.environ.get('AGENT_NAME') or \
    os.path.basename(__main__.__file__).split('.')[0]

AGENT_ROLES = "openai_agent"

CUSTOM_APIS_PATH = "wta.api"

C_OPENAI_API_KEY = "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"