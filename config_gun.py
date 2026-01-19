player = 1  # (1-3)
gun = 1    # (1-3)

def get_player_choice():
    """Получить выбор персонажа"""
    if player == 1:
        return "biker"
    elif player == 2:
        return "punk"
    elif player == 3:
        return "cyborg"
    else:
        return "biker"

def get_gun_choice():
    """Получить выбор оружия"""
    if gun == 1:
        return "1"
    elif gun == 2:
        return "2"
    elif gun == 3:
        return "3"
    else:
        return "1"

def select_player():
    return get_player_choice()
PLAYER_CHOICE = get_player_choice()
WEAPON_CHOICE = get_gun_choice()

def get_config():
    return {
        "player": get_player_choice(),
        "weapon": get_gun_choice()
    }