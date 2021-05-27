import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

sns.set()
#distro = [[3,2,12,4,7,5,10],
#[2,10,0,0,6,0,0],
#[2,2,12,5,4,11,10],
#[9,9,51,27,36,35,48],
#[6,23,20,10,27,15,17],
#[18,16,96,40,55,65,78],
#[14,25,68,31,69,53,64]]
distro = [[8, 13, 14, 22, 21, 0, 15],
[5, 12, 11, 18, 30, 3, 16],
[8, 12, 12, 25, 26, 0, 15],
[2, 4, 7, 13, 18, 0, 7],
[6, 8, 10, 31, 35, 0, 12],
[4, 13, 12, 36, 41, 5, 17],
[3, 25, 16, 46, 50, 0, 34]]
distro.reverse()
ax = sns.heatmap(distro, cmap='Blues', annot=True)
#labels = ['GLOB', 'S PORT', 'HW', 'M OUT', 'S SIG', 'M INT', 'MEM']
labels = ['out', 'int', 'mem', 'ins', 'dec', 'dbg', 'msm']
ax.set_xticklabels(labels)
labels.reverse()  
ax.set_yticklabels(labels)  
plt.xlabel("Source Group")
plt.ylabel("Sink Group")
plt.yticks(rotation=45)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('heat.png')
