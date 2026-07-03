"""
Pure data for resident spawning — name pools, role tables, dialogue banks.
No game logic here; import into mixin files only.
"""

# ── Name pools ────────────────────────────────────────────────────────────────

_NAMES_WOODLANDS = ["Arden", "Bren", "Calla", "Dale", "Elva", "Finn", "Gale", "Holt", "Ivy", "Jem", "Kess", "Lorne"]
_NAMES_PLAINS    = ["Alden", "Bess", "Colt", "Devin", "Etha", "Ford", "Greer", "Hazel", "Jules", "Merle", "Nell", "Perry"]
_NAMES_DESERT    = ["Saja", "Nour", "Kerim", "Zara", "Fahd", "Izar", "Leila", "Mahi", "Navid", "Qara", "Rima", "Tavin"]
_NAMES_COLD      = ["Harek", "Ingrid", "Bjorn", "Signe", "Runa", "Leif", "Astrid", "Einar", "Ylva", "Torben", "Solveig", "Gunnar"]
_NAMES_VOLCANIC  = ["Kael", "Sorn", "Vrek", "Dura", "Ash", "Cinder", "Grav", "Sola", "Tamek", "Breck", "Fendur", "Morra"]
_NAMES_COMMON    = ["Mira", "Tomas", "Sera", "Lund", "Wick", "Nett", "Brace", "Olm", "Caris", "Dunn", "Pell", "Wren"]

BIOME_NAME_POOL = {
    "forest":    _NAMES_WOODLANDS + _NAMES_COMMON,
    "plains":    _NAMES_PLAINS + _NAMES_COMMON,
    "farmland":  _NAMES_PLAINS + _NAMES_COMMON,
    "desert":    _NAMES_DESERT + _NAMES_COMMON,
    "swamp":     _NAMES_WOODLANDS + _NAMES_COMMON,
    "mountain":  _NAMES_COLD + _NAMES_COMMON,
    "badlands":  _NAMES_PLAINS + _NAMES_VOLCANIC,
    "tundra":    _NAMES_COLD,
    "volcanic":  _NAMES_VOLCANIC + _NAMES_COMMON,
}

# ── Biome-local resident definitions ─────────────────────────────────────────
# (kind, title, dialogue_lines, building_name_hints)

BIOME_LOCALS = {
    "forest":    ("herbalist", "Herbalist",   ("The woods cure and poison in equal measure.", "Roots, bark, and leaves can solve more than steel can.", "You learn the forest by what it does to you first."), ("shed", "cottage", "house")),
    "plains":    ("vendor",    "Peddler",     ("Road trade keeps a plains town breathing.", "Someone always needs a little powder, rope, or grain.", "The market moves whether the weather agrees or not."), ("store", "market", "stable")),
    "farmland":  ("miller",    "Miller",      ("Grain, flour, and patience keep a place like this standing.", "A quiet harvest says more than a loud road.", "The mill knows the season before the fields do."), ("granary", "barn", "farm")),
    "desert":    ("drover",    "Drover",      ("A desert town lives by what it can carry.", "Shade, water, and good sense all cost something out here.", "You count everything twice before the sun gets high."), ("yard", "depot", "storehouse")),
    "swamp":     ("ferryman",  "Ferryman",    ("In wet country, a sure crossing is worth more than a strong wall.", "Boardwalks and boats make better neighbors than pride.", "The swamp takes what you don't respect about it."), ("boat", "reed", "hut")),
    "mountain":  ("mason",     "Mason",       ("Stone remembers every bad cut and every good one.", "A mountain settlement survives by what it can brace.", "The cold teaches you which joints matter."), ("stone", "tool", "ore")),
    "badlands":  ("vendor",    "Trail Trader",("Badlands folk learn to pack light and sell quick.", "If something breaks out there, you fix it or bury it.", "Every trade post out here started as someone's bad idea."), ("store", "shed", "tack")),
    "tundra":    ("trapper",   "Trapper",     ("Cold country teaches you to read silence before tracks.", "A warm room is built long before the snow arrives.", "The tundra doesn't care about your plans."), ("smokehouse", "shed", "hut")),
    "volcanic":  ("kilnkeeper","Kilnkeeper",  ("Ash and heat still make homes if you know how to work them.", "Even here, people build first and complain after.", "Fire gives and fire takes. You just have to be faster."), ("kiln", "cistern", "ash")),
}

# ── Flavor building resident definitions ─────────────────────────────────────

FLAVOR_RESIDENTS = {
    "house": [
        ("settler", "settler", "Resident",
         ("The house has a settled, lived-in feel.",
          "Visitors are welcome if they're respectful.",
          "Days here run long and quiet.",
          "The road keeps changing but home stays the same.")),
    ],
    "hall": [
        ("elder", "settler", "Town Elder",
         ("The hall keeps older records than most buildings.",
          "We decide things slowly here. Deliberately.",
          "A settlement earns its name through its decisions, not its size.")),
        ("guide", "friend", "Councilor",
         ("Every settlement runs on its people.",
          "Word gets around. It always does.",
          "The hall hears everything eventually.")),
    ],
    "granary": [
        ("miller", "settler", "Miller",
         ("A full granary is a quiet confidence.",
          "Count before you measure, measure before you pour.",
          "The harvest sets the tone for the whole year.")),
    ],
    "barn": [
        ("farmer", "settler", "Farmer",
         ("Animals need tending before you need sleep.",
          "The smell is honest work.",
          "A good barn in autumn means a calm winter.")),
    ],
    "workshop": [
        ("mason", "settler", "Craftsman",
         ("Good tools outlast their owners if you treat them right.",
          "The work teaches you if you're patient enough to listen.",
          "Most problems are a fit problem. Fix the fit.")),
    ],
    "smokehouse": [
        ("trapper", "settler", "Smokehouse Hand",
         ("Slow and low — that's the rule in here.",
          "The smoke does the work. You just have to be patient.",
          "A good cure takes the day it takes. No shortcuts.")),
    ],
    "storehouse": [
        ("vendor", "settler", "Storekeeper",
         ("Everything here is counted and accounted for.",
          "A place for everything, everything in its place.",
          "The records tell you what the shelves won't admit.")),
    ],
}

