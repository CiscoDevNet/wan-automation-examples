# Simple prompt menu using simple-term-menu

from simple_term_menu import TerminalMenu


class Prompt:
    def menu(options):
        terminal_menu = TerminalMenu(options)
        menu_entry_index = terminal_menu.show()
        if menu_entry_index is None:
            raise SystemExit
        selection = options[menu_entry_index]
        return selection

    def dict_menu(dict_options):
        selection = Prompt.menu(
            list(dict_options.keys())
        )  # Convert keys to list and make a menu
        selected_function = dict_options.get(
            selection
        )  # Get the method that corresponds to the selected key
        selected_function()  # Invoke the method
