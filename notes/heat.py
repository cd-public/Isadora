  
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

sns.set()
distro = [[3,2,12,4,7,5,10],
[2,10,0,0,6,0,0],
[2,2,12,5,4,11,10],
[9,9,51,27,36,35,48],
[6,23,20,10,27,15,17],
[18,16,96,40,55,65,78],
[14,25,68,31,69,53,64]]
distro.reverse()
ax = sns.heatmap(distro, cmap='Blues', annot=True)
labels = ['GLOB', 'S PORT', 'C PORT', 'M PORT', 'CNFG', 'M INT', 'CNTRL']
ax.set_xticklabels(labels)
labels.reverse()  
ax.set_yticklabels(labels)  
plt.xlabel("Source Group")
plt.ylabel("Sink Group")
plt.yticks(rotation=45)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('heat.png')
