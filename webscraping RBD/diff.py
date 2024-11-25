import pandas as pd

# Read RBDs from rbd.csv
rbd_df = pd.read_csv('c:/Users/Rodrigo/Desktop/Roxana Files/webscraping RBD/rbd.csv')
rbd_list = rbd_df['RBD'].tolist()

# Read RBDs from resultados.csv
resultados_df = pd.read_csv('c:/Users/Rodrigo/Desktop/Roxana Files/webscraping RBD/resultados.csv')
resultados_list = resultados_df['RBD'].tolist()

# Find RBDs that are in rbd.csv but not in resultados.csv
missing_rbds = [rbd for rbd in rbd_list if rbd not in resultados_list]

# Write missing RBDs to a new CSV file
missing_rbds_df = pd.DataFrame(missing_rbds, columns=['RBD'])
missing_rbds_df.to_csv('c:/Users/Rodrigo/Desktop/Roxana Files/webscraping RBD/missing_rbds.csv', index=False)
