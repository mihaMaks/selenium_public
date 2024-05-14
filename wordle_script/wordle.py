"""Use this as a boilerplate for your test framework.
Define customized library methods in a class like this.
Then have your test classes inherit it.
BaseTestCase inherits SeleniumBase methods from BaseCase."""
from seleniumbase import BaseCase
import datetime
import pickle as pkl


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

    def get_letter(self, letters_evaluated, state, word):
        l = []
        for item, i in zip(letters_evaluated.items(), range(6)):
            letter = item[0]
            if item[1] == state:
                tl = []
                for i in range(len(word)):
                    if letter == word[i]:
                        tl.append(i)
                l.append((item[0], tl))
        return l

    def word_possible(self, word, pass_requirements):
        for letter_and_positions in pass_requirements['absent'].items():
            letter = letter_and_positions[0]
            if letter in pass_requirements['correct'].items() and letter in pass_requirements['present'].items():
                if word.count(letter) >= 3:
                    return False

            if letter in pass_requirements['correct'].items() or letter in pass_requirements['present'].items():
                if word.count(letter) >= 2:
                    return False
                continue

            if word.__contains__(letter):
                return False

        for letter_and_positions in pass_requirements['correct'].items():
            letter = letter_and_positions[0]
            positions = letter_and_positions[1]
            for ix in positions:
                if not word[ix] == letter:
                    return False

        for letter_and_positions in pass_requirements['present'].items():
            letter = letter_and_positions[0]
            positions = letter_and_positions[1]
            for ix in positions:
                if word[ix] == letter:
                    return False
            if not word.__contains__(letter):
                return False

        return True

    def solved(self, pass_requirements):
        if 'present' not in pass_requirements.values() and 'absent' not in pass_requirements.values():
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

    def add_requirements(self, pass_requirements, letters_evaluated, word):
        for letter_and_position in self.get_letter(letters_evaluated, 'absent', word):
            letter = letter_and_position[0]
            position = letter_and_position[1]
            if letter not in pass_requirements['absent']:
                pass_requirements['absent'].update({letter: position})

        for letter_and_position in self.get_letter(letters_evaluated, 'correct', word):
            letter = letter_and_position[0]
            positions = letter_and_position[1]
            if letter in pass_requirements['correct']:
                if letter in pass_requirements['present']:
                    pass_requirements['present'].pop(letter)
            else:
                pass_requirements['correct'].update({letter: positions})

        for letter_and_position in self.get_letter(letters_evaluated, 'present', word):
            letter = letter_and_position[0]
            positions = letter_and_position[1]
            if letter in pass_requirements['present']:
                l = pass_requirements['present'][letter]
                for pos in positions:
                    if pos not in l:
                        l.append(pos)
                pass_requirements['present'].update({letter: l})
            else:
                pass_requirements['present'].update({letter: positions})

    def score(self, word, distribution):
        score = 0
        s = set()
        for lt in word:
            s.add(lt)
        for lt in s:
            score += distribution[lt]

        return score
    def solve(self, possible_words, word, letter_scores):
        pass_requirements = {'correct': {}, 'present': {}, 'absent': {}}
        attempt = 1
        while attempt < 7:
            self.write(word)
            self.mprint((attempt, word))
            letters_evaluated = self.evaluate_letters(word, attempt)
            if 'tbd' in letters_evaluated.values():
                possible_words.remove(word)
                self.mprint(possible_words)
                b = False
                for w in possible_words:
                    if not w == word:
                        word = w
                        for i in range(5):
                            self.click('[aria-label="backspace"]')
                        b = True
                        break
                if b:
                    continue
            self.mprint(letters_evaluated)
            self.add_requirements(pass_requirements, letters_evaluated, word)
            self.mprint(pass_requirements)
            if self.solved(letters_evaluated):
                return f'SOLVED IN {attempt} ATTEMPTS!'
            possible_words = self.evaluate(possible_words, attempt, word, pass_requirements)
            if len(possible_words) == 0:
                word = 'crane'
                attempt += 1
                continue
            best_words = []
            for wrd in possible_words:
                best_words.append((wrd, self.score(word, letter_scores)))
            best_words.sort(key=lambda x: -x[1])
            self.mprint(possible_words)
            i = 0
            while word == best_words[i][0]:
                i += 1
            word = best_words[i][0]
            attempt += 1

        self.mprint(attempt)
        if attempt == 7:
            self.sleep(5)
            self.click('svg[data-testid="icon-close"]')
            self.sleep(5)
            self.click('svg[data-testid="icon-close"]')
            answr = self.find_element('.Toast-module_toast__iiVsN').text
            return f'NOT SOLVED EMPTY WORD LIST LOOKING FOR WORD: {answr.lower()}'

        return "NOT SOLVED!"

    def test_solve_wordle(self):
        self.open('https://www.nytimes.com/games/wordle/index.html')
        self.click('button[data-testid="Play"]')
        self.click('svg[data-testid="icon-close"]')
        possible_words = self.get_words('wordlist_fives.txt')
        f = open('letter_scores.pkl', 'rb')
        letter_scores = pkl.load(f)
        self.mprint(letter_scores)
        f.close()
        answer = self.solve(possible_words, 'crane', letter_scores)
        self.mprint(answer)

