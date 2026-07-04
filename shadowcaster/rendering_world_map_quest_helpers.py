def world_map_active_quests_for_coord(game, coord):
    entries = []
    for quest in game.active_quests:
        if quest.status != "active":
            continue
        if quest.from_world_pos != coord and quest.to_world_pos != coord:
            continue
        if quest.to_world_pos == coord:
            if quest.kind == "delivery":
                role = "Delivery Destination"
            elif quest.kind == "scout" and quest.stage == 0:
                role = "Scout Destination"
            elif quest.kind == "bounty" and quest.stage == 0:
                role = "Bounty Grounds"
            elif quest.kind == "chain" and quest.stage <= 1:
                role = game.board_kind_label(quest).title()
            else:
                role = "Quest Destination"
        else:
            if quest.kind in {"scout", "bounty"} and quest.stage >= 1:
                role = "Turn-In"
            elif quest.kind == "chain" and quest.stage >= 2:
                role = "Return Point"
            else:
                role = "Posted Here"
        entries.append((role, quest))
    return entries
