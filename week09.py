import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

titanic = sns.load_dataset('titanic')
print(titanic.query('age > = 70'))

sns.scatterplot(x='age', y = 'fare', data = titanic)
plt.plot
plt.show()