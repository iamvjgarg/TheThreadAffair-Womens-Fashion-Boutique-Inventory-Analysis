
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load datasets
products = pd.read_csv("Products.csv")
opening_inventory = pd.read_csv("Opening_Inventory.csv")
purchases = pd.read_csv("Purchases.csv")
sales = pd.read_csv("Sales.csv")

# Check dataset sizes
print("Products:", products.shape)
print("Opening Inventory:", opening_inventory.shape)
print("Purchases:", purchases.shape)
print("Sales:", sales.shape)


print("\nPRODUCTS")
print(products.head())

print("\nOPENING INVENTORY")
print(opening_inventory.head())

print("\nPURCHASES")
print(purchases.head())

print("\nSALES")
print(sales.head())


# Check missing values
print("\nMissing Values")

for name, df in {
    "Products": products,
    "Opening Inventory": opening_inventory,
    "Purchases": purchases,
    "Sales": sales
}.items():

    print(f"\n{name}")
    print(df.isnull().sum())

# Check duplicate records
print("\nDuplicate Records")

print("Products:", products.duplicated().sum())
print("Opening Inventory:", opening_inventory.duplicated().sum())
print("Purchases:", purchases.duplicated().sum())
print("Sales:", sales.duplicated().sum())


# 1. Total Units Purchased
total_purchased = purchases["Quantity_Purchased"].sum()

# 2. Total Units Sold
total_sold = sales["Quantity_Sold"].sum()

# 3. Total Opening Stock
total_opening_stock = opening_inventory["Opening_Stock_Quantity"].sum()

# 4. Current Stock
current_stock = (
    total_opening_stock
    + total_purchased
    - total_sold
)

# 5. Current Inventory Value
# Calculate stock separately for each product

inventory = products[
    ["Product_ID", "Product_Name", "Category", "Cost_Price_INR"]
].copy()

inventory = inventory.merge(
    opening_inventory,
    on="Product_ID",
    how="left"
)

purchase_summary = purchases.groupby("Product_ID")[
    "Quantity_Purchased"
].sum().reset_index()

sales_summary = sales.groupby("Product_ID")[
    "Quantity_Sold"
].sum().reset_index()

inventory = inventory.merge(
    purchase_summary,
    on="Product_ID",
    how="left"
)

inventory = inventory.merge(
    sales_summary,
    on="Product_ID",
    how="left"
)

# Replace missing quantities with zero
quantity_columns = [
    "Opening_Stock_Quantity",
    "Quantity_Purchased",
    "Quantity_Sold"
]

inventory[quantity_columns] = (
    inventory[quantity_columns].fillna(0)
)

# Calculate current stock per product
inventory["Current_Stock"] = (
    inventory["Opening_Stock_Quantity"]
    + inventory["Quantity_Purchased"]
    - inventory["Quantity_Sold"]
)

# Calculate inventory value at cost price
inventory["Current_Inventory_Value_INR"] = (
    inventory["Current_Stock"]
    * inventory["Cost_Price_INR"]
)

total_inventory_value = inventory[
    "Current_Inventory_Value_INR"
].sum()

# Display KPIs
print("\nSTYLEHER INVENTORY PERFORMANCE")

print("Total Units Purchased:", total_purchased)
print("Total Units Sold:", total_sold)
print("Total Opening Stock:", total_opening_stock)
print("Current Stock:", current_stock)

print(
    "Current Inventory Value (INR):",
    round(total_inventory_value, 2)
)

print("\nPRODUCT-WISE INVENTORY")

print(
    inventory[
        [
            "Product_ID",
            "Product_Name",
            "Category",
            "Current_Stock",
            "Current_Inventory_Value_INR"
        ]
    ].sort_values(
        by="Current_Stock",
        ascending=False
    ).to_string(index=False)
)

# Calculate product-wise sales
product_sales = sales.groupby("Product_ID").agg(
    Total_Units_Sold=("Quantity_Sold", "sum"),
    Total_Revenue_INR=("Total_Revenue_INR", "sum")
).reset_index()

# Join with product details
best_selling = product_sales.merge(
    products[["Product_ID", "Product_Name", "Category"]],
    on="Product_ID",
    how="left"
)

# Sort and select top 5
top_5_products = best_selling.sort_values(
    by="Total_Units_Sold",
    ascending=False
).head(5)

print("\nTOP 5 BEST-SELLING PRODUCTS")
print(top_5_products.to_string(index=False))


# Start with all products
least_selling = products[
    ["Product_ID", "Product_Name", "Category"]
].merge(
    product_sales,
    on="Product_ID",
    how="left"
)

# Replace missing sales with zero
least_selling[
    ["Total_Units_Sold", "Total_Revenue_INR"]
] = least_selling[
    ["Total_Units_Sold", "Total_Revenue_INR"]
].fillna(0)

# Sort in ascending order
least_5_products = least_selling.sort_values(
    by="Total_Units_Sold",
    ascending=True
).head(5)

