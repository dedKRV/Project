PLAYER_CHOICE = {
    "1": "biker",
    "2": "punk",
    "3": "cyborg"
}


def select_player():
    print("Выберите персонажа:")
    for key, value in PLAYER_CHOICE.items():
        print(f"{key}: {value}")

    while True:
        choice = input("Введите номер (1/2/3): ")
        if choice in PLAYER_CHOICE:
            return PLAYER_CHOICE[choice]
        print("Неверный выбор. Попробуйте снова.")