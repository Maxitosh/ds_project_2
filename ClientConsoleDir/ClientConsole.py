# Import the necessary packages
import sys, os, time
from socket import *

block_size = 1024
from consolemenu import *
from consolemenu.items import *

###
menu = ConsoleMenu()


###

def client(host, port, message):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect((host, port))

    # send filename
    sock.send(message.encode())
    sock.close()


def generate_menu():
    menu_g = ConsoleMenu("DFS control menu", "Subtitle")
    menu_item = MenuItem("Menu Item", should_exit=True)
    function_item = FunctionItem("Call a Python function", function=print, args=["Enter an input", ])
    command_item = CommandItem("Run a console command", "touch hello.txt")
    selection_menu = SelectionMenu(["item1", "item2", "item3"], "Select option")
    submenu_item = SubmenuItem("Submenu item", selection_menu, menu_g)

    menu_g.append_item(menu_item)
    menu_g.append_item(function_item)
    menu_g.append_item(command_item)
    menu_g.append_item(submenu_item)

    return menu_g


def initialization():
    global menu
    menu = generate_menu()
    menu.show()


def main():
    initialization()

    while True:
        print(menu.selected_item.text)
        client("NamingServer", 8800, "message123")
        menu.show()


if __name__ == "__main__":
    main()
