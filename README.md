### Unleashed API Scraper
- Api Credits are stored in scrapper.py
- DB Credits are stored in libs/db_connetcion.py
- Scraping Customers, Invoices & Products data from unleashed API.
- Store the data into:
   a) MariaDB
   b) Json files
   c) csv files
- Use python 3.8+
- Dbase tables creation code in DOC folder.

### Install requirements
```
$ pip install -r requirements.txt
```

### Running the scrapper
```
$ python3 scrapper.py
```

### Structure
- docs/sql_generator.txt  -->  use the code from this file to generate the db tables needed for API extraction
- libs/_init_.py
- libs/api_signature.py
- libs/currency_parser.py
- libs/customer_parser.py
- libs/db_connection.py
- libs/invoice_parser.py
- libs/products_parser.py
- README.md
- requirements.txt
- scrapper.py    --> the file that needs to be run!

### Attn!
The scraper is coded to upload the data from API to DB!
If you want to use the Json exporter or the csv exporters you will have to create a folder named 'data' in the main
path of scraper! That's the same place where docs and libs are.
