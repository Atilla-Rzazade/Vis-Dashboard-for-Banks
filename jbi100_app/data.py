import plotly.express as px
import pandas as pd
import numpy as np

def get_data():
    # Read data
    df = pd.read_csv('Dataset/all_data.csv', sep=';', low_memory=False)

    selected_columns = [
        "Customer_ID", # tick
        "Month", # tick
        "Age", # tick
        "Occupation", # tick
        "Annual_Income", 
        "Num_Bank_Accounts",# tick
        "Num_of_Loan", # tick
        "Type_of_Loan", # tick
        "Num_of_Delayed_Payment", # tick
        "Outstanding_Debt", # tick
        "Credit_Utilization_Ratio", # tick
    ]

    df_selected = df[selected_columns]

    empty_row_representation = ['_______', '_', '!@9#%8', '#F%$D@*&8', '__10000__']

    numerical_columns = ['Age', 'Annual_Income', 'Num_Bank_Accounts', 'Num_of_Loan', 'Num_of_Delayed_Payment', 'Outstanding_Debt', 'Credit_Utilization_Ratio']

    for column in numerical_columns:
        df_selected.loc[:, column] = df_selected[column].apply(lambda x: str(x).replace('_', ''))
        df_selected.loc[:, column] = df_selected[column].apply(lambda x: str(x).replace(',', '.'))

        df[column] = pd.to_numeric(df[column], errors='coerce')

    df_selected.replace(empty_row_representation, np.nan, inplace=True)

    df_selected = clean_data(df_selected, 'Age', 18, 100)
    df_selected = clean_data(df_selected, 'Num_of_Loan', 0, 9)
    df_selected = clean_data(df_selected, 'Num_Bank_Accounts', 0, 11)
    df_selected = clean_data(df_selected, 'Num_of_Delayed_Payment', 0, 28)

    refill_data(df_selected)

    loan_type_count = get_loan_type_count(df_selected)
    ocuppation_income_group = get_occupation_income_group(df_selected)

    income_group_dict = ocuppation_income_group.groupby('Income_Group')['Occupation'].apply(lambda x: list(set(x))).to_dict()

    debt_to_income_ratio = get_debt_to_income_ratio_per_occupation(df_selected)
    delays_per_occupation = get_num_of_delayed_payments_per_occupation(df_selected)

    return (top_left_data(ocuppation_income_group, loan_type_count), 
            top_right_data(df_selected), 
            bottom_left_data(debt_to_income_ratio, ocuppation_income_group), 
            bottom_right_data(df_selected, delays_per_occupation), income_group_dict) 


def clean_data(df, column_name: str, lower_bound: float, upper_bound: float):
    df[column_name] = pd.to_numeric(df[column_name], errors='coerce')
    df[column_name] = np.where((df[column_name] >= upper_bound) | (df[column_name] < lower_bound), np.nan, df[column_name])
    return df

def refill_data(df_selected):
    columns_to_fill = ['Age', 'Occupation']

    # Fill missing values
    for column in columns_to_fill:
        # Update the dictionary with the current state of the DataFrame
        df_selected[column] = df_selected.groupby('Customer_ID')[column].apply(lambda group: group.fillna(method='ffill'))
        df_selected[column] = df_selected.groupby('Customer_ID')[column].apply(lambda group: group.fillna(method='bfill'))

    df_selected['Num_of_Delayed_Payment'] = df_selected.groupby('Customer_ID')['Num_of_Delayed_Payment'].transform(lambda x: x.fillna(round(x.median(), 1)))

    def fill_with_mode(x):
        return x.fillna(x.mode()[0]) if not x.mode().empty else x

    def replace_with_mode(x):
        return x.mode()[0] if not x.mode().empty else x

    df_selected['Num_of_Loan'] = df_selected.groupby('Customer_ID')['Num_of_Loan'].transform(lambda x: x.fillna(fill_with_mode(x)))
    df_selected['Num_Bank_Accounts'] = df_selected.groupby('Customer_ID')['Num_Bank_Accounts'].transform(lambda x: x.fillna(round(x.median(), 1)))
    df_selected['Annual_Income'] = df_selected.groupby('Customer_ID')['Annual_Income'].transform(replace_with_mode)

    def fill_num_of_loan(row):
        if pd.isnull(row['Num_of_Loan']):
            count = row['Type_of_Loan'].count(',')
            return count + 1 if count > 0 else 0
        else:
            return row['Num_of_Loan']

    df_selected['Num_of_Loan'] = df_selected.apply(fill_num_of_loan, axis=1)

    return df_selected


def get_loan_type_count(df_selected):
    # Split the 'Type_of_Loan' column into separate rows
    df_selected = df_selected.assign(Type_of_Loan=df_selected['Type_of_Loan'].str.replace(", and", ",").str.split(',')).explode('Type_of_Loan')

    # Remove leading/trailing whitespaces
    df_selected['Type_of_Loan'] = df_selected['Type_of_Loan'].str.strip()

    # Group by 'Occupation' and 'Type_of_Loan' and count the number of each loan type per occupation
    loan_counts = df_selected.groupby(['Occupation', 'Type_of_Loan']).size().reset_index(name='Loan_Type_Count')

    return loan_counts

