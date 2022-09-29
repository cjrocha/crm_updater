import json, pandas as pd
from libs import db_connection

def customer_parser(customers_data):
    """_summary_
        This is the parser of customers data from unleashed API
    
    It handles the customers data and customers registered addresses separately,
    loads all data from API into 2 matrix: customers and addresses
    Connects to db and using pandas library handles each matrix.
    
    Args: customers_data: (matrix) the matrix of customers received from 
                           unleashed API
    Returns: nothing to console, but injects new data into DB unls_data
             on tables: customers and addresses
    """
# With small changes can work with csv files also. See comments bellow.      
    if customers_data:
        
        addresses = []
        customers = []

        for data in customers_data:
            
            if data['Addresses']:
                for addr in data['Addresses']:
                    addr['ParentID'] = data['Guid']
                    addresses.append(addr)
                data['Addresses'] = data['Guid']
            else:
                data['Addresses'] = None
                      
            if data['Currency']:
                for k,v in data['Currency'].items():
                    data[f'Currency.{k}'] = v
                data.pop('Currency')
            else:
                data.pop('Currency')

            customers.append(data)

        if customers:
            pre_cursor = db_connection.db_connector() #Connection to db
            query = 'select * from customers'
            dfc = pd.DataFrame(customers)
            # Remove columns not needed as index base: 1,21,23,24,28,29,30,35,36,37,38,42,44 or column name
            dfc_clean = dfc.drop(columns=['Contacts', 'SalesPerson', 'PrintPackingSlipInsteadOfInvoice', 'PrintInvoice', 'XeroCostOfGoodsAccount', 'SellPriceTier',
                                              'SellPriceTierReference', 'SourceId', 'CreatedBy', 'CreatedOn', 'LastModifiedBy', 'Currency.Description',
                                              'Currency.LastModifiedOn'])
            dfc_clean = dfc_clean.fillna(0) #Cleaning data like NaN nan, etc... all these are set as 0
            try:
                dfc1 = pd.read_sql(query, con = pre_cursor)   #pd.read_csv(f'data/Customers.csv')- if using csv generator
                dfc2 = dfc_clean
                dfc_new = pd.concat([dfc1, dfc2], ignore_index=True)
            except:
                dfc_new = dfc_clean
                
            #removing duplicates
            db_final = pd.read_sql(query, con = pre_cursor)
            dfc_final = pd.concat([db_final, dfc_new], ignore_index=True)
            dfc_cust_final = dfc_final.drop_duplicates(subset=['Guid','CustomerCode'], keep=False)    
            
            #dfc_cust_final.to_csv(f'data/Customers.csv', index=False, mode='w', header=True) - uploading to customers csv
            
            # creating column list for insertion
            cols = "`,`".join([str(i) for i in dfc_cust_final.columns.tolist()])
            # Insert DataFrame records one by one.
            for i,row in dfc_cust_final.iterrows():
                sql = "INSERT INTO `customers` (`" +cols + "`) VALUES (" + "%s,"*(len(row)-1) + "%s)"
                pre_cursor.execute(sql, tuple(row))
            
            pre_cursor.close() #Closing db connection


        if addresses:
            pre_cursor = db_connection.db_connector() #connection to db
            query = 'select * from addresses'
            try:
                dfa1 = pd.read_sql(query, con = pre_cursor)  #pd.read_csv(f'data/Addresses.csv')- if using csv generator
                dfa2 = pd.DataFrame(addresses).fillna(0)
                dfa_new = pd.concat([dfa1, dfa2], ignore_index=True)
            except:
                dfa_new = pd.DataFrame(addresses).fillna(0)

            #removing duplicates
            db_final = pd.read_sql(query, con = pre_cursor)
            dfa_final = pd.concat([db_final, dfa_new], ignore_index=True)
            dfa = dfa_final.drop_duplicates(subset=['AddressType', 'AddressName', 'PostalCode', 'IsDefault', 'ParentID'], keep=False)
            
            #dfa.to_csv(f'data/Addresses.csv', index=False, mode='w', header=True) - uploading to Addresses csv
            
            # creating column list for insertion
            cols = "`,`".join([str(i) for i in dfa.columns.tolist()])
            # Insert DataFrame records one by one.
            for i,row in dfa.iterrows():
                sql = "INSERT INTO `addresses` (`" +cols + "`) VALUES (" + "%s,"*(len(row)-1) + "%s)"
                pre_cursor.execute(sql, tuple(row))
            
            pre_cursor.close() #Closing db connection