import os
import ast
import datetime

class Solve:
    root_dir = "solves"
    def __init__(self, dir_name, file_name):
        self.dir_name = dir_name
        self.file_name = file_name
        self.num_attempts = 0
        self.success = None
        # print(f"Reading solve file: {dir_name}/{file_name}")
        self.date = self.getDate(dir_name, file_name)
        self.correct_word = None
        self.gueses = []
        self.num_possible_words_by_attempt = []
        self.correct_letters_by_attempt = []
        self.absent_letters_by_attempt = []
        self.present_letters_by_attempt = []
        self.readSolveFile(dir_name, file_name)


    def readSolveFile(self, dir_name, file_name):
        f = open(f"{self.root_dir}/{dir_name}/{file_name}", 'r')
        # print(f"{self.root_dir}/{dir_name}/{file_name}")
        lines = f.readlines()
        f.close()
        # print(len(lines))
        for i in range(0, len(lines), 4):
            try:
                possible_words, attempt, letter_stat, attempt_stat = lines[i: i+4]
                possible_words = ast.literal_eval(possible_words.strip())
                attempt = ast.literal_eval(attempt.strip())
                letter_stat = ast.literal_eval(letter_stat.strip())
                attempt_stat = ast.literal_eval(attempt_stat.strip())
                self.num_possible_words_by_attempt.append(len(possible_words))
                self.num_attempts += 1
                self.gueses.append(attempt[1])
                if isinstance(attempt_stat, dict):
                    self.correct_letters_by_attempt.append(attempt_stat['correct'].items())
                    self.present_letters_by_attempt.append(attempt_stat['present'].items())
                    self.absent_letters_by_attempt.append(attempt_stat['absent'].items())
            except Exception as e:
                print(f"Error parsing lines {i} to {i+4} in file {file_name}: {e}")
                self.success = False
                return
        if lines[-1].strip().__contains__("SOLVED"):
            self.success = True
        else:
            self.success = False
    
    def getDate(self, dir_name, file_name):
        date = datetime.datetime.strptime('_'.join(file_name.split('_')[:-1]), '%d_%b_%Y').date()
        # print(f"Date: {date}")
        return date

    def print(self):
        print(f"Solve file: {self.dir_name}/{self.file_name}")
        print(f"Date: {self.date}")
        print(f"Number of attempts: {self.num_attempts}")
        print(f"Success: {self.success}")
        print(f"Guesses: {self.gueses}")
        print(f"Num possible words by attempt: {self.num_possible_words_by_attempt}")
        print(f"Correct letters by attempt: {self.correct_letters_by_attempt}")
        print(f"Absent letters by attempt: {self.absent_letters_by_attempt}")
        print(f"Present letters by attempt: {self.present_letters_by_attempt}")




                     
        

def load_attempts(dir_name):
    attempts = os.listdir(f"solves/{dir_name}")
    return attempts
        

# print(os.listdir("solves/"))
dir_names = [name for name in os.listdir("solves/") if os.path.isdir(os.path.join("solves/", name))]
avg_num_attempts_by_month = {}
num_attempts_by_month = []

for dir_name in dir_names:
    # print(load_attempts(dir_name))
    
    number_of_solves_by_attempts_if_successful = {}

    

    attempts = load_attempts(dir_name)
    num_attempts_total = 0
    solves = [Solve(dir_name, fname) for fname in attempts]
    not_solved = 0
    solved = 0
    # add to dict number of attempts by day if successful
    for solve in solves:
        if solve.success:
            number_of_solves_by_attempts_if_successful[solve.num_attempts] = number_of_solves_by_attempts_if_successful[solve.num_attempts] + 1 if solve.num_attempts in number_of_solves_by_attempts_if_successful.keys() else 1
            solved += 1
            num_attempts_total += solve.num_attempts
        else:
            not_solved += 1
    avg_num_attempts_by_month.update({dir_name: [num_attempts_total/(solved if solved > 0 else 0), solved]})
    num_attempts_by_month.append(solved)
    print(f"Directory: {dir_name}")
    print(f"\tNumber of solved: {solved}")
    print(f"\t\tNumber of not solved: {not_solved}")

    import matplotlib.pyplot as plt
    plt.bar(
    number_of_solves_by_attempts_if_successful.keys(),    # x-axis: keys
    number_of_solves_by_attempts_if_successful.values(),  # y-axis: values
    width=0.8, align='center', color='skyblue', edgecolor='black')

    for x, y in number_of_solves_by_attempts_if_successful.items():
        plt.text(x, y + 0.1, str(y), ha='center', va='bottom')

    plt.xticks(range(1, 8))  # ensure ticks are 1..7, even if some bars are missing
    plt.xlabel("Attempts")
    plt.ylabel("Number of solves")
    plt.title("Number of solves by attempts for {dir_name}".format(dir_name=dir_name))
    plt.savefig(f'solves/{dir_name}_attempts_histogram.png')
    plt.close()
    
# plot number of attempts by month
months = list(avg_num_attempts_by_month.keys())
averages = [v[0] for v in avg_num_attempts_by_month.values()]
successful_solves = [v[1] for v in avg_num_attempts_by_month.values()]

fig, ax1 = plt.subplots(figsize=(8, 5))

bars1 = ax1.bar(months, averages, color='skyblue', label='Avg Attempts')
ax1.set_xlabel('Month')
ax1.set_ylabel('Average Number of Attempts', color='skyblue')
ax1.tick_params(axis='y', labelcolor='skyblue')
ax1.set_title('Average Attempts and Successful Solves by Month')
plt.xticks(rotation=30)

# Annotate average attempts
for bar, avg in zip(bars1, averages):
    ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f'{avg:.2f}', ha='center', va='bottom', color='skyblue')

# Secondary axis for successful solves
ax2 = ax1.twinx()
bars2 = ax2.bar(months, successful_solves, color='lightgreen', alpha=0.5, label='Successful Solves')
ax2.set_ylabel('Number of Successful Solves', color='green')
ax2.tick_params(axis='y', labelcolor='green')

# Annotate successful solves
for bar, num in zip(bars2, successful_solves):
    ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f'{num}', ha='center', va='bottom', color='green')

fig.tight_layout()
plt.savefig('attempts_and_successful_solves_by_month.png')
plt.close()