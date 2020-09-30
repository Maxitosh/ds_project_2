from consolemenu import SelectionMenu
a_list=["red", "blue", "green"]

menu = SelectionMenu(a_list,"Select an option")

menu.show()

menu.join()

selection = menu.selected_option
