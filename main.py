from dotenv import load_dotenv
import os


from WordleSolver import WordleSolver

load_dotenv() # load env variables
solver = WordleSolver( os.getenv("DRIVER_PATH") , os.getenv("WORD_PATH") ) # create driver using DRIVER_PATH constant


solver.play_game() # play game




