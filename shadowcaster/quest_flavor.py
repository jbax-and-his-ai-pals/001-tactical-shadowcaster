DELIVERY_INTROS = {
    "farmland": [
        "The stores at {work} need moving before the wagons turn.",
        "Hands at {work} are short on runners and the loads cannot wait.",
    ],
    "desert": [
        "Caravans leaving {town} are stretched thin across the heat.",
        "The road wardens near {civic} are asking for a reliable desert handoff.",
    ],
    "swamp": [
        "The marsh routes around {town} have gone soft and unreliable.",
        "People near {civic} want this moved before the bog closes another path.",
    ],
    "mountain": [
        "The pass settlements tied to {town} are short on steady runners.",
        "Word from {civic} is that the high road needs dependable couriers again.",
    ],
    "tundra": [
        "Cold weather has cut the easy routes out of {town}.",
        "The folk around {home} are sending only essential loads through the frost.",
    ],
    "volcanic": [
        "The ash roads beyond {town} are too rough for casual couriers.",
        "Workers near {work} need a careful hand through the hot country.",
    ],
    "default": [
        "A neighboring settlement needs a dependable courier.",
        "Someone in {town} is asking for a clean handoff beyond the usual roads.",
    ],
}

SCOUT_INTROS = {
    "forest": [
        "The woods beyond {town} have gone quiet in an unusual way.",
        "Hunters passing {home} brought back reports that do not match each other.",
    ],
    "swamp": [
        "No one near {civic} trusts the marsh reports secondhand.",
        "The bog trails east of {town} keep changing faster than the stories about them.",
    ],
    "mountain": [
        "The pass watchers at {civic} want fresh eyes on the road.",
        "Talk around {town} says the high trail is behaving strangely again.",
    ],
    "tundra": [
        "Tracks vanish quickly in the frost, so timing matters.",
        "The people at {home} want a firsthand look before the weather wipes the sign away.",
    ],
    "desert": [
        "Caravan talk reaching {work} is too muddled to trust on its own.",
        "The road stories coming through {town} need a proper field report.",
    ],
    "volcanic": [
        "Too many ash-road rumors are contradicting each other near {town}.",
        "The hall at {civic} wants a clean account before posting more routes.",
    ],
    "default": [
        "The town wants a firsthand report from the road.",
        "People around {civic} are asking for eyes on a nearby route.",
    ],
}

BOUNTY_INTROS = {
    "forest": [
        "The wardens near {civic} want the trail made safe again.",
        "Something is worrying the routes that feed back into {town}.",
    ],
    "plains": [
        "Open ground means these threats are hitting traffic too easily.",
        "Folks at {work} want the surrounding road pack thinned out.",
    ],
    "farmland": [
        "The fields tied to {work} are drawing trouble again.",
        "The outlying farms near {town} need someone to cut the pressure down.",
    ],
    "desert": [
        "The road captains passing through {civic} are losing patience with these stalkers.",
        "This stretch of heat country is costing {town} too many safe crossings.",
    ],
    "swamp": [
        "The marsh edge is chewing up too many decent routes out of {town}.",
        "People at {civic} want the swamp-side pressure reduced before it spreads.",
    ],
    "mountain": [
        "The pass out of {town} is only useful if someone keeps the ambushers down.",
        "The climb beyond {civic} has become too dangerous for normal traffic.",
    ],
    "default": [
        "The roads out of {town} need firm hands again.",
        "This threat has lingered long enough that {civic} is posting coin for it.",
    ],
}

CHAIN_RETURN_LINES = {
    "farmland": "The board at {civic} wants the account back while the work crews can still use it.",
    "swamp": "Bring the account back before the marsh changes the route again.",
    "mountain": "Report back before the pass shifts and the trail story changes with it.",
    "tundra": "Return quickly; good trail knowledge does not last long in this weather.",
    "desert": "Bring it back while the caravan captains can still act on it.",
    "volcanic": "Report back before ash and heat make the trail read differently again.",
    "default": "Return to {town} afterward.",
}


def _pick(options, seed_value):
    return options[seed_value % len(options)]


def flavored_text(table, biome, context, seed_value):
    options = table.get(biome, table["default"])
    return _pick(options, seed_value).format(**context)
