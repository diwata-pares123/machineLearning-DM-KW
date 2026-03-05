import pandas as pd
import random
import os

# Create the data directory if it doesn't exist
os.makedirs("../data", exist_ok=True)

# Our 16 Skincare Items
ITEMS = [
    "Gentle Cleanser", "Foaming Cleanser", "Exfoliating Toner", "Hydrating Toner",
    "Vitamin C Serum", "Niacinamide Serum", "Hyaluronic Acid Serum", "Lightweight Moisturizer",
    "Heavy Ceramide Cream", "Mineral Sunscreen SPF 50", "Chemical Sunscreen SPF 50", 
    "Snail Mucin Essence", "Pimple Patches", "Clay Mask", "Sheet Mask", "Lip Sleeping Mask"
]

def generate_transactions(num_transactions, season):
    transactions = []
    
    for i in range(1, num_transactions + 1):
        basket = []
        
        # 1. Base Routine (Everyone buys a cleanser and moisturizer)
        basket.append(random.choice(["Gentle Cleanser", "Foaming Cleanser"]))
        
        # 2. Inject Seasonal Trends (The "Self-Learning" triggers)
        if season == "Summer":
            # Summer Bundle: Vitamin C + Sunscreen + Light Moisturizer
            if random.random() > 0.4:  # 60% chance
                basket.extend(["Vitamin C Serum", "Mineral Sunscreen SPF 50", "Lightweight Moisturizer"])
            # Occasional breakout
            if random.random() > 0.7:
                basket.append("Pimple Patches")
                
        elif season == "Winter":
            # Winter Bundle: Hydration + Heavy Cream + Lip Mask
            if random.random() > 0.4:  # 60% chance
                basket.extend(["Hyaluronic Acid Serum", "Heavy Ceramide Cream", "Lip Sleeping Mask"])
            # Extra hydration
            if random.random() > 0.7:
                basket.append("Sheet Mask")
                
        elif season == "Transition":
            # A messy mix of both as seasons change
            if random.random() > 0.6:
                basket.extend(["Vitamin C Serum", "Lightweight Moisturizer"])
            if random.random() > 0.6:
                basket.extend(["Hyaluronic Acid Serum", "Heavy Ceramide Cream"])

        # 3. Add random impulse buys to create noise
        num_random_items = random.randint(0, 3)
        basket.extend(random.choices(ITEMS, k=num_random_items))
        
        # Remove duplicates in the same basket, then format for CSV
        basket = list(set(basket))
        for item in basket:
            transactions.append({"Transaction_ID": f"{season[:3]}_{i:04d}", "Item": item})
            
    return pd.DataFrame(transactions)

# Generate the 3 datasets (1,500 transactions each)
print("Generating Summer Data...")
df_summer = generate_transactions(1500, "Summer")
df_summer.to_csv("../data/dataset_A_summer.csv", index=False)

print("Generating Transition Data...")
df_transition = generate_transactions(1500, "Transition")
df_transition.to_csv("../data/dataset_B_transition.csv", index=False)

print("Generating Winter Data...")
df_winter = generate_transactions(1500, "Winter")
df_winter.to_csv("../data/dataset_C_winter.csv", index=False)

print("✅ Success! All datasets created in the /data/ folder.")