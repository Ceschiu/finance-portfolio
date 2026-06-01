import numpy as np
import pandas as pd
from statsmodels.regression.linear_model import RegressionResultsWrapper

def compute_contribution(result: RegressionResultsWrapper, ff: pd.DataFrame) -> pd.DataFrame:
    """Costruisce un DataFrame in cui vengono schematizzate le informazioni principali del modello OLS passato"""

    df = pd.DataFrame(index=result.params.index, columns=["Beta", "Factor Mean Return", "Abs Contribution", "Perc Contribution"]) # Costruisco il df

    for fattore in result.params.index:
        df.loc[fattore,"Beta"] = result.params[fattore] # Popolo la colonna dei Beta
        if fattore == "const": # alpha non ha FMR quindi tratto diversamente
            df.loc[fattore,"Abs Contribution"] = df.loc[fattore,"Beta"]*100 # Popolo la colonna delle contribution
            df.loc[fattore,"Perc Contribution"] = df.loc[fattore,"Abs Contribution"]/(result.fittedvalues.mean()*100) # Popolo la colonna delle contribution percentuali
        else:
            df.loc[fattore,"Factor Mean Return"] = ff[fattore].mean()*100 # Popolo la colonna dei FMR
            df.loc[fattore,"Abs Contribution"] = df.loc[fattore,"Beta"]* df.loc[fattore,"Factor Mean Return"] # Popolo la colonna delle contribution assolute
            df.loc[fattore,"Perc Contribution"] = df.loc[fattore,"Abs Contribution"]/(result.fittedvalues.mean()*100) # Popolo la colonna delle contribution percentuali

    return df