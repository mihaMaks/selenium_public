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
        file_name = datetime.datetime.now().strftime('%d_%b_%Y') + "_sets"
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
            for stt in item[1].keys():
                if stt == state:
                    l.append((letter, item[1][stt]))
        return l

    def word_possible(self, word, pass_requirements):
        for letter_and_positions in pass_requirements['absent'].items():
            letter = letter_and_positions[0]
            if letter in pass_requirements['correct'].keys() and letter in pass_requirements['present'].keys():
                if word.count(letter) >= 3:
                    return False

            if letter in pass_requirements['correct'].keys() or letter in pass_requirements['present'].keys():
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

        for letter_and_positions in pass_requirements['multiple'].items():
            letter = letter_and_positions[0]
            positions = letter_and_positions[1]
            if word.count(letter) < positions[0]:
                return False
        return True

    def solved(self, letters_evaluated):
        for letter_item in letters_evaluated.values():
            if 'present' in letter_item.keys():
                return False
        for letter_item in letters_evaluated.values():
            if 'absent' in letter_item.keys():
                return False
        return True

    def evaluate_letters(self, word, attempt):
        row = '[aria-label="Row %s"] [aria-roledescription="tile"]' % str(attempt)
        letters_evaluated = {}

        for letter, tile, pos in zip(word, self.find_elements(row), range(5)):
            state = tile.get_attribute('data-state')
            if letter in letters_evaluated:
                if state != 'absent' and 'absent' not in letters_evaluated[letter]:
                    if 'multiple' not in letters_evaluated[letter]:
                        letters_evaluated[letter].update({'multiple': [2]})
                    else:
                        letters_evaluated[letter]['multiple'][0] += 1
                if state in letters_evaluated[letter]:
                    letters_evaluated[letter][state].append(pos)
                else:
                    letters_evaluated[letter].update({state: [pos]})
            else:
                letters_evaluated.update({letter: {state: [pos]}})

        return letters_evaluated

    def evaluate(self, possible_words, pass_requirements):
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
                l = pass_requirements['correct'][letter]
                for pos in positions:
                    if pos not in l:
                        l.append(pos)
                pass_requirements['correct'].update({letter: l})

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

        for letter_and_position in self.get_letter(letters_evaluated, 'multiple', word):
            letter = letter_and_position[0]
            positions = letter_and_position[1]
            pass_requirements['multiple'].update({letter: positions})

    def score(self, word, distribution):
        score = 0
        s = set()
        for lt in word:
            s.add(lt)
        for lt in s:
            score += distribution[lt]

        return score

    def evaluate_words(self, possible_words, letter_scores):
        best_words = []
        for wrd in possible_words:
            best_words.append((wrd, self.score(wrd, letter_scores)))
        best_words.sort(key=lambda x: -x[1])
        return best_words

    def get_letter_scores(self, possible_words):
        alphabet = 'abcdefghijklmnopqrstuvwxyz'
        distribution = {}
        for lt in alphabet:
            distribution.update({lt: 0})
        for word in possible_words:
            for lt in set(l for l in word):
                distribution[lt] = distribution[lt] + 1
        return distribution

    def solve(self, possible_words):
        pass_requirements = {'correct': {}, 'present': {}, 'absent': {}, 'multiple': {}}
        attempt = 1
        while attempt < 7:
            if len(possible_words) == 0:
                word = 'crane'
                self.write(word)
                attempt += 1
                continue
            # GET LETTER FREQUENCY
            letter_scores = self.get_letter_scores(possible_words)

            # EVALUATE WORDS
            best_words = []
            for wrd in possible_words:
                best_words.append((wrd, self.score(wrd, letter_scores)))
            best_words.sort(key=lambda x: -x[1])
            for w, i in zip(best_words, range(len(best_words))):
                best_words[i] = w[0]
            if attempt != 1:
                self.mprint(best_words)

            # TYPE WORD IN BROWSER
            word = best_words[0]
            self.write(word)
            # READ PRESENCE OF LETTERS
            letters_evaluated = self.evaluate_letters(word, attempt)

            self.mprint((attempt, word))
            self.mprint(letters_evaluated)

            # WORD NOT IN DICT
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

            # CHECK IF SOLVED
            if self.solved(letters_evaluated):
                return f'SOLVED IN {attempt} ATTEMPTS!'

            # ALL DATA THAT IS COLLECTED FROM PREVIOUS ATTEMPTS
            self.add_requirements(pass_requirements, letters_evaluated, word)
            self.mprint(pass_requirements)

            # FILTER WORDS THAT ARE POSSIBLE
            possible_words = self.evaluate(possible_words, pass_requirements)
            attempt += 1

        # IF FAILS STILL WANT TO KNOW CORRECT ANSWER
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
        answer = self.solve(possible_words)
        self.mprint(answer)

