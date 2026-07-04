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
                    "The guide watches the road. 'Roads have been busy this stretch.'",
                    "The guide glances toward the edge of the map. 'That site I flagged — did you reach it?'",
                    "'Still mapping?' the guide asks. 'Good. Most stop too soon.'"),
    "scout":       ("The scout gives a measured nod.",
                    "'Still moving,' the scout says. 'That's the job.'",
                    "The scout glances at the horizon rather than answer.",
                    "'The route I named — worth the trip?' the scout asks.",
                    "The scout studies your face. 'You went out there. I can tell.'"),
    "farmer":      ("The farmer looks you over. 'Hard road?'",
                    "'You made it back,' the farmer says, seeming pleased.",
                    "The farmer wipes their hands. 'Come by again if you're hungry.'",
                    "'Hope that meal stretched out there,' the farmer says.",
                    "The farmer checks the sky. 'Road treated you all right?'"),
    "watch":       ("The watcher tracks the roads. 'Anything worth reporting?'",
                    "The watcher nods. 'Glad you're still upright.'",
                    "'The watch is always here,' the watcher says.",
                    "The watcher eyes you. 'You were out near that trouble we mentioned?'",
                    "'Danger we flagged — you saw it yourself, didn't you?'"),
    "vendor":      ("The vendor gestures to the stall. 'Still open, if you need it.'",
                    "'Nothing new yet,' the vendor says, 'but keep an eye out.'",
                    "The vendor shrugs. 'Business is always moving.'",
                    "The vendor nods. 'Put that ammo to use, I hope.'",
                    "'Supply's been thin,' the vendor says, 'but I keep what I can.'"),
    "herbalist":   ("The herbalist studies you. 'You look like you've been keeping clear of the worst.'",
                    "The herbalist nods. 'Come back if the road bites harder.'",
                    "'The mix takes time,' the herbalist says. 'Try again tomorrow.'",
                    "'No new bites since last time?' the herbalist asks.",
                    "The herbalist looks you over. 'The cleanse held, then. Good.'"),
    "elder":       ("The elder looks up slowly. 'You have the look of someone who's been places.'",
                    "'Sit a moment,' the elder says. 'You've earned a rest.'",
                    "The elder says nothing for a while, then: 'Good.'",
                    "The elder looks at you long. 'You used what I told you.'",
                    "'The place I named,' the elder says quietly. 'You went.'"),
    "drover":      ("The drover eyes the road. 'How were the trails out east?'",
                    "The drover nods. 'You didn't lose the route. That's half of it.'",
                    "'Still moving,' the drover says. 'That counts for something.'",
                    "The drover nods. 'Ammo I gave you — held up out there?'",
                    "'Routes I know are honest,' the drover says. 'Road prove it?'"),
    "miller":      ("The miller wipes flour from their hands. 'Back already?'",
                    "The miller says the harvest has been steady this season.",
                    "The miller nods. 'Take care out there on the roads.'",
                    "'That kit from the mill — you've used it by now,' the miller says.",
                    "The miller nods. 'Good to use those before the road gets rough.'"),
    "ferryman":    ("The ferryman eyes the water. 'Crossings have been clear.'",
                    "'Still here,' the ferryman says. 'Most days that's the job.'",
                    "The ferryman points south without saying why.",
                    "The ferryman glances at the exits. 'You found the routes I showed you?'",
                    "'Those crossings I mentioned — they hold?' the ferryman asks."),
    "mason":       ("The mason lays down their chisel. 'Road holding up?'",
                    "The mason studies the horizon. 'Stone endures.'",
                    "The mason says nothing, just nods once, firmly.",
                    "'The ward I set — how long did it hold?' the mason asks.",
                    "The mason glances at your gear. 'Stone blessing. Should last a few more hits.'"),
    "trapper":     ("The trapper looks you over. 'Tracks look cleaner. Good.'",
                    "The trapper says the cold's been biting early.",
                    "The trapper nods. 'Come back if the road gets mean.'",
                    "The trapper glances at your pack. 'Tonic came in handy, I take it.'",
                    "'Ward held up?' the trapper asks. 'That's what it's there for.'"),
    "kilnkeeper":  ("The kilnkeeper studies the coals. 'You're still burning. Good.'",
                    "The kilnkeeper says the ash has been coming in thick this week.",
                    "The kilnkeeper waves you off gently. 'You're fine. Go.'",
                    "'Ward still in you?' the kilnkeeper asks, studying your face.",
                    "The kilnkeeper nods. 'Burn's cleared. You look steady.'"),
    "wanderer":    ("The wanderer adjusts their pack. 'Still on the move myself.'",
                    "The wanderer says the road's been full of surprises lately.",
                    "'I'll be gone soon,' the wanderer says. 'That's the life.'",
                    "The wanderer grins. 'The lead I dropped — worth chasing?'",
                    "'Road I came from,' the wanderer says. 'You checked it?'"),
}

