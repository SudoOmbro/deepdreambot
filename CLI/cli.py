from CLI.commands import COMMANDS, Command


def get_command(context) -> (Command or None) and bool:
    command_string: str = input("enter command: ")
    get_info = command_string[0] == "?"
    if get_info:
        command_string = command_string[1:]
    split_string = command_string.split(" ")
    if len(split_string) == 0:
        return None
    cmd = COMMANDS.get(split_string[0], None)
    if not cmd:
        print(f"Invalid command '{split_string[0]}'")
        return None, False
    if len(split_string) != 1:
        return cmd(split_string[1:], context), get_info
    return cmd([], context), get_info


def cli():
    context = {
        "name": input("enter name: "),
        "surname": input("enter surname: ")
    }
    while True:
        command, info = get_command(context)
        if command:
            if info:
                print(command)
            elif command.execute():
                return
