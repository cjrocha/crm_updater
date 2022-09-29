import json, pandas as pd
from libs import db_connection

def invoice_parser(invoice_data):
    """_summary_
        This is the parser of invoices data from unleashed API
    
    It handles the invoice data and invoice lines separately,
    loads all data from API into 2 matrix: invoice and invoice_lines
    Connects to db and using pandas library handles each matrix.
    
    Args: invoice_data: (matrix) the matrix of invoices received from 
                           unleashed API
    Returns: nothing to console, but injects new data into DB unls_data
             on tables: invoices and invoice_lines
    """
# With small changes can work with csv files also. See comments bellow.    
    if invoice_data:
        invoice_lines = []
        invoices = []

        for data in invoice_data:
            
            if data['Customer']:
                for k,v in data['Customer'].items():
                    data[f'Customer.{k}'] = v
                data.pop('Customer')
            else:
                data.pop('Customer')

            if data['DeliveryAddress']:
                for k,v in data['DeliveryAddress'].items():
                    data[f'DeliveryAddress.{k}'] = v
                data.pop('DeliveryAddress')
            else:
                data.pop('DeliveryAddress')

            if data['InvoiceLines']:
                invoice_guid = data['Guid']
                for iline in data['InvoiceLines']:
                    if iline['Product']:
                        for k,v in iline['Product'].items():
                            iline[f'Product.{k}'] = v
                        iline.pop('Product')
                    else:
                        iline.pop('Product')
                    
                    iline['ParentID'] = invoice_guid
                    invoice_lines.append(iline)

                data['InvoiceLines'] = invoice_guid

            invoices.append(data)

        if invoices:
            pre_cursor = db_connection.db_connector() #Connection to db
            query = 'select * from invoices'
            dfi = pd.DataFrame(invoices)
            # Remove columns not needed as index base: 7,15,16,19,35 or column name
            dfi_clean = dfi.drop(columns=['PostalAddress', 'CreatedBy', 'PaymentTerm', 'LastModifiedOn', 'DeliveryAddress.DeliveryInstruction'])
            dfi_clean = dfi_clean.fillna(0)        #Cleaning data like NaN nan, etc... all these are set as 0
            try:
                dfi1 = pd.read_sql(query, con = pre_cursor)  #pd.read_csv(f'data/Invoices.csv')- if using csv generator
                dfi2 = dfi_clean
                dfi_new = pd.concat([dfi1, dfi2], ignore_index=True)
            except:
                dfi_new = dfi_clean
            #removing duplicates
            db_final = pd.read_sql(query, con = pre_cursor)
            dfi_final = pd.concat([db_final, dfi_new], ignore_index=True)
            df_inv_final = dfi_final.drop_duplicates(subset=['Guid'],keep=False)
            
            #df_inv_final.to_csv(f'data/Invoices.csv', index=False, mode='w', header=True) - uploading to Invoices csv
            
            # creating column list for insertion
            cols = "`,`".join([str(i) for i in df_inv_final.columns.tolist()])
            # Insert DataFrame records one by one.
            for i,row in df_inv_final.iterrows():
                sql = "INSERT INTO `invoices` (`" +cols + "`) VALUES (" + "%s,"*(len(row)-1) + "%s)"
                pre_cursor.execute(sql, tuple(row))
            
            pre_cursor.close() #Closing db connection

        if invoice_lines:
            pre_cursor = db_connection.db_connector() #Connection to db
            query = 'select * from invoice_lines'
            dfil = pd.DataFrame(invoice_lines)
            # Remove columns not needed as index base: 11,12,14 or column name
            dfil_clean = dfil.drop(columns=['SerialNumbers', 'BatchNumbers', 'LastModifiedOn'])
            dfil_clean = dfil_clean.fillna(0) #Cleaning data like NaN nan, etc... all these are set as 0
            try:
                dfil1 = pd.read_sql(query, con = pre_cursor)#pd.read_csv(f'data/InvoiceLines.csv')- if using csv generator
                dfil2 = dfil_clean
                dfil_new = pd.concat([dfil1, dfil2], ignore_index=True)
            except:
                dfil_new = dfil_clean
            
            dfil = dfil_new.drop_duplicates(subset=['Guid'],keep='last')
            #removing duplicates
            db_final = pd.read_sql(query, con = pre_cursor)
            dfil_final = pd.concat([db_final, dfil_new], ignore_index=True)
            df_invl_final = dfil_final.drop_duplicates(subset=['Guid'],keep=False)
            
            #df_invl_final.to_csv(f'data/InvoiceLines.csv', index=False, mode='w', header=True) - uploading to invoice_lines csv
            
            # creating column list for insertion
            cols = "`,`".join([str(i) for i in df_invl_final.columns.tolist()])
            # Insert DataFrame records one by one.
            for i,row in df_invl_final.iterrows():
                sql = "INSERT INTO `invoice_lines` (`" +cols + "`) VALUES (" + "%s,"*(len(row)-1) + "%s)"
                pre_cursor.execute(sql, tuple(row))
            
            pre_cursor.close() #Closing db connection