from datetime import datetime

#used by prinColor functions
COLOR_RED:str          = "\033[31m {}\033[00m"
COLOR_GREEN:str        = "\033[32m {}\033[00m"
COLOR_BLUE:str         = "\033[34m {}\033[00m"
COLOR_YELLOW:str       = "\033[33m {}\033[00m"
COLOR_PINK:str         = "\033[35m {}\033[00m"
COLOR_CYAN:str         = "\033[36m {}\033[00m"
COLOR_WHITE:str        = "\033[37m {}\033[00m"
COLOR_BLACK:str        = "\033[30m {}\033[00m"
COLOR_GRAY:str         = "\033[90m {}\033[00m"
COLOR_LIGHT_RED:str    = "\033[91m {}\033[00m"
COLOR_LIGHT_GREEN:str  = "\033[92m {}\033[00m"
COLOR_LIGHT_YELLOW:str = "\033[93m {}\033[00m"
COLOR_LIGHT_BLUE:str   = "\033[94m {}\033[00m"
COLOR_LIGHT_MAGENTA:str= "\033[95m {}\033[00m"
COLOR_LIGHT_CYAN:str   = "\033[96m {}\033[00m"
COLOR_LIGHT_WHITE:str  = "\033[97m {}\033[00m"

def debugLog(any_variable, color: str = "gray", calling_function:str="", filename:str=None) -> None:
    """ 
    print a stringin color if DEBUG_MODE=True. Also write on file if DEBUG_ON_FILE is True
    """
    DEBUG_MODE: bool    = True
    DEBUG_ON_FILE: bool = filename is not None 
    DEBUG_FILENAME:str  = filename.strip() if filename is not None else "debug_log.txt"

    timestamp: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    debug_string:str = timestamp + " - " + calling_function + " - " + str(any_variable)
    if DEBUG_MODE:
        #print('DEBUG: ', end='')  
        printColor(debug_string, color)
    
    if DEBUG_ON_FILE:
        
        try:
            with open(DEBUG_FILENAME, "a", encoding="utf-8") as file:
                file.write(debug_string + "\n")
        except Exception:
            printColor("Error writing to file: " + DEBUG_FILENAME, "red")

    return

def printColorSameLine(text: str, color:str="white"):
    """ funtion to print a text in color WITHOUT newline """
    if color.strip().lower() == "red":
        print(COLOR_RED .format(text), end="")
    elif color.strip().lower() == "green":
        print(COLOR_GREEN .format(text), end="")
    elif color.strip().lower() == "blue":
        print(COLOR_BLUE .format(text), end="")
    elif color.strip().lower() == "yellow":
        print(COLOR_YELLOW .format(text), end="")
    elif color.strip().lower() == "pink":
        print(COLOR_PINK .format(text), end="")
    elif color.strip().lower() == "cyan":
        print(COLOR_CYAN .format(text), end="")
    elif color.strip().lower() == "white":
        print(COLOR_WHITE .format(text), end="")
    elif color.strip().lower() == "black":
        print(COLOR_BLACK .format(text), end="")
    elif color.strip().lower() == "gray":
        print(COLOR_GRAY .format(text), end="")
    elif color.strip().lower() == "light_red":
        print(COLOR_LIGHT_RED .format(text), end="")
    elif color.strip().lower() == "light_green":
        print(COLOR_LIGHT_GREEN .format(text), end="")
    elif color.strip().lower() == "light_yellow":
        print(COLOR_LIGHT_YELLOW .format(text), end="")
    elif color.strip().lower() == "light_blue":
        print(COLOR_LIGHT_BLUE .format(text), end="")
    elif color.strip().lower() == "light_magenta":
        print(COLOR_LIGHT_MAGENTA .format(text), end="")
    elif color.strip().lower() == "light_cyan":
        print(COLOR_LIGHT_CYAN .format(text), end="")
    elif color.strip().lower() == "light_white":
        print(COLOR_LIGHT_WHITE .format(text), end="")

    else:
        print(text, end="")
    return


def printColor(text: str, color:str="white") -> None:
    """ print a text in the defined color """
    if color.strip().lower() == "red":
        print(COLOR_RED .format(text))
    elif color.strip().lower() == "green":
        print(COLOR_GREEN .format(text))
    elif color.strip().lower() == "blue":
        print(COLOR_BLUE .format(text))
    elif color.strip().lower() == "yellow":
        print(COLOR_YELLOW .format(text))
    elif color.strip().lower() == "pink":
        print(COLOR_PINK .format(text))
    elif color.strip().lower() == "cyan":
        print(COLOR_CYAN .format(text))
    elif color.strip().lower() == "white":
        print(COLOR_WHITE .format(text))
    elif color.strip().lower() == "black":
        print(COLOR_BLACK .format(text))
    elif color.strip().lower() == "gray":
        print(COLOR_GRAY .format(text))
    elif color.strip().lower() == "light_red":
        print(COLOR_LIGHT_RED .format(text))
    elif color.strip().lower() == "light_green":
        print(COLOR_LIGHT_GREEN .format(text))
    elif color.strip().lower() == "light_yellow":
        print(COLOR_LIGHT_YELLOW .format(text))
    elif color.strip().lower() == "light_blue":
        print(COLOR_LIGHT_BLUE .format(text))
    elif color.strip().lower() == "light_magenta":
        print(COLOR_LIGHT_MAGENTA .format(text))
    elif color.strip().lower() == "light_cyan":
        print(COLOR_LIGHT_CYAN .format(text))
    elif color.strip().lower() == "light_white":
        print(COLOR_LIGHT_WHITE .format(text))

    else:
        print(text)
    return

def printTwoColors(string1:str, color1:str, string2:str, color2:str) -> None:
    """ print two strings in different colors """
    printColorSameLine(string1, color1)
    printColor(string2, color2)
    return

def printCredits(program_name:str, version:str, author:str, date:str, copyritght:str, License:str)->None:

    printColor("\n " + program_name + " - Version: " + version, "cyan")
    printColorSameLine("Author      : ", "cyan")
    printColor(author, "blue")
    printColorSameLine("Date        : ", "cyan")
    printColor(date, "blue")
    printColorSameLine("Copyritght  : ", "cyan")
    printColor(copyritght, "blue")
    printColorSameLine("License     : ", "cyan")
    printColor(License, "blue")

    return

if __name__ == '__main__':
    print("printing_functions.py - not an executable module.")
