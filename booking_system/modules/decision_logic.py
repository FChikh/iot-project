import pandas as pd
import numpy as np

def topsis_decision_logic(room_data, user_pref, weights=None, lower_better_cols=[]):
    """
    Perform TOPSIS (Technique for Order Preference by Similarity to Ideal Solution)
    to rank rooms based on user preferences.

    Parameters:
        room_data (pd.DataFrame): DataFrame containing attributes of each room.
        user_pref (dict): Dictionary of user preferences for each attribute.
        weights (list or None): List of weights for each attribute. If None, all attributes are equally weighted.
        lower_better_cols (list): List of columns where lower values are better.

    Returns:
        pd.DataFrame: DataFrame with closeness coefficients and ranks for each room.
    """

    adjusted_df = pd.DataFrame(index=room_data.index)
    for col in room_data.columns:
        if col in lower_better_cols:
            adjusted_df[col] = 1 / (1 + abs(room_data[col] - user_pref[col]))
        else:
            adjusted_df[col] = 1 / (1 + abs(room_data[col] - user_pref[col]))


    norm = np.sqrt((adjusted_df**2).sum())
    normalized = adjusted_df / norm

    if weights is None:
        weights = np.ones(len(room_data.columns))
    weights = np.array(weights) / np.sum(weights)
    weighted = normalized * weights


    pis = weighted.max()
    nis = weighted.min()

    dist_pis = np.sqrt(((weighted - pis)**2).sum(axis=1))
    dist_nis = np.sqrt(((weighted - nis)**2).sum(axis=1))


    closeness = dist_nis / (dist_pis + dist_nis)


    result = room_data.copy()
    result['Closeness Coefficient'] = closeness
    result['Rank'] = closeness.rank(ascending=False)
    
    return result.sort_values('Rank')