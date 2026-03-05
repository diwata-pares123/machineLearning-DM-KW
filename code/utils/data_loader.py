import pandas as pd

def load_and_encode(file_path):
    """Loads a CSV and converts it to a one-hot encoded format."""
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        return None

    # Assuming our CSV has 'Transaction_ID' and 'Item' columns
    # We group them and unstack to create a wide matrix
    basket = (df.groupby(['Transaction_ID', 'Item'])['Item']
              .count().unstack().reset_index().fillna(0)
              .set_index('Transaction_ID'))
    
    # Convert all numbers > 0 to 1, and keep 0s as 0
    encoded_basket = (basket > 0).astype(int)
    
    return encoded_basket