import random

from .models import RegionPalette


def random_region_name(region_type):
    tables = {
        "dungeon": (
            ["Ashen", "Gloam", "Hollow", "Iron", "Silent", "Black", "Sunken"],
            ["Catacombs", "Vault", "Keep", "Depths", "Warrens", "Crypt", "Halls"],
        ),
        "forest": (
            ["Whispering", "Moss", "Amber", "Moon", "Thorn", "Green", "Cedar"],
            ["Grove", "Wilds", "Wood", "Glade", "Canopy", "Thicket", "Copse"],
        ),
        "ruins": (
            ["Broken", "Fallen", "Old", "Shattered", "Weathered", "Lost", "Sable"],
            ["Sanctum", "Stones", "Court", "Ruins", "Pillars", "Watch", "Forum"],
        ),
        "desert": (
            ["Amber", "Burning", "Dune", "Saffron", "Glass", "Sun", "Red"],
            ["Expanse", "Waste", "Reach", "Sea", "Hollows", "Oasis", "Steppe"],
        ),
        "mountain": (
            ["High", "Granite", "Storm", "Snow", "Iron", "Eagle", "Frost"],
            ["Pass", "Spine", "Ridge", "Climb", "Heights", "Steps", "Crown"],
        ),
        "swamp": (
            ["Black", "Mire", "Sour", "Fog", "Drowned", "Bog", "Reed"],
            ["Fen", "Marsh", "Bog", "Lowland", "Mire", "Hollow", "Waters"],
        ),
        "plains": (
            ["Golden", "Wide", "Sun", "High", "Long", "Breeze", "Open"],
            ["Field", "Plains", "Plateau", "Reach", "Grass", "Steppe", "Downs"],
        ),
        "farmland": (
            ["Amber", "Harvest", "Miller's", "Green", "Orchard", "Barley", "Sun"],
            ["Fields", "Farm", "Croft", "Acres", "Pasture", "Hold", "Meadow"],
        ),
        "badlands": (
            ["Red", "Broken", "Dust", "Shale", "Riven", "Dry", "Rust"],
            ["Badlands", "Cuts", "Canyon", "Reach", "Barrens", "Gulch", "Flats"],
        ),
        "tundra": (
            ["White", "Frost", "Pale", "Winter", "North", "Snow", "Icewind"],
            ["Tundra", "Waste", "Reach", "Expanse", "Fields", "Hollows", "Drift"],
        ),
        "volcanic": (
            ["Ash", "Cinder", "Ember", "Magma", "Fire", "Black", "Smoldering"],
            ["Caldera", "Crags", "Wastes", "Spine", "Fields", "Fissure", "Flow"],
        ),
        "castle": (
            ["Ivory", "Ashen", "Black", "Silent", "Red", "Kings", "Fallen"],
            ["Keep", "Castle", "Bastion", "Hall", "Rampart", "Court", "Citadel"],
        ),
        "cave": (
            ["Deep", "Echo", "Moon", "Hollow", "Stone", "Cold", "Twilight"],
            ["Cavern", "Grotto", "Cave", "Hollow", "Tunnels", "Sink", "Den"],
        ),
        "maze": (
            ["Crooked", "Mirror", "Lost", "Twisted", "Hedge", "Silent", "Winding"],
            ["Maze", "Labyrinth", "Ways", "Passages", "Turns", "Loops", "Grid"],
        ),
        "town": (
            ["Oak", "Lantern", "Still", "River", "Market", "Sun", "Crossing"],
            ["Hollow", "Cross", "Square", "Village", "Commons", "Rest", "Ford"],
        ),
        "monster_town": (
            ["Blight", "Grim", "Howling", "Rotted", "Ash", "Blood", "Crooked"],
            ["Borough", "Hamlet", "Row", "Hearth", "Square", "Stead", "Market"],
        ),
        "ossuary": (
            ["The", "Sunken", "Bone", "Forgotten", "Ancient"],
            ["Ossuary", "Charnel Hall", "Charnel Vault", "Bone Repository", "Reliquary"],
        ),
        "mirrorwood": (
            ["The", "Pale", "Still", "Silver", "Reflected"],
            ["Mirrorwood", "Silvered Grove", "Glass Glade", "Still Wood", "Mirror Thicket"],
        ),
        "inn": (["Traveler's"], ["Inn"]),
        "clinic": (["Town"], ["Clinic"]),
        "supply": (["Old"], ["Provisioner"]),
        "shrine": (["Wayside", "Quiet", "Sun", "Pilgrim's", "Stone"], ["Shrine", "Sanctum", "Chapel"]),
        "smith": (["Old", "Iron", "Ember", "Hammer", "Anvil"], ["Forge", "Smithy", "Works"]),
        "cartographer": (["Surveyor's", "Wayfinder's", "Lantern", "Road", "Atlas"], ["Office", "Charts", "Maps"]),
        "cache":         (["Hidden", "Buried", "Stashed", "Forgotten", "Lost"],   ["Cache", "Stores", "Supplies", "Hoard"]),
        "waystone":      (["Old", "Mossy", "Cracked", "Weathered", "Road"],        ["Waystone", "Marker", "Post", "Stone"]),
        "barrow":        (["Ancestor's", "Forgotten", "Old", "Earthen", "Stone"],  ["Barrow", "Mound", "Burial", "Cairn"]),
        "stone_circle":  (["Old", "Standing", "Thorn", "Moon", "Broken"],          ["Circle", "Ring", "Stones", "Henge"]),
        "oasis":         (["Clear", "Still", "Deep", "Desert", "Salt"],            ["Oasis", "Spring", "Pool", "Watering Hole"]),
        "hot_spring":    (["Scalding", "Steam", "Mineral", "Deep", "Sulfur"],      ["Spring", "Pool", "Vent", "Bath"]),
        "watchtower":    (["Old", "Crumbling", "Stone", "Border", "High"],         ["Watchtower", "Tower", "Lookout", "Post"]),
        "grove":         (["Ancient", "Still", "Quiet", "Mossy", "Hollow"],        ["Grove", "Copse", "Glade", "Thicket"]),
        "necropolis":    (["Forgotten", "Sunken", "Old", "Bone", "Silent"],        ["Necropolis", "Tombs", "Crypts", "Vaults"]),
        "geyser":        (["Steam", "Sulfur", "Hot", "Boiling", "Ash"],            ["Geyser", "Vent", "Spout", "Fumarole"]),
        "standing_stone":(["Carved", "Old", "Worn", "Road", "Boundary"],           ["Stone", "Marker", "Pillar", "Stele"]),
        "camp":          (["Abandoned", "Empty", "Old", "Burned", "Trail"],        ["Camp", "Campsite", "Bivouac", "Outpost"]),
    }
    first, second = tables.get(region_type, tables["dungeon"])
    return f"{random.choice(first)} {random.choice(second)}"


