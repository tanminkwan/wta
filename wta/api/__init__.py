from miniagent import configure

from . import (
    common_apis,
    game_manager_apis,
    openai_agent_apis,
    betting_booth_apis,
    config_map_apis,
    launcher_apis,
)

# Path api/v1/opensearch/ is also used in game_panel_apis
if 'opensearch_agent' in configure['AGENT_ROLES']:
    from . import opensearch_agent_apis
elif 'game_panel' in configure['AGENT_ROLES']:
    from . import game_panel_apis
