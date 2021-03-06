# Import the necessary packages
import sys, os, time
from socket import *

from ClientCommands import ClientCommands

from consolemenu import *
from consolemenu.items import *
import logging as log

log.basicConfig(filename="client.log", format='[CCO] %(asctime)s - %(levelname)s - %(message)s', level=log.DEBUG, force=True)

###
menu = ConsoleMenu()

block_size = 1024


###


def generate_menu():
    menu_g = ConsoleMenu("DFS control menu", "Subtitle")
    initialize_item = MenuItem("Initialize", should_exit=True)
    create_file_item = MenuItem("Create file", should_exit=True)
    read_file_item = MenuItem("Read file", should_exit=True)
    write_file_item = MenuItem("Write file", should_exit=True)
    delete_file_item = MenuItem("Delete file", should_exit=True)
    info_file_item = MenuItem("Info file", should_exit=True)
    copy_file_item = MenuItem("Copy file", should_exit=True)
    move_file_item = MenuItem("Move file", should_exit=True)
    read_directory_item = MenuItem("Read directory", should_exit=True)
    make_directory_item = MenuItem("Make directory", should_exit=True)
    delete_directory_item = MenuItem("Delete directory", should_exit=True)
    # function_item = FunctionItem("Call a Python function", function=print, args=["Enter an input", ])
    # command_item = CommandItem("Run a console command", "touch hello.txt")
    # selection_menu = SelectionMenu(["item1", "item2", "item3"], "Select option")
    # submenu_item = SubmenuItem("Submenu item", selection_menu, menu_g)
    naming_server_info_item = MenuItem("Naming Server db snapshot", should_exit=True)

    menu_g.append_item(initialize_item)
    menu_g.append_item(create_file_item)
    menu_g.append_item(read_file_item)
    menu_g.append_item(write_file_item)
    menu_g.append_item(delete_file_item)
    menu_g.append_item(info_file_item)
    menu_g.append_item(copy_file_item)
    menu_g.append_item(move_file_item)
    menu_g.append_item(read_directory_item)
    menu_g.append_item(make_directory_item)
    menu_g.append_item(delete_directory_item)
    # menu_g.append_item(function_item)
    # menu_g.append_item(command_item)
    # menu_g.append_item(submenu_item)
    menu_g.append_item(naming_server_info_item)

    return menu_g


def initialization():
    global menu
    menu = generate_menu()
    menu.show()


def main():
    print("Begin initialization...")
    log.info("Begin initialization...")
    client_commander = ClientCommands(input())
    initialization()
    print("Initialized successfully")
    log.info("Initialized successfully")
    while True:
        print("Selected menu item: %s" % menu.selected_item.text)
        log.info("Selected menu item: %s" % menu.selected_item.text)

        client_commander.dispatch_command(menu.selected_item.text)
        menu.show()


if __name__ == "__main__":
    main()
