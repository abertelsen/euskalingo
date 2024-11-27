import os 
import sys

sys.path.insert(1, os.path.join(os.path.dirname(__file__), "..", "src"))
import hitzon.utils as hut

target = "<bederatzi>, lau, hiru"
print(hut.to_blankfill(target=target))
print(hut.to_canon(target=target))
print(hut.to_blankfill(target=target))
print(hut.to_list(target=target))

target = "{t:Donostian} autobus geltoki <bat> dago {t}"
print(hut.to_canon(target=target))