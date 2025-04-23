from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from Trie import Trie

import os
import time

class WordleSolver:
    def __init__(self, driver_path: str, words_path: str):

        """
        Creates driver and trie object
        
        Args:
            driver_path (str): Path to the ChromeDriver executable.
            words_path (str): Path to the CSV file containing words.
        """
        service = Service(executable_path=driver_path) 
        self.driver = webdriver.Chrome(service=service)

        # Open a webpage
        self.driver.get("https://www.nytimes.com/games/wordle/index.html")
        
        self.trie = Trie()
        self.trie.create_dict(words_path)
    

    def enter_main_screen(self):
        """
        Closes card for updated terms, clicks the play button and closes the instructions pop up
        """
        #==============( Search of "We've updated our terms card..." )=================================
        elements = self.driver.find_elements(By.CLASS_NAME, "purr-blocker-card__button")

        if elements:
            try:
                elements[0].click() # close it if found
                print("Closed Card")
            except ElementClickInterceptedException:
                print("Couldn't close 'We've updated our terms card...'")


        #==============( Click "Play" button )=================================
        play_button = self.driver.find_element(By.XPATH, '//*[@data-testid="Play"]')

        if play_button:
            try:
                play_button.click() # close it if found
                print("Clicked 'PLAY' button")
            except ElementClickInterceptedException:
                print("'PLAY' button is not clickable at the moment.")

        #==============( Close Instructions )=================================
        # Wait up to 2 seconds for the element to appear
        try:
            close_button = WebDriverWait(self.driver, 2).until(
                EC.presence_of_element_located((By.CLASS_NAME, "Modal-module_closeIcon__TcEKb"))
            )
            close_button.click()
            print("Element clicked successfully.")
        except:
            print("Element not found.")




    def play_game(self):
        """
        Plays the game by trying words and getting feedback from the game.
        """
        
        self.enter_main_screen() # enter main screen
        
        word = os.getenv("firstword")
        for i in range(6):
            if i == 0:
                # Calculate the best word to try first if none is provided in .env
                # ex: firstword="alien"
                if word is None:
                    word = self.trie.find_nextBest_word() # get first word to try

            # Try inpputing word in the game and get feedback
            print(f"Trying word: {word}")
            green, yellow, grey = self.try_word(word, i+1) 

            # Prune the trie with the first word
            self.trie.prune(green, yellow, grey) 
            
            # Check if the game is over
            if len(green) == 5:
                print("🧠 SOLVER WINS THIS TIME! ")
                break

            # print( green, yellow, grey )
            word = self.trie.find_nextBest_word() # get next best word to try

        else:
            print("😭 solver lost this time...")
        


        input("Press Enter to close the browser...")
        self.driver.quit()
    
    def try_word(self, word, row):
        """
        Tries a word in the game and return feedback from the game: green, yellow, grey letters and positions
        """
        # Find the body element and send keystrokes in word
        body = self.driver.find_element(By.TAG_NAME, "body")

        # Send word
        time.sleep(1)
        body.send_keys(word)
        body.send_keys(Keys.RETURN) 
        time.sleep(3)  # wait for key animations

        # Get state of each letter
        row_div = self.driver.find_elements(By.CSS_SELECTOR, f'div[aria-label="Row {row}"]')
        
        green = []
        yellow = []
        grey = set()

        if row_div:
            letter_divs = row_div[0].find_elements(By.CSS_SELECTOR, 'div[class="Tile-module_tile__UWEHN"]')

            # Iterate over each letter div to get its state
            for i, letter_div in enumerate(letter_divs):
                data_state = letter_div.get_attribute("data-state") # correct, present, absent
                
                # print(f"Letter {word[i]} data-state: {data_state}")
                
                if data_state == "correct":
                    print("🟩", end="")
                    green.append((word[i], i))  # letter and position

                elif data_state == "present":
                    yellow.append((word[i], i))
                    print("🟨", end="")

                elif data_state == "absent":
                    grey.add(word[i])
                    print("⬛️", end="")

                else:
                    print(f"\nUnknown state for letter {word[i]}: {data_state}")
        else:
            print("Couldn't find row div", f'div[aria-label="Row {row}"]')
            
        print("")
        return green, yellow, grey