print("\nTOP 5 LEAST-SELLING PRODUCTS")
print(least_5_products.to_string(index=False))


# Merge sales with product categories
category_sales = sales.merge(
    products[["Product_ID", "Category"]],
    on="Product_ID",
    how="left"
)

# Calculate category performance
category_performance = category_sales.groupby(
    "Category"
).agg(
    Total_Units_Sold=("Quantity_Sold", "sum"),
    Total_Revenue_INR=("Total_Revenue_INR", "sum"),
    Average_Discount_Percentage=("Discount_Percentage", "mean")
).reset_index()

category_performance[
    "Average_Discount_Percentage"
] = category_performance[
    "Average_Discount_Percentage"
].round(2)

# Sort by revenue
category_performance = category_performance.sort_values(
    by="Total_Revenue_INR",
    ascending=False
)

print("\nCATEGORY-WISE SALES PERFORMANCE")
print(category_performance.to_string(index=False))


# Create product-wise purchase summary
purchase_summary = purchases.groupby("Product_ID").agg(
    Total_Units_Purchased=("Quantity_Purchased", "sum")
).reset_index()

# Create product-wise sales summary
sales_summary = sales.groupby("Product_ID").agg(
    Total_Units_Sold=("Quantity_Sold", "sum")
).reset_index()

# Merge product, purchase and sales data
overstock = products[
    ["Product_ID", "Product_Name", "Category", "Cost_Price_INR"]
].merge(
    opening_inventory,
    on="Product_ID",
    how="left"
).merge(
    purchase_summary,
    on="Product_ID",
    how="left"
).merge(
    sales_summary,
    on="Product_ID",
    how="left"
)

# Replace missing quantities with zero
quantity_columns = [
    "Opening_Stock_Quantity",
    "Total_Units_Purchased",
    "Total_Units_Sold"
]

overstock[quantity_columns] = (
    overstock[quantity_columns].fillna(0)
)

# Calculate current stock
overstock["Current_Stock"] = (
    overstock["Opening_Stock_Quantity"]
    + overstock["Total_Units_Purchased"]
    - overstock["Total_Units_Sold"]
)

# Calculate inventory value
overstock["Current_Inventory_Value_INR"] = (
    overstock["Current_Stock"]
    * overstock["Cost_Price_INR"]
)

# Calculate purchase sell-through percentage
overstock["Purchase_Sell_Through_Percentage"] = np.where(
    overstock["Total_Units_Purchased"] > 0,
    (
        overstock["Total_Units_Sold"]
        / overstock["Total_Units_Purchased"]
    ) * 100,
    np.nan
)

overstock["Purchase_Sell_Through_Percentage"] = (
    overstock["Purchase_Sell_Through_Percentage"].round(2)
)

# Display products with remaining stock
potential_overstock = overstock[
    overstock["Current_Stock"] > 0
].sort_values(
    by="Current_Stock",
    ascending=False
)

print("\nPOTENTIAL OVERSTOCK ANALYSIS")

print(
    potential_overstock[
        [
            "Product_ID",
            "Product_Name",
            "Category",
            "Total_Units_Purchased",
            "Total_Units_Sold",
            "Current_Stock",
            "Current_Inventory_Value_INR",
            "Purchase_Sell_Through_Percentage"
        ]
    ].to_string(index=False)
)


low_sell_through = overstock[
    (overstock["Total_Units_Purchased"] > 0)
    & (overstock["Purchase_Sell_Through_Percentage"] < 30)
].sort_values(
    by="Purchase_Sell_Through_Percentage",
    ascending=True
)

print("\nPRODUCTS WITH LOW PURCHASE SELL-THROUGH")

print(
    low_sell_through[
        [
            "Product_Name",
            "Category",
            "Total_Units_Purchased",
            "Total_Units_Sold",
            "Current_Stock",
            "Purchase_Sell_Through_Percentage"
        ]
    ].to_string(index=False)
)

# 1. Check for negative stock
negative_stock = inventory[
    inventory["Current_Stock"] < 0
]

print("\nNEGATIVE STOCK CHECK")
print("Products with negative stock:", len(negative_stock))

if len(negative_stock) > 0:
    print(negative_stock[
        ["Product_ID", "Product_Name", "Current_Stock"]
    ].to_string(index=False))
else:
    print("No negative stock found.")


# 2. Check for duplicate Product IDs
print("\nDUPLICATE PRODUCT ID CHECK")

print(
    "Duplicate Product IDs:",
    products["Product_ID"].duplicated().sum()
)


# 3. Check for unmatched Product IDs
print("\nUNMATCHED PRODUCT ID CHECK")

product_ids = set(products["Product_ID"])

print(
    "Unmatched purchase Product IDs:",
    len(set(purchases["Product_ID"]) - product_ids)
)

print(
    "Unmatched sales Product IDs:",
    len(set(sales["Product_ID"]) - product_ids)
)

print(
    "Unmatched opening inventory Product IDs:",
    len(set(opening_inventory["Product_ID"]) - product_ids)
)
