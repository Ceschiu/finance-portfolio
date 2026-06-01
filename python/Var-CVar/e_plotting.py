import pandas as pd
import os
import matplotlib.pyplot as plt


def plot_var(w: pd.Series, rend:pd.DataFrame, var_param:float, es_param:float, var_hist:float, es_hist:float, var_mc:float, es_mc:float, alpha:float):
    fig, ax = plt.subplots()
    rend_ptf = rend@w

    ax.hist(rend_ptf, bins = 100, color="Black", label="ptf_returns")

    ax.axvline(x=-var_param, color="red", linestyle="-", label="VaR Param")
    ax.axvline(x=-es_param, color="red", linestyle=":", label="ES Param")
    ax.axvline(x=-var_hist, color="orange", linestyle="-", label="VaR Hist")
    ax.axvline(x=-es_hist, color="orange", linestyle=":", label="ES Hist")
    ax.axvline(x=-var_mc, color="blue", linestyle="-", label="VaR MC")
    ax.axvline(x=-es_mc, color="blue", linestyle=":", label="ES MC")

    plt.legend()
    plt.title(f"VaR & ES al {alpha:.0%}")
    base = os.path.dirname(__file__)
    path = os.path.join(base, "VaR_ES.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")

    return