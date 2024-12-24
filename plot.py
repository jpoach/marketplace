import os
import pandas as pd
import matplotlib.pyplot as plt

def plot_generic(
        df=pd.read_csv(os.path.join('docs', 'listings.csv'), index_col=0),
        savepath=os.path.join('docs', 'generic_hist.png')
    ):

    df.price.hist()

    plt.axvline(df.price.mean(), color='black', linestyle='--', label=f'mean=${df.price.mean():.0f}')

    plt.xlabel('Price')
    plt.legend()

    plt.savefig(savepath)