# ── Second-visit (claimed) dialogue ──────────────────────────────────────────

RETURN_DIALOGUE = {
    "guide":       ("The guide nods. 'Still finding the edges out there?'",
                    "'You're back,' the guide says. 'Good sign.'",
                    "The guide watches the road. 'Roads have been busy this stretch.'"),
    "scout":       ("The scout gives a measured nod.",
                    "'Still moving,' the scout says. 'That's the job.'",
                    "The scout glances at the horizon rather than answer."),
    "farmer":      ("The farmer looks you over. 'Hard road?'",
                    "'You made it back,' the farmer says, seeming pleased.",
                    "The farmer wipes their hands. 'Come by again if you're hungry.'"),
    "watch":       ("The watcher tracks the roads. 'Anything worth reporting?'",
                    "The watcher nods. 'Glad you're still upright.'",
                    "'The watch is always here,' the watcher says."),
    "vendor":      ("The vendor gestures to the stall. 'Still open, if you need it.'",
                    "'Nothing new yet,' the vendor says, 'but keep an eye out.'",
                    "The vendor shrugs. 'Business is always moving.'"),
    "herbalist":   ("The herbalist studies you. 'You look like you've been keeping clear of the worst.'",
                    "The herbalist nods. 'Come back if the road bites harder.'",
                    "'The mix takes time,' the herbalist says. 'Try again tomorrow.'"),
    "elder":       ("The elder looks up slowly. 'You have the look of someone who's been places.'",
                    "'Sit a moment,' the elder says. 'You've earned a rest.'",
                    "The elder says nothing for a while, then: 'Good.'"),
    "drover":      ("The drover eyes the road. 'How were the trails out east?'",
                    "The drover nods. 'You didn't lose the route. That's half of it.'",
                    "'Still moving,' the drover says. 'That counts for something.'"),
    "miller":      ("The miller wipes flour from their hands. 'Back already?'",
                    "The miller says the harvest has been steady this season.",
                    "The miller nods. 'Take care out there on the roads.'"),
    "ferryman":    ("The ferryman eyes the water. 'Crossings have been clear.'",
                    "'Still here,' the ferryman says. 'Most days that's the job.'",
                    "The ferryman points south without saying why."),
    "mason":       ("The mason lays down their chisel. 'Road holding up?'",
                    "The mason studies the horizon. 'Stone endures.'",
                    "The mason says nothing, just nods once, firmly."),
    "trapper":     ("The trapper looks you over. 'Tracks look cleaner. Good.'",
                    "The trapper says the cold's been biting early.",
                    "The trapper nods. 'Come back if the road gets mean.'"),
    "kilnkeeper":  ("The kilnkeeper studies the coals. 'You're still burning. Good.'",
                    "The kilnkeeper says the ash has been coming in thick this week.",
                    "The kilnkeeper waves you off gently. 'You're fine. Go.'"),
    "wanderer":    ("The wanderer adjusts their pack. 'Still on the move myself.'",
                    "The wanderer says the road's been full of surprises lately.",
                    "'I'll be gone soon,' the wanderer says. 'That's the life.'"),
}

# ── Wanderer dialogue templates ───────────────────────────────────────────────
# Used to compose the traveler NPC's boon reveal message.

WANDERER_DIRECTION_FLAVOR = {
    "north": ("came down from the north", "was heading south from the highlands", "pushed down from up north"),
    "south": ("came up from the south", "was moving north out of the lowlands", "followed the road up from the south"),
    "east":  ("came in from the east", "was crossing from the eastern stretch", "moved west from the far side"),
    "west":  ("came in from the west", "was cutting east through the back country", "pushed in from the western roads"),
}

WANDERER_REGION_FLAVOR = {
    "dungeon": "a deep site worth the trouble",
    "cave":    "a cave system with more in it than it looks",
    "ruins":   "ruins with a fair bit of salvage left",
    "castle":  "a fortified site — well-guarded but solid rewards",
    "town":    "a settlement that could use a visitor",
    "shrine":  "an old shrine still doing its work",
    "cache":   "a stash someone left for whoever found it",
    "monster_town": "hostile ground — keep clear or go ready",
}

WANDERER_NAMES = [
    "Daven", "Cress", "Olan", "Tev", "Sable", "Ran", "Merin", "Pike",
    "Joss", "Ula", "Brant", "Sidra", "Feth", "Quill", "Nave", "Arro",
]

CHILD_OBSERVATIONS = (
    "The child watches you with open curiosity.",
    "The child kicks a stone down the path and doesn't look back.",
    "The child stares, then decides you're not that interesting.",
    "The child is busy with something small in the dirt.",
    "The child waves once, uncertain.",
    "The child follows you with their eyes until you stop moving.",
    "The child asks where you came from, then runs off before you can answer.",
    "The child squints. 'You have a lot of stuff.'",
    "The child points at your pack. 'What's that for?'",
    "The child is clearly supposed to be somewhere else.",
)
