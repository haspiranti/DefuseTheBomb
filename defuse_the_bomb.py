import typing
import random
import time
from threading import Thread
from threading import Event

class Countdown(Thread):

    StopEvent = 0

    def __init__(self, args):
        Thread.__init__(self)
        self.StopEvent = args

    def run(self):
        global cd_timer
        while cd_timer > 0:
            time.sleep(1)
            cd_timer -= 1
            if(self.StopEvent.wait(0)):
                break
            

def choose_difficulty():
    easy = 4
    medium = 5
    hard = 6
    while True:
        diff = input("Please choose a difficulty:\n[Easy, Medium, Hard]\n>> ")
        if diff.upper() == "EASY" or diff.upper() == "E":
            print("Easy mode selected")
            return easy
        elif diff.upper() == "MEDIUM" or diff.upper() == "M" or diff.upper() == "MED":
            print("Medium mode selected")
            return medium
        elif diff.upper() == "HARD" or diff.upper() == "H":
            print("Hard mode selected")
            return hard
        else:
            print("Invalid difficulty")

def validate(guess: str, codelen: int) -> typing.Tuple[str, str]:
    """
    Validate a guess from a user.

    Return a tuple of [None if no error or a string containing
    the error message, the guess].
    """
    if len(guess) != codelen:
        return f"Guess must be of length {codelen}", guess
    
    if guess.isdigit() == False: 
        return "Guess must be a valid number", guess
    return None, guess


def get_user_guess(codelen: int) -> str:
    """Get a user's guess input, validate, and return the guess."""

    # continue looping until you get a valid guess
    while cd_timer > 0:
        guess = input("Guess: ")
        # here we overwrite guess with
        # the filtered guess
        error, guess = validate(guess=guess, codelen=codelen)
        
        if error is None:
            break

        print(error)
    return guess


def find_all_num_positions(code: str, num: str) -> typing.List[int]:
    """Given a word and a character, find all the indices of that character."""
    positions = []
    pos = code.find(num)
    while pos != -1:
        positions.append(pos)
        pos = code.find(num, pos + 1)
    return positions


def compare(expected: str, guess: str) -> typing.List[str]:
    """Compare the guess with the expected code and return the output parse."""
    # the output is assumed to be incorrect to start,
    # and as we progress through the checking, update
    # each position in our output list
    output = ["⬛"] * len(expected)
    counted_pos = set()

    # first we check for expected numbers in the correct positions
    # and update the output accordingly
    for index, (expected_num, guess_num) in enumerate(zip(expected, guess)):
        if expected_num == guess_num:
            # a correct number in the correct position
            output[index] = "🟩"
            counted_pos.add(index)
    
    # now we check for the remaining numbers that are in incorrect
    # positions. in this case, we need to make sure that if the
    # number that this is correct for was already
    # counted as a correct number, we do NOT display
    # this in the double case. e.g. if the correct code
    # is "12335" but we guess "16781", the second "1"
    # should display "_" and not "-", since the "1" where
    # it belongs was already displayed correctly
    # likewise, if the guess word has two numbers in incorrect
    # places, only the first number is displayed as a "-".
    # e.g. if the guess is "12344" but the game word is "46789"
    # then the output should be "_ _ _ - _"; the second "4" in "12344"
    # is not displayed.    
    for index, guess_num in enumerate(guess):
        # if the guessed number is in the correct code,
        # we need to check the other conditions. the easiest
        # one is that if we have not already guessed that
        # number in the correct place. if we have, don't
        # double-count
        if guess_num in expected and output[index] != "🟩":
            # first, what are all the positions the guessed
            # number is present in        
            positions = find_all_num_positions(code=expected, num=guess_num)
            # have we accounted for all the positions
            for pos in positions:
                # if we have not accounted for the correct
                # position of this number yet
                if pos not in counted_pos:
                    output[index] = "🟨"
                    counted_pos.add(pos)
                    # we only count the "correct number" once,
                    # so we break out of the "for pos in positions" loop
                    break  
    # return the list of parses
    return output


if __name__ == "__main__":

    # countdown timer. how many seconds the game lasts.
    cd_timer = 60
    
    # the game code is X digits
    CODELEN = choose_difficulty()
    
    # bottom and top range of digits
    BOTTOM_RANGE, TOP_RANGE = (int("0" * CODELEN), int("9" * CODELEN))

    # select a random code to start with
    CODE = (f"{random.randint(BOTTOM_RANGE, TOP_RANGE):0{CODELEN}d}")

    # display the starting point
    print("_ " * CODELEN)

    # define the countdown timer
    Stop = Event()
    Countdown = Countdown(Stop)

    try:
        # start the countdown timer
        Countdown.start()
        while cd_timer > 0:
            # get the user to guess something
            GUESS = get_user_guess(CODELEN)
            # display the guess when compared against the game code
            result = compare(expected=CODE, guess=GUESS)
            print(" ".join(result))
            
            if CODE == GUESS:
                print("You defused the bomb!")
                break
            elif cd_timer < 1:
                print(f"Time's up! the code was {CODE}")
                break

        # stop the countdown thread
        Stop.set()
        exit
    except KeyboardInterrupt:
        print("You gave up and the bomb exploded.")