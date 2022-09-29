import json, pandas as pd
from libs import db_connection

def currency_parser(currencies_data):
    """_summary_
    This is the parser of currencies used with unleashed API
    
    It loads all data from API into a currencies matrix
    Connects to db and using pandas library handles the currencies matrix.
    
    Args: currencies_data: (matrix) the matrix of currencies received from 
                           unleashed API
    Returns: nothing to console, but injects new data into DB unls_data
             on table currencies                       
    """
# With small changes can work with csv files also. See comments bellow.      
    if currencies_data:
        
        currencies = []
        for index,data in enumerate(currencies_data,start=1):
            data['CurrencyId'] = index
            currencies.append(data)

        if currencies:
            pre_cursor = db_connection.db_connector() #connection to db
            query = 'select * from currencies'
            try:
                df_curr1 = pd.read_sql(query, con = pre_cursor)  #pd.read_csv(f'data/Currencies.csv') - if using csv generator
                df_curr2 = pd.DataFrame(currencies)
                df_curr_new = pd.concat([df_curr1, df_curr2], ignore_index=True)
            except:
                df_curr_new = pd.DataFrame(currencies)
            #removing duplicates
            df_curr = df_curr_new.drop_duplicates(subset=['Guid'],keep=False)

            #df_curr.to_csv(f'data/Currencies.csv', index=False, mode='w', header=True) - uploading to Curencies csv
            
            # creating column list for db insertion
            cols = "`,`".join([str(i) for i in df_curr.columns.tolist()])
            # Insert DataFrame records one by one into currencies table.
            for i,row in df_curr.iterrows():
                sql = "INSERT INTO `currencies` (`" +cols + "`) VALUES (" + "%s,"*(len(row)-1) + "%s)"
                pre_cursor.execute(sql, tuple(row))
                
            #Closing connection to db           
            pre_cursor.close()