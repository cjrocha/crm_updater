import json, pandas as pd
from libs import db_connection

def products_parser(products_data):
    """
    _summary_
    This is the parser of products data from unleashed API
    
    It loads all data from API into a products matrix
    Connects to db and using pandas library handles the products matrix.
    
    Args: products_data: (matrix) the matrix of products received from 
                           unleashed API
    Returns: nothing to console, but injects new data into DB unls_data
             on table products                       
    
    """
# With small changes can work with csv files also. See comments bellow.    
    if products_data:
        
        products = []
        for index,data in enumerate(products_data,start=1):
            data['productId'] = index
            products.append(data)

        if products:
            pre_cursor = db_connection.db_connector() #Connection to db
            query = 'select * from products'
            df = pd.DataFrame(products)
            # Remove columns not needed as index base: 2-12 and 18-31 and 34-39 and 41-64 or column name
            df_clean = df.drop(columns=['Barcode', 'PackSize', 'Width', 'Height', 'Depth', 'Weight', 'MinStockAlertLevel', 'MaxStockAlertLevel', 
                                            'ReOrderPoint', 'UnitOfMeasure', 'NeverDiminishing', 'Obsolete', 'Notes', 'Images', 'ImageUrl', 'SellPriceTier1',
                                            'SellPriceTier2', 'SellPriceTier3', 'SellPriceTier4', 'SellPriceTier5', 'SellPriceTier6', 'SellPriceTier7',
                                            'SellPriceTier8', 'SellPriceTier9', 'SellPriceTier10', 'TaxablePurchase', 'TaxableSales', 'XeroSalesTaxCode',
                                            'XeroSalesTaxRate', 'IsComponent', 'IsAssembledProduct', 'XeroSalesAccount', 'XeroCostOfGoodsAccount', 'PurchaseAccount',
                                            'BinLocation', 'Supplier', 'AttributeSet', 'SourceId', 'SourceVariantParentId', 'IsSerialized', 'IsBatchTracked',
                                            'IsSellable', 'MinimumSellPrice', 'MinimumSaleQuantity', 'MinimumOrderQuantity', 'CreatedBy', 'CreatedOn',
                                            'LastModifiedBy', 'CommerceCode', 'CustomsDescription', 'SupplementaryClassificationAbbreviation', 'ICCCountryCode',
                                            'ICCCountryName', 'InventoryDetails', 'AlternateUnitsOfMeasure'])
            #ProdGroup is a json field, so we read it as Json and remove the un-wanted fields, keeping just the GroupName values.
            new = pd.json_normalize(df_clean['ProductGroup'])
            df_clean['ProductGroup'] = new['GroupName']
            df_clean = df_clean.fillna(0) #Cleaning data like NaN nan, etc... all these are set as 0
            
            try:
                df_prods1 = pd.read_sql(query, con = pre_cursor) #pd.read_csv(f'data/Products.csv')- if using csv generator
                df_prods2 = df_clean
                df_prods_new = pd.concat([df_prods1, df_prods2], ignore_index=True)
            except:
                df_prods_new = df_clean
            #removing duplicates    
            db_final = pd.read_sql(query, con = pre_cursor)
            df_final = pd.concat([db_final, df_prods_new], ignore_index=True)
            df_prods_final = df_final.drop_duplicates(subset=['Guid'],keep=False)
            
            #df_prods_final.to_csv(f'data/Products.csv', index=False, mode='w', header=True) - uploading to Products csv
            
            # creating column list for insertion
            cols = "`,`".join([str(i) for i in df_prods_final.columns.tolist()])
            # Insert DataFrame records one by one.
            for i,row in df_prods_final.iterrows():
                sql = "INSERT INTO `products` (`" +cols + "`) VALUES (" + "%s,"*(len(row)-1) + "%s)"
                pre_cursor.execute(sql, tuple(row))
            
            pre_cursor.close() #Closing db connection