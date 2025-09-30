# File: prompt.py

from simple_term_menu import TerminalMenu


class Prompt:
    # This 'menu' method is a helper for dict_menu, not directly used by config_groups_test.py's main loop.
    # It can remain as is, or be removed if dict_menu is the only public interface.
    @staticmethod
    def menu(options):
        terminal_menu = TerminalMenu(options)
        menu_entry_index = terminal_menu.show()
        if menu_entry_index is None:
            raise SystemExit  # User pressed Ctrl+C or Esc
        selection = options[menu_entry_index]
        return selection

    @staticmethod
    def dict_menu(dict_options):
        """
        Displays a menu from a dictionary of options using simple_term_menu
        and returns the selected option's name and its corresponding function.
        """
        keys = list(dict_options.keys())

        terminal_menu = TerminalMenu(keys)
        menu_entry_index = terminal_menu.show()

        if menu_entry_index is None:
            # User cancelled (e.g., pressed Ctrl+C or Esc)
            raise SystemExit

        selected_option_name = keys[menu_entry_index]
        selected_function = dict_options.get(selected_option_name)

        # IMPORTANT CHANGE:
        # Instead of invoking selected_function() here, we return it.
        # This allows config_groups_test.py to invoke it and print banners around it.
        return selected_option_name, selected_function
