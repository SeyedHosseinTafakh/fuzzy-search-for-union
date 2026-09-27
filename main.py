import curses
import glob
import os
import csv
from pathlib import Path
import pandas as pd
from rapidfuzz import process, fuzz

def search_dataframe(df, query, threshold=60, id_col='id'):
    searchable_cols = [
        col for col in df.columns 
        if (col != id_col or id_col not in df.columns) and df[col].notna().any()
    ]
    
    if not searchable_cols:
        return pd.DataFrame(columns=df.columns)
    
    search_corpus = df[searchable_cols].astype(str).agg(' '.join, axis=1).tolist()
    
    matches = process.extract(
        query, 
        search_corpus, 
        scorer=fuzz.partial_token_set_ratio, 
        score_cutoff=threshold
    )
    
    if not matches:
        return pd.DataFrame(columns=df.columns)
        
    matched_positions = [idx for text, score, idx in matches]
    scores = [score for text, score, idx in matches]
    
    results = df.iloc[matched_positions].copy()
    #results['match_score'] = scores    
    return results

def read_csv_files():
    """
    Returns a list of strings representing the names of all .csv files 
    in the current working directory. Works cleanly across Windows paths.
    """
    # Get the current working directory
    current_dir = Path.cwd()
    
    # Find all files ending in .csv (case-insensitive on Windows)
    # .name extracts just 'data.csv' instead of the full 'C:/Users/.../data.csv'
    csv_files = [file.name for file in current_dir.glob("*.csv")]   
    #return [str(file.resolve()) for file in Path(".").glob("*.csv")]
    return csv_files
    
def main(stdscr):
    data_b = [
    {'id': 1, 'company': 'Acme Corp', 'postal_code': '12345', 'country': 'Iran'},
    {'id': 2, 'company': 'Tech Solutions', 'postal_code': '67890', 'country': 'Turkey'}
    ]
    db = pd.DataFrame(data_b)
    result = pd.DataFrame()

    search_query = ""
    # Hide the blinking block cursor for cleaner lock
    curses.curs_set(0)
    #stdscr.addstr(0, 0, f": {current_query}")
    curses.noecho()
    # main interactive loop
    screen_controll = "0"
    searched_file_name = "";

    while True:
        if screen_controll == "0":
            stdscr.clear()
            #display_files(stdscr)
            stdscr.addstr(0, 0, f"please select one of this options")
            stdscr.addstr(1, 0, "-"*40)
            stdscr.addstr(4, 0, f"1 : Search your directory for csv files to upload.")
            stdscr.addstr(8, 0, f"2 : Use the default demo data.")
            stdscr.addstr(12, 0, f"3 : Press ESC to exit.")
            stdscr.refresh()
            key = stdscr.getch()
            if key == 27:
                return 0;
            if chr(key) == "1":
                screen_controll = "01"
                stdscr.refresh()
                continue
            if chr(key) =="2":
                screen_controll = "001"
                stdscr.refresh()
                continue
        if screen_controll == "01":
            stdscr.clear()
            files = read_csv_files()
            if not files:
                stdscr.addstr(0, 0, "No CSV files found in this directory. Press any key to exit.")
                stdscr.refresh()
                stdscr.getch()
                return 0;
            file_index = 0
            stdscr.addstr(0, 0, f"please type the name of file :{searched_file_name}")
            stdscr.refresh()
            print(files)

            key = stdscr.getch()
            if key == 27:
                return 0;
            if key == 127 or key == 8 or key == curses.KEY_BACKSPACE:
                searched_file_name = searched_file_name[:-1]
            elif key in (10, 13, curses.KEY_ENTER):
                # search for the entered csv file
                if searched_file_name in files:
                    print(searched_file_name in filepath)
                    #todo error
                    db = pd.read_csv(searched_file_name)
                    screen_controll = "001"
                    stdscr.clear()
                    stdscr.refresh()                    
                    continue
                else:
                    stdscr.clear()
                    stdscr.refresh()
                    stdscr.addstr(0, 0, f"the file name not found, Press any key to exit")
                    stdscr.getch()
                    return 0;
            else:
                searched_file_name = searched_file_name+chr(key)

        if screen_controll == "001":
            stdscr.clear()
            result = search_dataframe(db, query=search_query, threshold=60)

            for row2 in result.itertuples():
                line_string2 = " ".join(str(getattr(row2, field)) for field in row2._fields)
                stdscr.addstr(line_rows,0,line_string2)
                line_rows = line_rows+1
                stdscr.refresh()
            max_y, max_x = stdscr.getmaxyx()
            stdscr.addstr(max_y-1,0,"Press Esc to exit.")
            stdscr.addstr(max_y-2,0,"|"*(max_x))
            max_y = max_y -3
            for row in db.head(5).itertuples(index=False):
                line_string = " ".join(str(getattr(row, field)) for field in row._fields)
                stdscr.addstr(max_y,0,line_string)
                max_y = max_y-1
            stdscr.addstr(max_y-4,0,"|"*(max_x))
            stdscr.addstr(max_y-2,0,"**** DATABASE ****")
            stdscr.addstr(0, 0, f"search :{search_query}")

            max_y = max_y - 8
            line_rows = 4
            key = stdscr.getch()
            if key == 27:
                return 0;
            if key == 127 or key == 8 or key == curses.KEY_BACKSPACE:
                search_query = search_query[:-1]
                result = search_dataframe(db, query=search_query, threshold=60)
                stdscr.refresh()
            else:
                search_query = search_query+chr(key)
                result = search_dataframe(db, query=search_query, threshold=60)
            if line_rows == max_y:
                continue
curses.wrapper(main)
