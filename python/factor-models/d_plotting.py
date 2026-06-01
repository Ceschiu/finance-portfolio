import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
from statsmodels.regression.linear_model import RegressionResultsWrapper

def plot_factor_analysis(capm_result: RegressionResultsWrapper, ff3_result: RegressionResultsWrapper, ff5_result: RegressionResultsWrapper, capm_attr: pd.DataFrame, ff3_attr: pd.DataFrame, ff5_attr: pd.DataFrame, color_list: list=["steelblue", "orange", "green"], model_selected: str = "ff5"):
    """Costruisce i plot: confronto R2 dei modelli, Beta dei fattori di un modello specifico, confronto contribution assoluta dei fattori per un modello specifico, confronto alpha dei modelli"""

    fig, axes = plt.subplots(1,4, figsize=(18, 5))
    
    if model_selected == "ff5": graph1, graph2, color_single = ff5_result, ff5_attr, color_list[2]
    elif model_selected == "ff3": graph1, graph2, color_single = ff3_result, ff3_attr, color_list[1]
    else: graph1, graph2, color_single = capm_result, capm_attr, color_list[0]

    axes[0].bar(["CAPM","FF3","FF5"], [capm_result.rsquared, ff3_result.rsquared, ff5_result.rsquared], color = color_list) # R2 comparison
    axes[0].set_title("R2 comparison between models")

    betas = graph1.params.drop("const") # Beta comparison per il modello selezionato
    axes[1].barh(betas.index, betas, color = color_single) 
    axes[1].axvline(x=0, color='black', linewidth=0.5)
    axes[1].set_title(f"Betas comparison for {model_selected}")

    axes[2].bar(graph2.index, graph2["Abs Contribution"], color = color_single) # contribution assolute di ogni fattore per il modello selezionato
    axes[2].set_title(f"Return absolute contribution for {model_selected}")

    axes[3].bar(["CAPM","FF3","FF5"], [capm_attr.loc["const","Abs Contribution"], ff3_attr.loc["const","Abs Contribution"], ff5_attr.loc["const","Abs Contribution"]], color = color_list) # valore degli alpha di ciascun modello
    axes[3].set_title(f"Alpha contribution for each model")

    base = os.path.dirname(__file__) # Salvo plot
    path = os.path.join(base, "Factor_Analysis.png")
    plt.tight_layout(pad=2.0)
    plt.savefig(path, dpi=150, bbox_inches="tight")

    return