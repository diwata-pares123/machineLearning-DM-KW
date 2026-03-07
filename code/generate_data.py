import pandas as pd
import random
import os

# Create the data directory if it doesn't exist
os.makedirs("../data", exist_ok=True)

# Our 16 Gaming E-commerce Items (Meets the >= 15 unique items rule)
ITEMS = [
    "PlayStation 5 Console", "DualSense Wireless Controller", "Spider-Man 2 (PS5)", 
    "Nintendo Switch OLED", "Zelda: Tears of the Kingdom", "Switch Pro Controller",
    "Xbox Series X Console", "Halo Infinite (Xbox)", "Xbox Wireless Controller",
    "Mechanical Gaming Keyboard", "Wireless Gaming Mouse", "XL RGB Mousepad",
    "27-inch 144Hz Gaming Monitor", "Noise-Cancelling Gaming Headset", 
    "1TB NVMe SSD", "Ergonomic Gaming Chair"
]

def generate_transactions(num_transactions, phase):
    transactions = []
    
    for i in range(1, num_transactions + 1):
        basket = []
        
        # 1. Base Logic (General Gamers)
        # People usually buy a console or a PC peripheral as a base item
        base_choice = random.choice(["Console Gamer", "PC Gamer"])
        
        if base_choice == "Console Gamer":
            # Pick a random console
            basket.append(random.choice(["PlayStation 5 Console", "Nintendo Switch OLED", "Xbox Series X Console"]))
        else:
            # PC gamers usually start with a mouse or keyboard
            basket.append(random.choice(["Mechanical Gaming Keyboard", "Wireless Gaming Mouse"]))

        # 2. Inject Data Drift / Seasonal Trends (This triggers the AI's Self-Learning)
        if phase == "Regular":
            # Standard organic purchases
            if "PlayStation 5 Console" in basket and random.random() > 0.5:
                basket.append("Spider-Man 2 (PS5)")
            if "Mechanical Gaming Keyboard" in basket and random.random() > 0.4:
                basket.append("Wireless Gaming Mouse")

        elif phase == "Holiday":
            # HUGE SHIFT: The "PS5 Holiday Bundle" trend takes over
            if random.random() > 0.3:  # 70% chance to buy this bundle
                basket.extend(["PlayStation 5 Console", "DualSense Wireless Controller", "Spider-Man 2 (PS5)"])
            # Switch families buying gifts
            if random.random() > 0.6:
                basket.extend(["Nintendo Switch OLED", "Zelda: Tears of the Kingdom", "Switch Pro Controller"])
                
        elif phase == "Esports":
            # ANOTHER SHIFT: Holiday is over, competitive PC gaming season starts
            if random.random() > 0.3: # 70% chance for a PC setup upgrade
                basket.extend(["Mechanical Gaming Keyboard", "Wireless Gaming Mouse", "XL RGB Mousepad", "27-inch 144Hz Gaming Monitor"])
            if random.random() > 0.5:
                basket.append("Noise-Cancelling Gaming Headset")

        # 3. Add random impulse buys to create realistic data noise
        num_random_items = random.randint(0, 2)
        basket.extend(random.choices(ITEMS, k=num_random_items))
        
        # Remove duplicates in the same basket, then format for CSV
        basket = list(set(basket))
        for item in basket:
            transactions.append({"Transaction_ID": f"{phase[:3]}_{i:04d}", "Item": item})
            
    return pd.DataFrame(transactions)

# Generate the 3 datasets (1,500 transactions each - easily passing the 1,000 req)
print("Generating Iteration 1: Regular Season Data...")
df_regular = generate_transactions(1500, "Regular")
df_regular.to_csv("../data/dataset_A_regular.csv", index=False)

print("Generating Iteration 2: Holiday Rush Data...")
df_holiday = generate_transactions(1500, "Holiday")
df_holiday.to_csv("../data/dataset_B_holiday.csv", index=False)

print("Generating Iteration 3: Esports Season Data...")
df_esports = generate_transactions(1500, "Esports")
df_esports.to_csv("../data/dataset_C_esports.csv", index=False)

print("✅ Success! All DataBlitz-style datasets created in the /data/ folder.")