# ── Per-kind region concern templates ─────────────────────────────────────────
# Keyed by (resident_kind, neighbor_region_type).
# {rname} is substituted with the neighboring region's name.

RESIDENT_KIND_CONCERNS = {
    ("farmer", "monster_town"): "There's been trouble coming out of {rname}. The roads haven't been safe.",
    ("farmer", "ruins"):        "We've had wanderers from {rname} looking for work. Not all of them reliable.",
    ("farmer", "dungeon"):      "The site at {rname} draws trouble this way sometimes.",
    ("farmer", "badlands"):     "Nothing grows near {rname}. The soil out there is wrong.",
    ("watch",  "monster_town"): "{rname} is hostile ground. We keep an eye on that direction.",
    ("watch",  "dungeon"):      "Something's been moving out of {rname}. That road needs watching.",
    ("watch",  "castle"):       "The fortification at {rname} has been active. Hard to say whose banner.",
    ("watch",  "cave"):         "We've had reports from the direction of {rname}. Unusual movement.",
    ("watch",  "ruins"):        "Scavengers have been coming through from {rname}. Some don't leave.",
    ("vendor", "ruins"):        "Scavengers from {rname} pass through. Good for business, rough on the roads.",
    ("vendor", "cache"):        "Travelers keep asking about {rname}. Word is there's something out there.",
    ("vendor", "town"):         "Caravans from {rname} have been running light. Supply's been thin.",
    ("vendor", "dungeon"):      "Expeditions heading to {rname} pass through here. They always need ammo.",
    ("herbalist", "grove"):     "The grove near {rname} has good materials. Worth the detour.",
    ("herbalist", "swamp"):     "Useful plants near {rname}, but the ground out there is treacherous.",
    ("drover",  "plains"):      "The roads through {rname} are passable. Keep your pace up in the open.",
    ("drover",  "desert"):      "The crossing near {rname} is rough. Know your water before you head out.",
    ("drover",  "badlands"):    "Stay off the ground near {rname} if you can. Axles don't survive it.",
    ("mason",   "ruins"):       "Old stonework near {rname}. Whoever built it knew what they were doing.",
    ("mason",   "castle"):      "The fortification at {rname} — good construction. Solid work.",
    ("mason",   "mountain"):    "The stone out of {rname} is quality. Different from what we quarry here.",
    ("trapper", "forest"):      "The woods near {rname} have been active this season. Good hunting, if careful.",
    ("trapper", "tundra"):      "The cold near {rname} runs deep. If you're going out, leave early.",
    ("miller",  "farmland"):    "Harvest from {rname} has been shorter than expected. Lean season coming.",
    ("miller",  "plains"):      "Grain's been moving through from {rname}. Not enough of it, but moving.",
    ("ferryman","swamp"):       "Crossings near {rname} flood unpredictably. Ask before you cross.",
    ("kilnkeeper","volcanic"):  "Ash coming in from {rname}. Not dangerous yet, just thick.",
    ("kilnkeeper","badlands"):  "The heat near {rname} dries everything. Keep the kiln doors tight.",
    ("elder",   "monster_town"): "{rname} has been a problem since before I was running this place.",
    ("elder",   "dungeon"):     "Old expeditions to {rname} rarely came back with what they expected.",
    ("elder",   "ruins"):       "{rname} was something once. What, exactly, nobody's left to say.",
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