def region_summary(region_type, floor):
    summaries = {
        "dungeon": "Dense corridors, tighter fights, reliable cover.",
        "forest": "Open paths, broken sightlines, vitality-friendly growth.",
        "ruins": "Shattered halls, mixed cover, stronger salvage.",
        "desert": "Open sands, jagged cover, and long sightlines between oases.",
        "mountain": "Narrow passes, sudden bends, and strong positional choke points.",
        "swamp": "Broken islands of footing with murky, awkward approaches.",
        "plains": "Broad space, sparse cover, and clean lines for ranged pressure.",
        "farmland": "Cultivated lanes, hedges, and open working ground around settlements.",
        "badlands": "Riven rock, hard bends, and broken canyon approaches.",
        "tundra": "Cold open stretches with wind-cut cover and bright sightlines.",
        "volcanic": "Ash-choked chambers, hard rock, and constant heat hazards.",
        "castle": "Structured wings, central keeps, and disciplined room fights.",
        "cave": "Jagged chambers and tunnels with irregular visibility pockets.",
        "maze": "Tight turns, deliberate scouting, and disorienting navigation.",
        "town": "Peaceful streets, townsfolk, and room to recover bearings.",
        "monster_town": "A settlement gone wrong, full of hostile residents and beasts.",
        "ossuary": "A silent bone-house deep in the wilds, older than any map.",
        "mirrorwood": "A wood where the light behaves strangely and the paths double back.",
        "inn": "A quiet room and a chance to rest.",
        "clinic": "A clean stop for patching wounds.",
        "supply": "A stocked room for expedition essentials.",
        "shrine": "A still place where protective rites linger.",
        "smith": "A forge for tuning gear before the road ahead.",
        "cartographer": "A map room for charting the nearby frontier.",
    }
    suffix = f" Floor {floor + 1} route."
    return summaries.get(region_type, "Unfamiliar territory.") + suffix


