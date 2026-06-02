# %% [markdown]
# # NeoStats Retail Data Engineering Pipeline
# 
# ## End-to-End Workflow
# 
# Excel Source Files
# ↓
# Data Ingestion
# (Retail Dataset 1, Retail Dataset 2, Product Dimension Table)
# 
# ↓
# Data Quality Checks
# - Schema validation
# - Missing value detection
# - Duplicate record checks
# 
# ↓
# Data Cleaning & Transformation
# - Missing price handling
# - Invalid record removal
# - Category standardization
# - Product name standardization
# - PII masking
# 
# ↓
# Curated Dataset Creation
# - Product dimension merge
# - Revenue KPI calculation
# 
# ↓
# Aggregation-Ready Analytics Layer
# - Total Revenue
# - Revenue by Category
# - Revenue by City
# - Additional KPIs
# 
# ↓
# Final Dataset Validation
# 
# ↓
# Export Curated Dataset
# (cleaned_retail_dataset.csv)
# 
# ↓
# Power BI Dashboard Source

# %%
# Import pandas library for data handling and analysis
import pandas as pd

# Import os library for file path operations
import os

# Verify notebook environment is working
print("NeoStats VS Code Ready")

# %%
# Define Excel file location

file = r"G:\Haveloc\USECASE  neostats - Data Engineering.xlsx"

# Display file path to verify
print(file)

# %%
# Load Retail Dataset 1
# header=2 means row 3 contains column names

retail1 = pd.read_excel(
    file,
    sheet_name='RETAIL DATA 1',
    header=2
)
# Load Retail Dataset 2
# header=4 means row 5 contains column names

retail2 = pd.read_excel(
    file,
    sheet_name='RETAIL DATA 2',
    header=4
)

# %%
# Display first 5 rows of Retail Dataset 1

display(retail1.head())

# Display first 5 rows of Retail Dataset 2

display(retail2.head())

# %%
# Load standardized product dimension table
# header=2 means row 3 contains column names

product = pd.read_excel(
    file,
    sheet_name='PRODUCT DETAILS',
    header=3
)

# Display first few rows

display(product.head())

# Verify product columns

print(product.columns)

# %%
# Check column names for all datasets

print("Retail1 Columns")
print(retail1.columns)

print("\nRetail2 Columns")
print(retail2.columns)

print("\nProduct Columns")
print(product.columns)

# %%
# Combine both retail transaction datasets

retail = pd.concat(
    [retail1, retail2],
    ignore_index=True
)

# Display dataset dimensions
print("Combined Dataset Shape:")
print(retail.shape)

# %%
# Display first 5 rows of combined dataset

display(
    retail.head()
)

# %%
# Display dataset structure

retail.info()

# %%
# Check missing values in every column

missing_values = retail.isnull().sum()

# Display missing value count

print(missing_values)

# %%
# Count duplicate rows

duplicates = retail.duplicated().sum()

# Display duplicate count

print(
    "Duplicate Records:",
    duplicates
)

# %%
# Display column names

print(
    retail.columns
)

# %%
# Display column names from both retail datasets

print("Retail1 Columns:")
print(retail1.columns)

print("\nRetail2 Columns:")
print(retail2.columns)

# %%
# Fill missing prices using average price of the same product

retail['price'] = retail.groupby(
    'product_id'
)['price'].transform(
    lambda x: x.fillna(
        x.mean()
    )
)

# Verify missing values after cleaning

print(
    retail.isnull().sum()
)

# %%
print(
    "Negative Prices:",
    (retail['price'] < 0).sum()
)

print(
    "Invalid Quantity:",
    (retail['quantity'] <= 0).sum()
)

# %%
# Remove invalid records

retail = retail[
    (retail['price'] >= 0)
    &
    (retail['quantity'] > 0)
]

# Verify cleaned dataset size

print(
    "Cleaned Dataset Shape:",
    retail.shape
)

# %%
# Recheck invalid records after cleaning

print(
    "Negative Prices:",
    (retail['price'] < 0).sum()
)

print(
    "Invalid Quantity:",
    (retail['quantity'] <= 0).sum()
)


# %%
# Standardize category values
# Replace inconsistent category labels

