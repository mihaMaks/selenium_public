"""Use this as a boilerplate for your test framework.
Define customized library methods in a class like this.
Then have your test classes inherit it.
BaseTestCase inherits SeleniumBase methods from BaseCase."""
from seleniumbase import BaseCase



class MyTests(BaseCase):

    def test_solve_wordle(self):
        self.open('https://www.wordunscrambler.net/word-list/wordle-word-list')
        f = open('wordle_words_list', 'w')
        self.click('.material-icons.fc-close-icon')
        for word in self.find_elements('li.invert.light a[href]', by='css selector'):
            f.write(word.text)
            f.write('\n')
        f.close()
        

