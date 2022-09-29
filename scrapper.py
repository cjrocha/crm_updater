from libs import api_signature, currency_parser, customer_parser, invoice_parser, products_parser
import json, os, random, requests, time

"""
Python code to handle and upload to MariaDB the data
received from Unleashed API 
"""
#Supports Json generation of data. See comments bellow.

class UnleashedScraper():
    #Api credits
    def __init__(self) -> None:
        self.base_url = "https://api.unleashedsoftware.com/"
        self.API_ID = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        self.API_KEY = "xxxxxx........xxxxxxxxxxx"
        if not (self.API_ID and self.API_KEY):
            raise Exception(f"API_ID / API_KEY not found on env variable!")
        
    def data_parser(self,data,endpoint):
        """_summary_
            Parsing raw data, then save to csv file.
        Args:
            data (dict): raw data.
            endpoint (str): name of API endpoint that data coming from.
        """

        if endpoint=='Currencies':
            currency_parser(data)
        elif endpoint=='Customers':
            customer_parser(data)
        elif endpoint=='Invoices':
            invoice_parser(data)
        elif endpoint=='Products':
            products_parser(data)
            
    def get_headers(self,query_string=''):
        """_summary_
            generate specific headers for particular API_ID, API_KEY, and query_string. 
        Args:
            query_string (str, optional): query param string. Defaults to ''.

        Returns:
            dict: dictionary of the headers.
        """

        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'api-auth-id': self.API_ID,
            'api-auth-signature': api_signature(query_string,self.API_KEY)
        }

    def req_crawler(self,url,headers):
        """_summary_
            The unleashed API fetcher.
        
        Args:
            url (str): wanted url in full format (with or without query params).
            headers (dict): the headers required for this request.

        Returns:
            tuple: (response,error) returning response of the request and the error (if any).
        """

        res = None
        error = None
        try:
            res = requests.get(url, headers=headers, timeout=20) #verify=False,           
        except requests.exceptions.HTTPError as err:
            error = f"HTTP ERROR - {err}"
        except requests.exceptions.SSLError as err:
            error = f"SSL ERROR - {err}"
        except requests.exceptions.RequestException as err:
            error = f"OTHER REQ ERROR - {err}"
        except Exception as err:
            error = f"OTHER ERROR - {err}"
        return res,error

    def fetcher_ctrl(self,endpoint,endpoint_id=None,crawl_mode='all',page_num=None,page_size=None,qfilter_key=None,qfilter_val=None):
        """_summary_
            api fetcher controller.
            have 3 crawling mode: all, page, filter.
            - all: crawling all data on that endpoint.
            - page: crawling particular page on that endpoint.
            - filter: crawling particular filter by its key & value. 
        
        Args:
            endpoint (str): particular endpoint of unleashed API. See unleashed API docs for available endpoints.
            endpoint_id (str): ID of the particular element from the endpoint. Defaults to None.
            crawl_mode (str, optional): crawling mode: all, page, filter. Defaults to 'all'.
            page_num (int, optional): Defaults to None.
            page_size (int, optional): Defaults to None.
            qfilter_key (str, optional): query filter key, diferent for each endpoint. See unleashed API docs for more details. Defaults to None.
            qfilter_val (str, optional): query filter value. Defaults to None.
            
            Reports any error found during process in console.
        """

        query_string = ''
        surl = f"{self.base_url}/{endpoint}"
        sheaders = self.get_headers(query_string)
        sres,serror = self.req_crawler(surl,sheaders)
        if isinstance(sres, requests.models.Response):
            if sres.status_code == 200:
                sdata = sres.json()
                try:
                    det_pgs = sdata['Pagination']['NumberOfPages']
                    #crawl_mode == 'page'
                    for x in range(1, det_pgs+1):
                        url = f"{self.base_url}/{endpoint}/{x}"
                        headers = self.get_headers(query_string)
                        res,error = self.req_crawler(url,headers)
                        if isinstance(res, requests.models.Response):
                            if res.status_code == 200:
                                data = res.json()
                                # if Json format data is needed please uncomment these 2 lines!    
                                #with open(f"data/{endpoint}.json", "w") as write_file:
                                #    json.dump(data, write_file, indent=4)
                                #end of json data export
                                self.data_parser(data['Items'],endpoint)
                            else:
                                print(f"status_code: {res.status_code}")
                                print(f"response_text: {res.text}")
                        else:
                            print(f"error: {error}")
                            print(res.text)
                except:
                    url = f"{self.base_url}/{endpoint}"
                    headers = self.get_headers(query_string)
                    res,error = self.req_crawler(url,headers)
                    if isinstance(res, requests.models.Response):
                        if res.status_code == 200:
                            data = res.json()
                            # if Json format data is needed please uncomment these 2 lines!     
                            #with open(f"data/{endpoint}.json", "w") as write_file:
                            #    json.dump(data, write_file, indent=4)
                            #end of json data export
                            self.data_parser(data['Items'],endpoint)
                        else:
                            print(f"status_code: {res.status_code}")
                            print(f"response_text: {res.text}")    
                    else:
                        print(f"error: {error}")
                        print(res.text)
            else:
                print(f"status_code: {sres.status_code}")
                print(f"response_text: {sres.text}")            
        else:
            print(f"error: {serror}")
            print(sres.text)                    

if __name__ == "__main__":
    """
    Consider this function as a switcher:
    It tells program wich endpoints to follow.
    If not all endpoints are needed, just comment them.
    """
    endpoints = [
        'Currencies',
        'Customers',
        'Invoices',
        'Products',
    ]
    us = UnleashedScraper()
    for key in endpoints:
        us.fetcher_ctrl(key)
