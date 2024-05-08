def get_words(file):
    l = []
    f = open(file, 'r')
    for line in f:
        l.append(line.strip())
    return l


def score(word, distribution):
    score = 0
    s = set()
    for lt in word:
        s.add(lt)
    for lt in s:
        score += distribution[lt]
    return score

vowels = ['a', 'e', 'i', 'o', 'u']
alphabet = 'abcdefghijklmnopqrstuvwxyz'
all_words = get_words('wordlist_fives.txt')
distribution = {}
for lt in alphabet:
    distribution.update({lt: 0})
for word in all_words:
    for lt in word:
        distribution[lt] = distribution[lt] + 1
print(distribution)
popularity = []
for item in distribution.items():
    popularity.append((item[0], item[1]))

popularity.sort(key=lambda x: -x[1])
print(popularity)
best_words = []
for word in all_words:
    best_words.append((word, score(word, distribution)))

best_words.sort(key=lambda x: -x[1])
print(best_words)

import pickle as pkl

f = open("letter_scores.pkl", 'wb')
pkl.dump(distribution, f)
f.close()