import input_translate
from sys import argv

if len(argv) > 0:
    test = argv[0]
else:
    test = "3"

for char in test:
    input_translate.enqueue_morse_of_char(char.upper())

# while True:
#     input_translate.sleep(0.01)