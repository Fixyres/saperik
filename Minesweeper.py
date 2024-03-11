import random


def generate_mine_field(local_field_size, local_number_of_mines):
    local_mine_field = []

    for i in range(local_field_size ** 2):
        local_mine_field.append(0)

    while sum(local_mine_field) < local_number_of_mines:
        random_mine = random.randint(0, local_field_size ** 2 - 1)
        if local_mine_field[random_mine] == 0:
            local_mine_field[random_mine] = 1

    return local_mine_field


def show_mine_field(local_field_size, local_mine_field):
    for j in range(local_field_size ** 2):
        if j % local_field_size == 0:
            print("\n" + str(local_mine_field[j]) + " ", end="")
        else:
            print(str(local_mine_field[j]) + " ", end="")
    print("")


def fill_field_with_hints(local_field_size, local_mine_field):
    local_field_with_counter = []
    for i in range(local_field_size ** 2):
        if i == 0:  # left upper corner
            counter = local_mine_field[i + 1] + local_mine_field[i + local_field_size] \
                                + local_mine_field[i + local_field_size + 1]
            local_field_with_counter.append(counter)
        elif i == local_field_size - 1:  # right upper corner
            counter = local_mine_field[i - 1] + local_mine_field[i + local_field_size - 1] + \
                                local_mine_field[i + local_field_size]
            local_field_with_counter.append(counter)
        elif i == local_field_size * (local_field_size - 1):  # left bottom corner
            counter = local_mine_field[i - local_field_size] + local_mine_field[i - local_field_size + 1] \
                                + local_mine_field[i + 1]
            local_field_with_counter.append(counter)
        elif i == (local_field_size ** 2) - 1:  # right bottom corner
            counter = local_mine_field[i - local_field_size - 1] + local_mine_field[i - local_field_size] \
                                + local_mine_field[i - 1]
            local_field_with_counter.append(counter)
        elif i < local_field_size - 1:  # top row (no corners)
            counter = local_mine_field[i - 1] + local_mine_field[i + 1] \
                                + local_mine_field[i + local_field_size - 1] + local_mine_field[i + local_field_size] \
                                + local_mine_field[i + local_field_size + 1]
            local_field_with_counter.append(counter)
        elif local_field_size * (local_field_size - 1) < i < local_field_size ** 2 - 1:  # down row (no corners)
            counter = local_mine_field[i - local_field_size - 1] + local_mine_field[i - local_field_size] \
                                + local_mine_field[i - local_field_size + 1] + local_mine_field[i - 1] \
                                + local_mine_field[i + 1]
            local_field_with_counter.append(counter)
        elif i % local_field_size == 0 and i != local_field_size * (local_field_size - 1):  # left column (no corners)
            counter = local_mine_field[i - local_field_size] + local_mine_field[i - local_field_size + 1] \
                                + local_mine_field[i + 1] + local_mine_field[i + local_field_size] + \
                                local_mine_field[i + local_field_size + 1]
            local_field_with_counter.append(counter)
        elif (i + 1) % local_field_size == 0 and i != (local_field_size**2 - 1):  # right column (no corners)
            counter = local_mine_field[i - local_field_size - 1] + local_mine_field[i - local_field_size] \
                                + local_mine_field[i - 1] + local_mine_field[i + local_field_size - 1] + \
                                local_mine_field[i + local_field_size]
            local_field_with_counter.append(counter)
        else:  # center
            counter = local_mine_field[i - local_field_size - 1] + local_mine_field[i - local_field_size] \
                                + local_mine_field[i - local_field_size + 1] + local_mine_field[i - 1] + \
                                local_mine_field[i + 1] + local_mine_field[i + local_field_size - 1] + \
                                local_mine_field[i + local_field_size] + local_mine_field[i + local_field_size + 1]
            local_field_with_counter.append(counter)
    return local_field_with_counter


def show_game_field(local_field_size, local_field_with_hints, local_mine_field):
    for i in range(local_field_size ** 2):
        if i % local_field_size == 0:
            if local_mine_field[i] == "x":
                print("\n(" + str(local_field_with_hints[i]) + ")", end="")
            else:
                print("\n" + "#" + str(i), end="")
        elif i <= 10:
            if local_mine_field[i] == "x":
                print("   (" + str(local_field_with_hints[i]) + ")", end="")
            else:
                print("   #" + str(i), end="")
        else:
            if local_mine_field[i] == "x":
                print("  (" + str(local_field_with_hints[i]) + ")", end="")
            else:
                print("  #" + str(i), end="")
    return ""


def get_user_pick(local_field_size):
    while True:
        user_pick = input("\nInput the cell number you want to open: ")
        try:
            user_pick = int(user_pick)
            if user_pick < local_field_size**2:
                break
        except ValueError:
            pass
    return user_pick


def begin_game(local_field_size, local_number_of_mines):

    mine_field = generate_mine_field(local_field_size, local_number_of_mines)
    field_with_hints = fill_field_with_hints(local_field_size, mine_field)
    opened = 0

    print("\nHello!!! Welcome to Minesweeper.", end="")

    while True:
        show_game_field(local_field_size, field_with_hints, mine_field)
        pick = get_user_pick(local_field_size)
        if mine_field[pick] == 0:
            mine_field[pick] = "x"
            opened += 1
            if opened == local_field_size**2 - local_number_of_mines:
                choice = input("You won!!! \nWow!!! \nDo you want to play again? [Yes/No]: ")
                if choice.lower() == "yes":
                    begin_game(local_field_size, local_number_of_mines)
                else:
                    break

        elif mine_field[pick] == "x":
            print("\nField #" + str(pick), "already opened", end="")

        else:
            print("BOOM!!!")
            show_mine_field(local_field_size, mine_field)
            choice = input("\nDo you want to play again? [Yes/No]: ")
            if choice.lower() == "yes":
                begin_game(local_field_size, local_number_of_mines)
            else:
                break
            break


if __name__ == "__main__":
    begin_game(5, 4)