def get_occupation_income_group(df_selected):
    # Define income groups based on percentiles
    df_selected['Income_Group'] = pd.qcut(df_selected['Annual_Income'], q=[0, .2, .4 , .6, .8, 1], labels=['20', '40', '60', '80', '100'])

    # Now you can group by occupation and income group
    grouped = df_selected.groupby(['Occupation', 'Income_Group']).size().reset_index(name='Counts')

    ocuppation_income_group = grouped.loc[grouped.groupby('Occupation')['Counts'].idxmax()]

    return ocuppation_income_group

def get_debt_to_income_ratio_per_occupation(df_selected):
    df_selected['Outstanding_Debt'] = df_selected['Outstanding_Debt'].astype(float)

    df_selected['DIO'] = df_selected['Outstanding_Debt']/df_selected['Annual_Income']

    debt_to_income_ratio = df_selected.groupby('Occupation')['DIO'].mean().reset_index(name="DIO")

    debt_to_income_ratio['DIO'] = (debt_to_income_ratio['DIO'] - debt_to_income_ratio['DIO'].min()) / (debt_to_income_ratio['DIO'].max() - debt_to_income_ratio['DIO'].min())

    return debt_to_income_ratio


def get_num_of_delayed_payments_per_occupation(df_selected):
    df_selected['Num_of_Delayed_Payment'] = df_selected['Num_of_Delayed_Payment'].astype(float)

    delays_per_occupation = df_selected.groupby('Occupation')['Num_of_Delayed_Payment'].mean().reset_index(name="Delays")

    delays_per_occupation['Delays'] = 1 + (delays_per_occupation['Delays'] - delays_per_occupation['Delays'].min()) * (10 - 1) / (delays_per_occupation['Delays'].max() - delays_per_occupation['Delays'].min())

    return delays_per_occupation


def top_left_data(ocuppation_income_group, loan_type_count):
    df_merged = pd.merge(loan_type_count, ocuppation_income_group, on='Occupation')

    top_left_data = df_merged[['Type_of_Loan', 'Loan_Type_Count', 'Income_Group']]

    return top_left_data


def top_right_data(df_selected):
    df_selected['Num_of_Delayed_Payment'] = df_selected['Num_of_Delayed_Payment'].astype(float)

    top_right_data = df_selected.groupby(['Month', 'Occupation'])['Num_of_Delayed_Payment'].sum().reset_index(name="Count")

    top_right_data['Count'] = 1 + (top_right_data['Count'] - top_right_data['Count'].min()) * (10 - 1) / (top_right_data['Count'].max() - top_right_data['Count'].min())

    return top_right_data

def bottom_left_data(debt_to_income_ratio, ocuppation_income_group):
    # Map each occupation to its income group
    df_merged = pd.merge(debt_to_income_ratio, ocuppation_income_group, on='Occupation')

    # Create a new dataframe that contains the 'Occupation', 'Debt_to_Income_Ratio', and 'Income_Group' columns
    bottom_left_data = df_merged[['Occupation', 'DIO', 'Income_Group']]

    return bottom_left_data

def bottom_right_data(df_selected, delays_per_occupation):
    df_selected['Credit_Utilization_Ratio'] = df_selected['Credit_Utilization_Ratio'].astype(float)
    df_selected['Num_Bank_Accounts'] = df_selected['Num_Bank_Accounts'].astype(float)

    credit_util_ratio_per_occupation = df_selected.groupby('Occupation')['Credit_Utilization_Ratio'].mean().reset_index(name="Avg_Credit_Util_Ratio")

    bottom_right_data = df_selected[['Num_Bank_Accounts', 'Occupation']]

    bottom_right_data = pd.merge(bottom_right_data, delays_per_occupation, on='Occupation')
    bottom_right_data = pd.merge(bottom_right_data, credit_util_ratio_per_occupation, on='Occupation')

    bottom_right_data = bottom_right_data.groupby('Occupation').mean().reset_index()

    bottom_right_data['Num_Bank_Accounts'] = 1 + (bottom_right_data['Num_Bank_Accounts'] - bottom_right_data['Num_Bank_Accounts'].min()) * (10 - 1) / (bottom_right_data['Num_Bank_Accounts'].max() - bottom_right_data['Num_Bank_Accounts'].min())
    bottom_right_data['Avg_Credit_Util_Ratio'] = 1 + (bottom_right_data['Avg_Credit_Util_Ratio'] - bottom_right_data['Avg_Credit_Util_Ratio'].min()) * (10 - 1) / (bottom_right_data['Avg_Credit_Util_Ratio'].max() - bottom_right_data['Avg_Credit_Util_Ratio'].min())
    
    return bottom_right_data