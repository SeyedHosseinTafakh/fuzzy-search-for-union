import curses
import os
import csv

def get_target_filename(stdscr):
    """Prompts the user for a CSV filename using curses text input."""
    try:
        stdscr.clear()
        max_y, max_x = stdscr.getmaxyx()
        
        # Turn cursor and echo back on for typing
        curses.curs_set(1)
        curses.echo()
        
        prompt = "Enter CSV filename to open: "
        stdscr.addstr(max_y // 2, max_x // 8, prompt)
        stdscr.refresh()
        
        # Read user input up to 100 characters
        user_input = stdscr.getstr(max_y // 2, (max_x // 8) + len(prompt), 100)
        
        # Turn cursor and echo back off for viewing
        curses.noecho()
        curses.curs_set(0)
        
        filename = user_input.decode('utf-8').strip()
        
        if not filename:
            return -1
            
        # Automatically append .csv extension if the user didn't type it
        if not filename.lower().endswith('.csv'):
            filename += '.csv'
            
        return filename
        
    except Exception:
        return -1

def display_files(stdscr):
    # 1. Get the target filename from the user
    filename = get_target_filename(stdscr)
    if filename == -1:
        return -1

    # 2. Check if file exists and try to read it
    if not os.path.exists(filename):
        return -1

    try:
        with open(filename, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            lines = list(reader)
            
        if not lines: # Check if file is empty
            return -1
    except Exception:
        return -1  # Return -1 if reading fails (e.g., file lock, corrupt format)

    current_row = 0

    while True:
        max_y, max_x = stdscr.getmaxyx()
        stdscr.clear()
        
        # Header line displaying the file name
        title = f" Viewing File: {filename} (Press ESC to exit) "
        stdscr.addstr(0, 0, title[:max_x - 1], curses.A_REVERSE)

        # Display rows until bottom of screen is reached
        for i in range(max_y - 2):
            row_idx = current_row + i
            if row_idx < len(lines):
                row_str = " | ".join(lines[row_idx])[:max_x - 1]
                if row_idx == 0:
                    stdscr.addstr(i + 2, 0, row_str, curses.A_BOLD)
                else:
                    stdscr.addstr(i + 2, 0, row_str)

        stdscr.refresh()
        key = stdscr.getch()

        # Navigation logic
        if key == curses.KEY_DOWN and current_row + (max_y - 2) < len(lines):
            current_row += 1
        elif key == curses.KEY_UP and current_row > 0:
            current_row = max(0, current_row - 1)
        elif key == 27:  # ESC key pressed
            return filename

def main():
    # curses.wrapper safely restores terminal settings after execution
    result = curses.wrapper(display_files)
    print(f"\nExecution finished. Result returned: {result}")

if __name__ == "__main__":
    main()
