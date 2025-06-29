THE_PROGRAM="smart_renamer.py"
THE_VERSION="1.0.0"
THE_AUTHOR="Antonio Romeo"
THE_DATE="2025-06-28"
THE_COPYRIGHT="Antonio Romeo © 2024, 2025"
THE_LICENSE="MIT License"


import os
import sys
import getopt
from rom_print import printColor, printCredits, printTwoColors
from pdf_utils import pdf_to_images_to_filename, list_pdf_in_folder, get_file_date


def showHelp():
    print("Usage: python " + THE_PROGRAM + " [OPTIONS]")
    print("Options:")
    print("  -p, --pdf_folder <folder>         Specify the folder containing PDFs")
    print("  -h, --help                        Show this help message")
    print("Example:")
    print("  python " + THE_PROGRAM + " -p PDF")
    print("  python " + THE_PROGRAM + " -h")
    print("  python " + THE_PROGRAM + " --help")


#################   MAIN STARTS HERE   ##################################
def main():

    PDF_FOLDER: str = "PDF"
    PDF_DONE_FOLDER = os.path.join(PDF_FOLDER, "DONE")
    LOG_FILE: str = "smart_renamer.log"


    # Remove 1st argument from the list of command line arguments
    argumentList: list[str] = sys.argv[1:]
    # Options
    options = "p:h"
    # Long options
    long_options: list[str] = ["pdf_folder=", "help"]

    try:
        # Parsing argument
        arguments, values = getopt.getopt(argumentList, options, long_options)
        for currentArgument, currentValue in arguments:
    
            if currentArgument in ("-p", "--pdf_folder"):
                
                currentValue = os.path.normpath(currentValue)

                if os.path.isdir(currentValue):
                    PDF_FOLDER = currentValue
                    PDF_DONE_FOLDER = os.path.join(PDF_FOLDER, "DONE")
                else:
                    printColor("Invalid argument (not a dir): " + currentArgument + " " + currentValue + ". Using default:" + str(PDF_FOLDER), "red")

                #create the PDF_DONE_FOLDER if it does not exist
                if not os.path.exists(PDF_DONE_FOLDER):
                    try:
                        os.makedirs(PDF_DONE_FOLDER)
                        printColor(f"Created folder: {PDF_DONE_FOLDER}", "green")
                    except Exception as e:
                        printColor(f"Failed to create folder {PDF_DONE_FOLDER}: {str(e)}", "red")
                        os._exit(1)

            elif currentArgument in ("-h", "--help"):
                showHelp()
                os._exit(0)

            else:
                showHelp()
                os._exit(1)

    except getopt.error as err:
        # output error, and return with an error code
        print("Argument parsing error: " + str(err))
        showHelp()
        os._exit(2)

    #BUILD the full path for log file (inside the PDF_FOLDER)
    LOG_FILE = os.path.join(PDF_FOLDER, LOG_FILE)
    # if log file already exists, rename it to .old and create a new one. if .old eists, delete it
    if os.path.exists(LOG_FILE):
        old_log_file = LOG_FILE + ".old"
        if os.path.exists(old_log_file):
            os.remove(old_log_file)
        os.rename(LOG_FILE, old_log_file)
        printColor(f"Renamed existing log file to: {old_log_file}", "yellow")
    
    #write "PDF_ORIGINAL_FILNAME, PDF_NEW_FILENAME" to the log file
    with open(LOG_FILE, 'w', encoding="utf-8") as log_file:
        log_file.write("PDF_ORIGINAL_FILENAME, PDF_NEW_FILENAME\n")
        printColor(f"Created log file: {LOG_FILE}", "green")

    printCredits(THE_PROGRAM, THE_VERSION, THE_AUTHOR, THE_DATE, THE_COPYRIGHT, THE_LICENSE)
    printTwoColors("PDF Folder: ", "white", PDF_FOLDER, "green")
    printTwoColors("PDF_DONE_FOLDER: ", "white", PDF_DONE_FOLDER, "green")
    printTwoColors("LOG_FILE: ", "white", LOG_FILE, "green")


    my_pdfs:list[str] = list_pdf_in_folder(PDF_FOLDER)
    #CVs = read_pdfs_from_folder_with_pdfplumber(PDF_FOLDER)

    how_many_pdfs: int = len(my_pdfs)
    if how_many_pdfs == 0:
        printColor("No PDF found in folder: " + PDF_FOLDER, "red")
        os._exit(3)
    else:
        printColor(f"{THE_PROGRAM} - Found {how_many_pdfs} PDFs in folder: " + PDF_FOLDER, "green")

    pdf_count:int = 0

    message_to_log: str = ""

    # Create the PDF_DONE_FOLDER if it does not exist
    if not os.path.exists(PDF_DONE_FOLDER):
        os.makedirs(PDF_DONE_FOLDER)

    # Process each CV using the filename and the text content
    for the_pdf in my_pdfs:
        pdf_count += 1
        printTwoColors(f"Looking at PDF {pdf_count}/{how_many_pdfs}: ", "green", the_pdf, "pink")

        the_new_filename: str = pdf_to_images_to_filename(the_pdf) 

        if the_new_filename is not None and the_new_filename != "":
            the_new_filename= the_new_filename + ".pdf"

            #if starts with "0000-00-00" then  replace the "0000-00-00" with the original file date
            if the_new_filename.startswith("0000-00-00"):
                original_file_date:str = get_file_date(the_pdf)
                new_pdf_path = the_new_filename.replace("0000-00-00", original_file_date)
                the_new_filename = new_pdf_path
                printColor(f"Date not found. replacing with original file date: {original_file_date}", "red")

            # if the file exist in the PDF_DONE_FOLDER, append the pdf_count to the filename
            if os.path.exists(os.path.join(PDF_DONE_FOLDER, the_new_filename)):
                base, ext = os.path.splitext(the_new_filename)
                the_new_filename = f"{base}_{pdf_count}{ext}"
                printColor(f"File already exists in DONE folder. Renaming to {the_new_filename}", "yellow")

            printTwoColors(f"New filename for pdf {pdf_count}:", "green", the_new_filename, "pink")

            try:

                #os.rename(the_pdf, the_new_filename)
                # Move the renamed PDF to the DONE folder
                new_pdf_path: str = os.path.join(PDF_DONE_FOLDER, os.path.basename(the_new_filename))

                os.rename(the_pdf, new_pdf_path)
                the_new_filename = new_pdf_path  # Update the new filename to the moved path
                
                message_to_log = f"{the_pdf}, {the_new_filename}"

                printColor(f"Moved PDF {pdf_count} to DONE folder: {the_new_filename}", "green")
                printColor(f"Renamed PDF {pdf_count} from {the_pdf} *** to *** {the_new_filename}", "green")
                
            except Exception as e:
                printColor(f"Failed to rename PDF {pdf_count} from {the_pdf} to {the_new_filename}: {str(e)}", "red")
                # Log the original and new filenames
                message_to_log = f"{the_pdf}, Error renaming"
        else:
            printColor(f"Failed to find a new name for PDF {pdf_count}: {the_pdf}", "red")
            message_to_log = f"{the_pdf}, No new name found"            
            
        with open(LOG_FILE, 'a', encoding="utf-8") as log_file:
            log_file.write(f"{message_to_log}\n")

    print("that's all folks!")

if __name__ == "__main__":
    main()

# MIT License
# 
# Copyright (c) [2024] [Antonio Romeo]
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

