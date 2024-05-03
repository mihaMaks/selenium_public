"""Use this as a boilerplate for your test framework.
Define customized library methods in a class like this.
Then have your test classes inherit it.
BaseTestCase inherits SeleniumBase methods from BaseCase."""
from seleniumbase import BaseCase
import datetime


class MyTests(BaseCase):

    def get_words(self, file):
        l = []
        f = open(file, 'r')
        for line in f:
            l.append(line.strip())
        return l

    def mprint(self, s):
        file_name = datetime.datetime.now().strftime('%d_%b_%Y')
        f = open(file_name, 'a')
        f.write(s.__repr__())
        f.write('\n')
        f.close()

    def write(self, word):
        for letter in word:
            key = 'button[data-key="%s"]' % letter
            self.click(key)
        self.click('[aria-label="enter"]')
        self.sleep(5)

    def get_letter(self, letters_evaluated, state):
        l = []
        for item, i in zip(letters_evaluated.items(), range(6)):
            if item[1] == state:
                l.append((item[0], i))
        return l

    def word_possible(self, word, pass_requirements):
        for letter_and_positions in pass_requirements['absent'].items():
            letter = letter_and_positions[0]
            if word.__contains__(letter):
                return False

        for letter_and_positions in pass_requirements['correct'].items():
            letter = letter_and_positions[0]
            position = letter_and_positions[1][0]
            if not word[position] == letter:
                return False

        for letter_and_positions in pass_requirements['present'].items():
            letter = letter_and_positions[0]
            positions = letter_and_positions[1]
            for ix in positions:
                if word[ix] == letter:
                    return False

        return True

    def solved(self, pass_requirements):
        if len(pass_requirements['correct']) == 5:
            return True
        return False

    def evaluate_letters(self, word, attempt):
        row = '[aria-label="Row %s"] [aria-roledescription="tile"]' % str(attempt)
        letters_evaluated = {}
        for letter, tile in zip(word, self.find_elements(row)):
            letters_evaluated.update({letter: tile.get_attribute('data-state')})
        return letters_evaluated

    def evaluate(self, possible_words, attempt, word, pass_requirements):
        new_words = []
        for word in possible_words:
            if self.word_possible(word, pass_requirements):
                new_words.append(word)

        return new_words

    def add_requirements(self, pass_requirements, letters_evaluated):
        for letter_and_position in self.get_letter(letters_evaluated, 'absent'):
            letter = letter_and_position[0]
            position = letter_and_position[1]
            if not letter in pass_requirements['absent']:
                pass_requirements['absent'].update({letter: position})

        for letter_and_position in self.get_letter(letters_evaluated, 'correct'):
            letter = letter_and_position[0]
            position = letter_and_position[1]
            if letter in pass_requirements['correct']:
                if letter in pass_requirements['present']:
                    pass_requirements['present'].pop(letter)
            else:
                pass_requirements['correct'].update({letter: [position]})

        for letter_and_position in self.get_letter(letters_evaluated, 'present'):
            letter = letter_and_position[0]
            position = letter_and_position[1]
            if letter in pass_requirements['present']:
                l = pass_requirements['present'][letter]
                l.append(position)
                pass_requirements['present'].update({letter: l})
            else:
                pass_requirements['present'].update({letter: [position]})


    def solve(self, possible_words, word):
        pass_requirements = {'correct': {}, 'present': {}, 'absent': {}}
        for attempt in range(1, 7):
            self.write(word)
            self.mprint((attempt, word))
            letters_evaluated = self.evaluate_letters(word, attempt)
            self.mprint(letters_evaluated)
            self.add_requirements(pass_requirements, letters_evaluated)
            self.mprint(pass_requirements)
            if self.solved(pass_requirements):
                return f'SOLVED IN {attempt} ATTEMPTS!'
            possible_words = self.evaluate(possible_words, attempt, word, pass_requirements)
            i = 0
            while word == possible_words[i]:
                i+=1

            word = possible_words[i]
            self.mprint(possible_words)

        return "NOT SOLVED!"

    def test_solve_wordle(self):
        self.open('https://www.nytimes.com/games/wordle/index.html')
        self.click('button[data-testid="Play"]')
        self.click('svg[data-testid="icon-close"]')
        possible_words = self.get_words('wordle_words_list')
        answer = self.solve(possible_words, 'crane')
        self.mprint(answer)
        file_name = datetime.datetime.now().strftime('%d_%b_%Y')