def palette_for_region(region_type):
    palettes = {
        "dungeon": RegionPalette((96, 100, 112), (42, 42, 52), (46, 50, 60), (20, 20, 28), (18, 24, 36), (120, 154, 188), (245, 244, 232)),
        "forest": RegionPalette((48, 108, 62), (34, 52, 38), (24, 62, 34), (18, 28, 20), (16, 32, 22), (94, 156, 112), (236, 248, 228)),
        "ruins": RegionPalette((116, 90, 62), (54, 46, 40), (68, 50, 34), (26, 22, 20), (34, 24, 18), (176, 132, 94), (250, 238, 220)),
        "desert": RegionPalette((168, 132, 72), (92, 76, 44), (102, 72, 28), (40, 30, 18), (42, 28, 12), (228, 184, 92), (255, 244, 214)),
        "mountain": RegionPalette((108, 120, 126), (56, 64, 70), (62, 70, 76), (26, 28, 32), (24, 28, 36), (168, 184, 196), (244, 248, 252)),
        "swamp": RegionPalette((64, 86, 52), (44, 58, 40), (34, 48, 26), (20, 28, 18), (20, 26, 18), (124, 166, 96), (232, 246, 222)),
        "plains": RegionPalette((132, 156, 86), (74, 92, 54), (68, 88, 42), (28, 34, 20), (28, 32, 16), (206, 216, 126), (248, 250, 224)),
        "farmland": RegionPalette((156, 150, 92), (84, 88, 54), (92, 94, 48), (32, 34, 20), (34, 34, 18), (224, 206, 118), (250, 246, 214)),
        "badlands": RegionPalette((144, 96, 72), (76, 52, 42), (92, 58, 36), (30, 22, 18), (34, 22, 14), (220, 154, 104), (252, 236, 214)),
        "tundra": RegionPalette((176, 186, 194), (92, 102, 112), (110, 122, 132), (36, 40, 46), (34, 40, 48), (220, 236, 244), (252, 252, 255)),
        "volcanic": RegionPalette((110, 88, 84), (62, 48, 46), (84, 52, 42), (26, 20, 20), (34, 18, 18), (232, 126, 84), (255, 236, 226)),
        "castle": RegionPalette((124, 124, 138), (62, 58, 72), (68, 68, 84), (26, 24, 30), (26, 22, 34), (180, 168, 214), (246, 240, 255)),
        "cave": RegionPalette((92, 84, 74), (48, 42, 36), (54, 44, 34), (22, 18, 16), (22, 18, 14), (172, 144, 116), (246, 234, 220)),
        "maze": RegionPalette((84, 112, 86), (40, 54, 42), (34, 68, 36), (18, 26, 18), (18, 30, 20), (154, 210, 156), (236, 250, 236)),
        "town": RegionPalette((160, 126, 88), (82, 78, 70), (88, 68, 48), (34, 30, 28), (38, 28, 22), (198, 160, 112), (252, 242, 220)),
        "monster_town": RegionPalette((120, 54, 54), (54, 40, 40), (62, 26, 26), (24, 18, 18), (34, 14, 18), (210, 92, 112), (255, 232, 236)),
        "ossuary": RegionPalette((130, 118, 110), (64, 56, 52), (72, 60, 50), (26, 22, 20), (28, 20, 18), (200, 176, 152), (252, 240, 228)),
        "mirrorwood": RegionPalette((140, 180, 160), (64, 96, 80), (72, 116, 96), (22, 36, 28), (20, 36, 28), (200, 236, 212), (240, 252, 244)),
        "inn": RegionPalette((132, 102, 70), (70, 58, 46), (76, 58, 40), (28, 24, 20), (34, 26, 20), (208, 170, 120), (255, 244, 222)),
        "clinic": RegionPalette((122, 132, 144), (62, 72, 84), (70, 80, 92), (24, 28, 34), (22, 28, 32), (180, 214, 226), (240, 250, 255)),
        "supply": RegionPalette((132, 118, 84), (72, 64, 48), (80, 70, 50), (28, 24, 18), (32, 28, 22), (214, 192, 132), (255, 246, 224)),
        "shrine": RegionPalette((126, 126, 152), (62, 58, 78), (72, 68, 90), (24, 22, 32), (26, 22, 38), (196, 186, 234), (248, 242, 255)),
        "smith": RegionPalette((146, 104, 74), (72, 52, 40), (82, 58, 42), (28, 20, 18), (34, 22, 18), (226, 164, 96), (255, 240, 220)),
        "cartographer": RegionPalette((96, 120, 138), (50, 64, 74), (56, 74, 88), (20, 26, 30), (22, 28, 34), (154, 204, 224), (240, 248, 252)),
        "tavern": RegionPalette((138, 98, 62), (68, 54, 40), (78, 54, 36), (28, 22, 18), (34, 24, 18), (214, 158, 98), (255, 240, 210)),
        "chapel": RegionPalette((130, 124, 158), (64, 60, 80), (74, 68, 94), (24, 22, 32), (26, 22, 40), (200, 188, 238), (250, 244, 255)),
        "stable": RegionPalette((138, 112, 74), (72, 62, 46), (84, 66, 44), (30, 24, 18), (34, 26, 18), (210, 172, 108), (252, 238, 208)),
        "house": RegionPalette((152, 120, 82), (78, 72, 62), (84, 64, 44), (32, 28, 24), (36, 26, 20), (192, 152, 104), (250, 238, 214)),
        "hall": RegionPalette((148, 116, 78), (76, 70, 60), (80, 60, 40), (30, 26, 22), (34, 24, 18), (196, 158, 110), (252, 240, 216)),
        "granary": RegionPalette((162, 144, 88), (86, 82, 54), (94, 86, 48), (34, 32, 20), (36, 32, 18), (222, 198, 118), (252, 246, 212)),
        "barn": RegionPalette((154, 106, 68), (78, 58, 42), (88, 60, 38), (30, 22, 18), (36, 22, 16), (222, 154, 96), (254, 234, 206)),
        "workshop": RegionPalette((140, 108, 72), (70, 56, 42), (80, 60, 40), (28, 22, 18), (34, 24, 18), (212, 164, 100), (252, 238, 210)),
        "smokehouse": RegionPalette((110, 96, 82), (58, 52, 46), (64, 54, 42), (24, 22, 18), (28, 22, 16), (174, 148, 118), (244, 232, 216)),
        "storehouse": RegionPalette((136, 120, 84), (70, 66, 50), (78, 68, 46), (28, 26, 20), (32, 28, 20), (208, 186, 124), (250, 244, 216)),
        "cache": RegionPalette((88, 72, 54), (44, 38, 30), (50, 42, 34), (18, 16, 12), (22, 18, 14), (164, 130, 88), (240, 224, 196)),
    }
    return palettes.get(region_type, palettes["town"])
