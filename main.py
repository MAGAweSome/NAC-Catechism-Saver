import requests
from bs4 import BeautifulSoup
from gtts import gTTS
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from alive_progress import alive_bar

import os


# Function to create directories if they don't exist
def create_directories_if_not_exist(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# Function to determine the appropriate numbering format
def get_numbering_format(link):
    # Define global variables
    global leading_number_content
    global current_leading_number

    if leading_number_content == False:
        numbering_format = f"0.{current_leading_number} "
        current_leading_number += 1  # Use += to increment
        return numbering_format
    else:
        numbering_format = f"14.{current_leading_number} "
        current_leading_number += 1  # Use += to increment
        return numbering_format
    
# This will create Html files also
def create_html_files():
    # Create a new HTML file within the Catechism directory
    html_file_path = os.path.join(base_directory, f"{file_name}.html")
    with open(html_file_path, "w", encoding="utf-8") as file:
        file.write(
            f"<!DOCTYPE html>\n<html>\n<head>\n<title>{link}</title>\n</head>\n<body>\n{content}\n</body>\n</html>"
        )

# Defining a variable to see if the leading number after introductiuon hhas been triggered yet
leading_number_content = False
current_leading_number = 1
user_would_like_html = False

# Check if the 'Catechism' folder exists
if not os.path.exists('Catechism'):
    # If it doesn't exist, create the folder
    os.makedirs('Catechism')

print("Hello, Welcome to The Catechism to mp3 builder.")
print("This script will create an html file and a mp3 of every section of the Catechism.")

# Setting up Chrome options for headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")  # Runs Chrome in headless mode

# Create a WebDriver instance for headless Chrome
#driver = webdriver.Chrome(options=chrome_options)
service = Service(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# URL of the webpage to scrape
url = "https://nak.org/en/abouttheNAC/catechism?id=toc"

# Open the URL in the headless browser
driver.get(url)

# Sending an HTTP GET request to fetch the webpage content
response = requests.get(url)

# Checking if the request was successful (status code 200)
if response.status_code == 200:
    # Parsing the webpage content using BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")

    # Finding all divs with class "padder"
    all_padder_divs = soup.find_all("div", class_="padder")

    # Retrieving the last "padder" div
    if all_padder_divs:
        last_padder_div = all_padder_divs[-1]  # Selecting the last div from the list

        # Extracting text from the first h1 tag in the last "padder" div
        first_h1_text = (
            last_padder_div.find("h1").get_text()
            if last_padder_div.find("h1")
            else "No_Title"
        )

        # Extracting all text within the last "padder" div on the content page
        content_links = last_padder_div.get_text("\n").splitlines()

        # Filter out empty elements from content_links
        content_links = [link.strip() for link in content_links if link.strip()]

        # Remove the "Content" tag from the array3
        content_links = content_links[1:]

        # Items to be excluded from the content_links
        # This will ask the user what they would like not saved
        # exclude_items = ["Content", "Glossary", "Index", "Index of Bible references"]
        exclude_items = []

        # Ask the user what they would not like downloaded part from the content links
        while True:
            confirm = input("Would you like to exclude any parts of the Catechism? (Yes/No): ").lower()
            if confirm == "yes":
                print("To exclude a section, please copy and paste the exact heading from the content page. \nYou will need to enter one heading at a time. For example, if you don’t want to include “1.1.1 God reveals Himself as the Creator”, type that heading and press enter.\nThen, add the next heading you want to exclude.")
                while True:
                    exclusion = input(
                        "What would you like to exclude? Enter 'Done' when finished: "
                    )
                    if exclusion.lower() == "done":
                        break
                    else:
                        exclude_items.append(exclusion)
                break
            elif confirm == "no":
                exclude_items = []
                break
            else:
                print("Invalid input. Please enter 'Yes' or 'No'.")     

        # Show the current excluded items and makre sure thats what the user wants
        while True:
            if exclude_items:
                print("Excluded items:", exclude_items)
            else:
                print("Excluded items: None")

            confirm = input("Is this exclusion list correct? (Yes/No): ").lower()
            if confirm == "yes":
                break
            elif confirm == "no":
                exclude_items = []
                while True:
                    exclusion = input(
                        "Let's remake the exclusion list. Make sure to double check your entry before pressing enter. Enter 'Done' when finished: "
                    )
                    if exclusion.lower() == "done":
                        break
                    else:
                        exclude_items.append(exclusion)
            else:
                print("Invalid input. Please enter 'Yes' or 'No'.")

        # Ask if the user wants the html files also
        while True:
            confirm = input("Would you also like html files? (Yes/No): ").lower()
            if confirm == "yes" or confirm == "no":
                if confirm == "yes":
                    user_would_like_html = True
                break
            else:
                print("Invalid input. Please enter 'Yes' or 'No'.")

        # Remove specified items from content_links
        content_links = [
            link
            for link in content_links
            if all(exclude not in link for exclude in exclude_items)
        ]

        # Setting the base directory for where the links and html will be stored
        base_directory = "Catechism"

        with alive_bar(len(content_links)) as bar:
            for link in content_links:
                # Get the appropriate leading number for the current link
                if not link[0].isdigit():
                    numbering_format = get_numbering_format(link)
                else:
                    leading_number_content = True
                    current_leading_number = 1

                # Make the html file for the given link
                try:
                    # Find the link element by its text ("Introduction")
                    intro_link = driver.find_element(By.LINK_TEXT, link)

                    # Click the "Introduction" link
                    intro_link.click()

                    # Get the page source after clicking the "Introduction" link
                    page_source = driver.page_source

                    # Parsing the webpage content using BeautifulSoup
                    soup = BeautifulSoup(page_source, "html.parser")

                    # Finding all divs with class "padder"
                    all_padder_divs = soup.find_all("div", class_="padder")

                    # Checking if the third "padder" div is available
                    if len(all_padder_divs) >= 3:

                        third_padder_div = all_padder_divs[
                            2
                        ]  # Selecting the third div from the list (index 2)

                        # Get the HTML representation of the third "padder" div
                        content = third_padder_div.prettify()

                        # This will make the file name for saving purposes
                        if not link[0].isdigit():
                            # If the file name doesn't not already have a leading digit, add one
                            file_name = f"{numbering_format}{link}"
                        else:
                            # If the file name already has a leading digit, don't add one
                            file_name = f"{link}"
                        
                        if user_would_like_html:
                            create_html_files()

                        # Make a variable called text_to_convert, This will grab all the text on the desired webpage that
                        # will be translated into mp3

                        # Extracting all text content within the third "padder" div
                        text_to_convert = third_padder_div.get_text()

                        # Converting extracted text to speech
                        tts = gTTS(text=text_to_convert, lang="en")

                        # Saving the audio file within the Catechism directory
                        audio_file_path = os.path.join(base_directory, f"{file_name}.mp3")
                        tts.save(audio_file_path)
                    else:
                        print(
                            f'The third div with class "padder" was not found on the {link} webpage.'
                        )

                except Exception as e:
                    print(f"An error occurred: {e}")

                # Navigate back to the previous page before the next iteration
                driver.back()
                #update progress bar
                bar()


        # Close the browser
        driver.quit()

    else:
        # Error message if "padder" div not found
        print('Divs with class "padder" not found on the Content webpage.')

else:
    # Error message if request failed
    print("Failed to fetch the webpage. Status code:", response.status_code)
