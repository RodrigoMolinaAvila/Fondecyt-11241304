import pandas as pd

# List of CSV files to convert
csv_files = [
#    r'C:\Users\Rodrigo\Desktop\Roxana Files\webscraping RBD\resultados+dep1.csv',
    r'C:\Users\Rodrigo\Desktop\Roxana Files\webscraping RBD\resultados.csv'
]

# Convert each CSV file to XLSX
for csv_file in csv_files:
    # Read the CSV file
    df = pd.read_csv(csv_file)
    
    # Define the XLSX file path
    xlsx_file = csv_file.replace('.csv', '.xlsx')
    
    # Write the DataFrame to an XLSX file
    df.to_excel(xlsx_file, index=False)

print("Conversion completed.")