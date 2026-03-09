import pandas as pd

def load_and_encode(file_path):
    """Loads a CSV, preprocesses it, and converts it to a one-hot encoded format."""
    try:
        df = pd.read_csv(file_path, names=["Transaction_ID", "Item"])
    except FileNotFoundError:
        return None

    if df.empty:
        return None

    # --- 🧹 LAYER 1 PREPROCESSING: DATA SANITIZATION ---
    # 1. Convert to string and strip invisible trailing spaces
    df['Item'] = df['Item'].astype(str).str.strip()
    
    # 2. Drop any rows that are completely empty or NaN
    df = df[df['Item'] != '']
    df = df.dropna(subset=['Item', 'Transaction_ID'])
    
    # 3. Deduplication (Crucial for MBA)
    # If a customer bought 3 mice in one order, we compress it to 1 instance of 'Mouse'
    df = df.drop_duplicates(subset=['Transaction_ID', 'Item'])

    # Group them and unstack to create a wide matrix
    basket = (df.groupby(['Transaction_ID', 'Item'])['Item']
              .count().unstack().reset_index().fillna(0)
              .set_index('Transaction_ID'))
    
    # Convert all numbers > 0 to 1, and keep 0s as 0
    encoded_basket = (basket > 0).astype(int)
    
    return encoded_basket