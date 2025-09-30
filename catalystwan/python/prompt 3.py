import os
import sys

# Platform-specific imports for getch (get character) functionality
if os.name == "nt":  # Windows
    import msvcrt
else:  # Unix-like (Linux, macOS)
    import termios
    import tty


class Prompt:
    @staticmethod
    def _getch():
        """
        Reads a single character from stdin without echoing it to the console.
        Handles cross-platform differences (Windows vs. Unix-like).
        """
        if os.name == "nt":
            # For Windows, msvcrt.getch() returns bytes, decode to string
            return msvcrt.getch().decode("utf-8")
        else:
            # For Unix-like systems, use tty and termios
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())  # Set terminal to raw mode
                ch = sys.stdin.read(1)  # Read a single character
            finally:
                termios.tcsetattr(
                    fd, termios.TCSADRAIN, old_settings
                )  # Restore old settings
            return ch

    @staticmethod
    def _print_menu(keys, current_selection):
        """
        Prints the menu options, highlighting the currently selected item.
        Uses ANSI escape codes for coloring.
        """
        for i, key in enumerate(keys):
            if i == current_selection:
                # Cyan color for selected item
                sys.stdout.write(f"\033[96m> {i + 1}. {key}\033[0m\n")
            else:
                sys.stdout.write(f"  {i + 1}. {key}\n")
        sys.stdout.write(
            "\nEnter your choice (use arrow keys, Enter to select, Ctrl+C to quit): "
        )
        sys.stdout.flush()  # Ensure output is immediately displayed

    @staticmethod
    def _clear_menu_lines(num_lines):
        """
        Clears the specified number of lines from the console, moving the cursor up.
        Uses ANSI escape codes.
        """
        # Erase the current line (the prompt line)
        sys.stdout.write("\033[K")
        # Move cursor up and erase for the remaining lines
        for _ in range(num_lines - 1):  # -1 because the first line was already handled
            sys.stdout.write("\033[F\033[K")  # Move up to previous line, then erase
        sys.stdout.flush()

    @staticmethod
    def dict_menu(options_dict):
        """
        Displays a menu from a dictionary of options, allowing navigation with arrow keys.
        Returns the selected option's name and function.
        """
        keys = list(options_dict.keys())
        num_options = len(keys)
        current_selection = 0

        # Initial print of the menu
        sys.stdout.write("\n")  # Start with a new line for cleaner initial display
        Prompt._print_menu(keys, current_selection)

        # Calculate total lines occupied by the menu + prompt for clearing purposes
        # Each option takes 1 line + 1 line for the blank line before prompt + 1 line for the prompt itself
        menu_display_lines = num_options + 2

        while True:
            key = Prompt._getch()

            if key == "\x1b":  # ANSI escape sequence start (usually for arrow keys)
                # Read the next two characters to identify the specific arrow key
                # e.g., \x1b[A for Up, \x1b[B for Down
                try:
                    next_char = Prompt._getch()
                    if next_char == "[":
                        arrow_key = Prompt._getch()
                        if arrow_key == "A":  # Up arrow
                            current_selection = (
                                current_selection - 1 + num_options
                            ) % num_options
                        elif arrow_key == "B":  # Down arrow
                            current_selection = (current_selection + 1) % num_options
                except Exception:
                    # Handle cases where not enough characters are read (e.g., malformed escape sequence)
                    pass  # Just ignore and continue

                # Clear and redraw menu after arrow key press
                Prompt._clear_menu_lines(menu_display_lines)
                Prompt._print_menu(keys, current_selection)

            elif (
                key == "\r" or key == "\n"
            ):  # Enter key (Windows uses '\r', Unix uses '\n' or '\r')
                # Clear the menu one last time before returning
                Prompt._clear_menu_lines(menu_display_lines)
                selected_option_name = keys[current_selection]
                selected_function = options_dict[selected_option_name]
                return selected_option_name, selected_function

            elif key == "\x03":  # Ctrl+C (ASCII for End of Text, used for interrupt)
                # Clear the menu and exit gracefully
                Prompt._clear_menu_lines(menu_display_lines)
                print("Operation cancelled by user.")
                raise SystemExit  # Propagate SystemExit for graceful shutdown

            # Ignore other keys for now, they won't affect selection or exit
