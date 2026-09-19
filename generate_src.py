import re
import shutil
from pathlib import Path

VANILLA = Path.home() / ".local/share/kcd2-modding-docs/docs/kcd2-mod-docs/Scripts"
EVENTS = Path("Quests/Final/Barbora/random_events")
OUTPUT = Path(__file__).resolve().parent / "src/Data/RoadEncounters"

ELITE_FACTOR = 2  # 1 -> 2
WEAK_FACTOR = 1.8  # 2.5 -> 4.5
CARAVAN_SOLDIER_FACTOR = 3  # 2 -> 6
ROAD_FACTOR = 1.5

# Vanilla gives fractional counts a deviation, like 1.5 +- 0.2
DEVIATION = 0.2

# (event file, NpcAssetName)
CAMP_ELITES = [
    ("unfriendly_bandits", "spawnedNPCs"),
    ("unfriendly_cumans", "spawnedNPCs"),
]
CAMP_WEAK = [
    ("unfriendly_bandits", "spawnedNPCs_party"),
    ("unfriendly_cumans", "spawnedNPCs_party"),
]
CARAVAN_SOLDIERS = [
    ("armed_caravan_big_germans", "accompany_thirdCart"),
    ("armed_caravan_big_soldiers", "accompany_thirdCart"),
    ("armed_caravan_medium_germans", "accompany_secondCart"),
    ("armed_caravan_medium_soldiers", "accompany_secondCart"),
]
ROAD_NPCS = [
    ("bandits_duo", "bandits_looter"),
    ("bandits_duo", "bandits_watcher"),
    ("solo_bandit", "bandits_looter"),
    ("dummy_wanderer", "spawnedNPCs"),
    ("ambush_npc_man_variants", "ambusher_party"),
    ("ambush_npc_woman", "ambusher_party"),
    ("prepadeni_magic_shop", "ambusher_party"),
    ("prepadeni_unlucky_guy", "ambusher_party"),
    ("attack_on_sight_bandits", "spawnedNPCs"),
    ("attack_on_sight_cumans", "spawnedNPCs"),
    ("listovni_tajemstvi_zabijaci", "spawnedNPCs"),
    ("bandits_reactive", "spawnedNPCs"),
    ("bandits_rydlo", "spawnedNPCs"),
    ("deserters_rotten_apple", "spawnedNPCs"),
    ("deserters_weapon_and_armor", "spawnedNPCs"),
    ("peasants_reactive", "spawnedNPCs"),
]

FACTORS = [
    (ELITE_FACTOR, CAMP_ELITES),
    (WEAK_FACTOR, CAMP_WEAK),
    (CARAVAN_SOLDIER_FACTOR, CARAVAN_SOLDIERS),
    (ROAD_FACTOR, ROAD_NPCS),
]


def find_event(name: str) -> Path:
    (path,) = (VANILLA / EVENTS).rglob(f"{name}.xml")
    return path.relative_to(VANILLA)


def scale_count(text: str, asset: str, factor: float) -> str:
    (group,) = re.findall(rf'<NpcGroup [^>]*NpcAssetName="{asset}"[^>]*/>', text)
    old = re.search(r' Count="([^"]*)"', group)
    assert old

    count = round(float(old[1]) * factor, 2)
    new = f' Count="{count:g}"'
    if count % 1 and "CountStandardDeviation" not in group:
        new += f' CountStandardDeviation="{DEVIATION}"'

    return text.replace(group, group.replace(old[0], new))


def main(output: Path = OUTPUT) -> None:
    files = {}
    for factor, groups in FACTORS:
        for name, asset in groups:
            path = find_event(name)
            text = files.get(path) or (VANILLA / path).read_text(encoding="utf-8")
            files[path] = scale_count(text, asset, factor)

    if (output / "Quests").exists():
        shutil.rmtree(output / "Quests")

    for path, text in files.items():
        target = output / path
        target.parent.mkdir(parents=True, exist_ok=True)
        # Vanilla in the docs is LF, the game's own files are CRLF
        target.write_bytes(text.replace("\n", "\r\n").encode("utf-8"))


if __name__ == "__main__":
    main()