retail['category'] = retail[
    'category'
].replace({

    'ELEC':'Electronics',

    'electronics':'Electronics',

    'FURN':'Furniture',

    'furniture':'Furniture',

    'home appliances':'Home Appliances',

    'HOME':'Home Appliances',

    'CLOTH':'Clothing',

    'clothing':'Clothing'

})

# Verify cleaned categories

print(
    retail['category'].unique()
)

# %%
# Standardize product names
# Convert inconsistent capitalization into consistent format

retail['product_name'] = retail[
    'product_name'
].str.title()

# Verify cleaned product names

print(
    retail['product_name'].unique()
)

# %%
# Merge retail dataset with product dimension table
# Join using product_id

curated_dataset = retail.merge(

    product,

    on='product_id',

    how='left',

    suffixes=(
        '_retail',
        '_product'
    )

)

# Preview merged dataset

display(
    curated_dataset.head()
)

# %%
# Calculate revenue KPI
# Revenue = Price × Quantity × (1 − Discount)

curated_dataset['revenue'] = (

    curated_dataset['price_retail']

    *

    curated_dataset['quantity']

    *

    (
        1 -
        curated_dataset['discount']
    )

)

# Preview revenue calculation

display(

    curated_dataset[
        [
            'product_name_retail',
            'price_retail',
            'quantity',
            'discount',
            'revenue'
        ]
    ].head()

)

# %%
# Display final curated dataset structure

curated_dataset.info()

# Check missing values in final dataset

print(
    curated_dataset.isnull().sum()
)

# %%
# Export curated dataset for Power BI

curated_dataset.to_csv(

    r"G:\Haveloc\cleaned_retail_dataset.csv",

    index=False

)

print(
    "Curated dataset exported successfully."
)

# %%
# Mask customer email addresses
# Example:
# Troy60@gmail.com → T***@gmail.com

curated_dataset['email'] = curated_dataset[
    'email'
].str.replace(

    r'(^.).*(@.*$)',

    r'\1***\2',

    regex=True

)

# Verify masked emails

display(

    curated_dataset[
        ['email']
    ].head()

)

# %%
# Mask phone numbers
# Example:
# 8385276968 → ******6968

curated_dataset['phone'] = curated_dataset[
    'phone'
].astype(str).str.replace(

    r'\d(?=\d{4})',

    '*',

    regex=True

)

# Verify masked phone numbers

display(

    curated_dataset[
        ['phone']
    ].head()

)

# %%
# Export final privacy-protected dataset

curated_dataset.to_csv(

    r"G:\Haveloc\cleaned_retail_dataset.csv",

    index=False

)

print(
    "PII-masked curated dataset exported successfully."
)

# %%
# Calculate Total Revenue KPI

total_revenue = curated_dataset[
    'revenue'
].sum()

# Display KPI

print(
    "Total Revenue:",
    total_revenue
)

# %%
# Calculate Revenue by Category

revenue_by_category = curated_dataset.groupby(

    'category_retail'

)[
    'revenue'
].sum().sort_values(
    ascending=False
)

# Display result

print(
    revenue_by_category
)

# %%
# Calculate Revenue by City

revenue_by_city = curated_dataset.groupby(

    'city'

)[
    'revenue'
].sum().sort_values(
    ascending=False
)

# Display result

print(
    revenue_by_city
)

# %%
# Calculate total transaction count

total_orders = curated_dataset[
    'transaction_id'
].nunique()

print(
    "Total Orders:",
    total_orders
)

# %%
# Calculate average revenue per transaction

average_revenue = curated_dataset[
    'revenue'
].mean()

print(
    "Average Revenue:",
    average_revenue
)

# %%
# Revenue by payment method

revenue_by_payment = curated_dataset.groupby(

    'payment_method'

)[
    'revenue'
].sum().sort_values(
    ascending=False
)

print(
    revenue_by_payment
)

# %%
# Final curated dataset validation

print(
    curated_dataset.shape
)

print(
    curated_dataset.isnull().sum()
)

display(
    curated_dataset.head()
)

# %%
# Export final curated dataset

curated_dataset.to_csv(

    r"G:\Haveloc\cleaned_retail_dataset.csv",

    index=False

)

print(
    "Final curated dataset exported successfully."
)


