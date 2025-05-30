from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from modules.dats import DatNode
    from modules.config import Config
    from modules.titletools import Removes

from modules.utils import eprint


def filter_regions(
    processed_titles: dict[str, set[DatNode]], config: Config, removes: Removes
) -> dict[str, set[DatNode]]:
    """
    Filters titles in a dict of DatNodes for regions as defined by the user.

    Args:
        processed_titles (dict[str, set[DatNode]]): A work in progress dictionary
        of DatNodes, originally populated from the input DAT and actively being worked
        on by Retool.

        config (Config): The Retool config object.

        removes (Removes): The Retool removes object, which contains and categorizes
        all the titles that have been removed from consideration. Is used for stats
        and other output files generated by Retool.

    Returns:
        dict[str, set[DatNode]]: A dictionary of DatNodes with titles filtered
        based on regions.
    """
    eprint('• Removing titles without specified regions... ')

    temp_dict = processed_titles.copy()
    regions_count: set[str] = set()

    # Check if a system config is in play
    region_order: list[str] = config.region_order_user

    if config.system_region_order_user:
        if {'override': 'true'} in config.system_region_order_user:
            region_order = [str(x) for x in config.system_region_order_user if 'override' not in x]

    for group_name, titles in temp_dict.items():
        supported_regions: set[DatNode] = set()

        for title in titles:
            for region in region_order:
                if region in title.regions:
                    supported_regions.add(title)

        # Exception to track stats later for superset titles, which can be in multiple groups
        regions_count = regions_count | {
            x.full_name for x in processed_titles[group_name] if x not in supported_regions
        }

        # Track removed titles
        for title in [x for x in processed_titles[group_name] if x not in supported_regions]:
            title.exclude_reason = 'Region remove'
            removes.region_removes.add(title)

        processed_titles[group_name] = set(supported_regions)

        # Clean up empty groups
        if not processed_titles[group_name]:
            del processed_titles[group_name]

    # Add removed titles due to region filters to the stats
    config.stats.regions_count = len(regions_count)

    eprint('• Removing titles without specified regions... done.', overwrite=True)

    return processed_titles
