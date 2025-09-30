# Simple prompt with numbered options


class Prompt:
    @staticmethod
    def dict_menu(options_dict):
        """
        Displays a menu from a dictionary of options and returns the selected option's name and function.
        """
        keys = list(options_dict.keys())
        for i, key in enumerate(keys):
            print(f"  {i + 1}. {key}")

        while True:
            try:
                choice = input("\nEnter your choice: ")
                if not choice.isdigit():
                    print("Invalid input. Please enter a number.")
                    continue

                choice = int(choice) - 1
                if 0 <= choice < len(keys):
                    selected_option_name = keys[choice]
                    selected_function = options_dict[selected_option_name]
                    return (
                        selected_option_name,
                        selected_function,
                    )  # Return the name and the function
                else:
                    print("Invalid choice. Please enter a number from the menu.")
            except Exception as e:
                print(f"An unexpected error occurred in menu selection: {e}")
                # Continue loop to re-prompt
