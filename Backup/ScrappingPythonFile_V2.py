import json
import re
import requests
from bs4 import BeautifulSoup,  ResultSet, Tag
from urllib.request import Request, urlopen
import ftfy
import time
from datetime import datetime
import pytz

import warnings
from bs4 import MarkupResemblesLocatorWarning

listofdealersurlsUS=[]
listofdealersTitlesUS=[]

listofdealersurlsCanada=[]
listofdealersTitlesCanada=[]

listofspecificDealersID=[]
listofspecificDealersNames=[]
listofspecificDealersURLS=[]
listofspecificDealersAddress=[]


def clean_html_text(html_content: str):

    warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

    soup = BeautifulSoup(str(html_content), "html.parser")
    return soup.get_text(strip=True)

def getHeaders() -> dict:
    dictionarytouse= [{ 
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'es-US,es-419;q=0.9,es;q=0.8,en;q=0.7',
            'cache-control': 'max-age=0',
            'priority': 'u=0, i',
            'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
        },{'User-Agent': 'Mozilla/5.0'}]
    return dictionarytouse[0]


sampleurls = [
    "https://www.henryusa.com/henry-dealer-locations-nearest-to-you/firearm-dealers-iowa/",
    "https://www.henryusa.com/henry-dealer-locations-nearest-to-you/firearm-dealers-tennessee/",
    "https://www.henryusa.com/henry-dealer-locations-nearest-to-you/firearm-dealers-quebec/"
]
def fix_encoding(text):
    return ftfy.fix_text(text)

def refiningcontactdetailstext (texttorefine: str):
    new_text=texttorefine
    unwantedstrings = ["Contact Name:", "Phone:", "Email", "Website:", "Fax:"]
    for string in unwantedstrings:
        if string in texttorefine:
            new_text = texttorefine.replace(string, "").strip()
    return new_text

def getContactDetailsPosition (texttoanalyse: str,contactdetailslist_sofar: list):
   
    #Determining positions NOT taken
    positionsNOTtaken=[]
    for index, item in enumerate(contactdetailslist_sofar):
        if item == 'Empty field':
            positionsNOTtaken.append(index)

    if len(positionsNOTtaken) > 4:
        position=positionsNOTtaken[-(len(positionsNOTtaken)-4)] if len(positionsNOTtaken) > 1 else positionsNOTtaken[-1]
    else:
        position=positionsNOTtaken[0] if len(positionsNOTtaken) > 1 else positionsNOTtaken[-1]


   #Getting field positions for extracted text
    fieldpositiondictionary = {"Contact Name:":0, "Phone:":1, "Email":2, "Website:":3, "Fax:":4}
    
    for item in fieldpositiondictionary:
        if item in texttoanalyse:
            position = fieldpositiondictionary[item]
            break
    return position


def writefile(title,input):
    if (isinstance(input,str)):
        stringtowrite=input
    else:
        stringtowrite=''
        if isinstance(input,ResultSet):
            for element in input:
                stringtowrite+=element.prettify()+"\n\n"
        elif isinstance(input,Tag):
            stringtowrite=input.prettify()
        elif isinstance(input,list):
            for element in input:
                stringtowrite+=element+"\n\n"
    
    filename=f"{title}.txt"
    with open (filename, "w", encoding='utf-8') as f:
        f.write(stringtowrite)


def write_log(title: str, items: list, additional_text: str):
    madrid_tz = pytz.timezone('Europe/Madrid')
    timestamp = datetime.now(madrid_tz).strftime("%Y-%m-%d %H:%M:%S")

    with open(f"{title}.log", "a", encoding="utf-8") as file:
        file.write(f"\n[{timestamp}] Log Entry:\n")
        file.write(f"{additional_text}\n")  # Append the additional string
        for item in items:
            file.write(f"- {item}\n")

   
def getlistofinfo(listofdealersresult: ResultSet,distinguisher: list):
        
        for dealer in listofdealersresult:
            if distinguisher=='US':

                listofdealersurlsUS.append(dealer['href'])
                listofdealersTitlesUS.append(dealer['title'])
            
            elif distinguisher=='CA':
                listofdealersurlsCanada.append(dealer['href'])
                listofdealersTitlesCanada.append(dealer['title'])

            writefile('listofdealersurlsCanada',listofdealersurlsCanada)
            writefile('listofdealersurlsUS',listofdealersurlsUS)
        return
 

def generaldealersinfoextraction(soupobject: BeautifulSoup) ->list:
    distinguisher=['US','CA','Popular_US_Cities']
    listofstatesdata=soupobject.find_all('ul',class_='state-grid')
    for index, alist in enumerate(listofstatesdata):
        atagfromstate_grid=alist.find_all('a')
        getlistofinfo(atagfromstate_grid,distinguisher[index])
    return


def specificdealerexportation(listofspecificDealersIDs: list,listofspecificDealersNames: list,listofspecificDealersURLS: list, listofspecificDealersAddresses:list,listofspecificDealersStates:list, distinguisher:str) ->None:
    import pandas as pd
    nameforfile=f'SpecificListofDealers_{distinguisher}.csv'
    headerforcsv=['No.','ID','Name','URL','Address','State']
    df=pd.DataFrame(columns=headerforcsv)

    for index in range(len(listofspecificDealersIDs)):
    
        df.loc[index]=[index+1,listofspecificDealersIDs[index], listofspecificDealersNames[index],listofspecificDealersURLS[index],listofspecificDealersAddresses[index],listofspecificDealersStates[index]]

    df.to_csv(nameforfile, index=False,encoding='utf-8-sig')
    
def specificdealerexportation_contacts(listofspecificDealersIDs: list,listofspecificDealersNames: list,listofspecificDealersURLS: list, listofspecificDealersAddresses:list,listofspecificDealersStates:list, listofcontactdetails: list,distinguisher:str) ->None:
    import pandas as pd
    nameforfile=f'SpecificListofDealersContacts_{distinguisher}.csv'
    headerforcsv=['No.','ID','Name','URL','Address','State','Contact details 1','Contact details 2','Contact details 3','Contact details 4','Contact details 5','Contact details 6','Contact details 7']
    
    df=pd.DataFrame(columns=headerforcsv)

    for index in range(len(listofcontactdetails)):
           
        df.loc[index]=[index+1,listofspecificDealersIDs[index], listofspecificDealersNames[index],listofspecificDealersURLS[index],listofspecificDealersAddresses[index],listofspecificDealersStates[index],listofcontactdetails[index][0],listofcontactdetails[index][1],listofcontactdetails[index][2],
                       listofcontactdetails[index][3],listofcontactdetails[index][4],listofcontactdetails[index][5],listofcontactdetails[index][6]]

    df.to_csv(nameforfile, index=False,encoding='utf-8-sig')


def getnumeroofurlaextraer():
   message="How many URLs do you want to extract data from? Press '*' to select all: "
   numberodeurlsaextraer=input(message)
   if numberodeurlsaextraer=="*":
        numberodeurlsaextraer=None
   elif int(numberodeurlsaextraer)>0:
        numberodeurlsaextraer=int(numberodeurlsaextraer)
    
   return numberodeurlsaextraer

def extractingspecificdetails(listofStatesURL: list,distinguisher: str):
    from urllib.error import URLError, HTTPError
    import pandas as pd

    iteraciones=0

    urlswitherrors=[]
    
    dealer_state_region=''
    listofspecificDealersIDs=[]
    listofspecificDealersNames=[]
    listofspecificDealersURLS=[]
    listofspecificDealersAddresses=[]
    listofspecificDealersStatuses=[]
    listofspecificDealersStates=[]
    
    numerodeurlsaextraer=len(listofStatesURL[:getnumeroofurlaextraer()])

    for index,url in enumerate(listofStatesURL[:numerodeurlsaextraer]):
        
        iteraciones=counterdeprogreso(iteraciones,numerodeurlsaextraer)

        if distinguisher == 'US':
            dealer_state_region=listofdealersTitlesUS[index]
        elif distinguisher=='CA':
            dealer_state_region=listofdealersTitlesCanada[index]
        elif distinguisher == 'Sample':
            dealer_state_region='Mixed (US/CA)'

        req = Request(url, headers=getHeaders())

        try:
            page = urlopen(req)
            soup = BeautifulSoup(page,"html.parser")
            script_tag = soup.find("script", id="dealer-js-js-extra")
            if  script_tag!= None:
                script_content = script_tag.string
                match = re.search(r'var page_data = ({.*});', script_content)
                if match:
                    json_data = match.group(1)  # Extract JSON-like string
                    parsed_data = json.loads(json_data)  # Convert to Python dictionary
                else:
                    print("No JSON data found.")
                

                dealerslist=parsed_data['dealers']
                for dealer in dealerslist:
                    dealersID=clean_html_text(dealer['id'])
                    dealersName=clean_html_text(dealer['name'])
                    dealersURL=clean_html_text(dealer['permalink'])
                    dealersAddress=clean_html_text(dealer['address'])
                    dealerStatus=clean_html_text(dealer['status'])
                    
                    listofspecificDealersIDs.append(dealersID)
                    listofspecificDealersNames.append(dealersName)
                    listofspecificDealersURLS.append(dealersURL)
                    listofspecificDealersAddresses.append(dealersAddress)
                    listofspecificDealersStates.append(dealer_state_region)
                    listofspecificDealersStatuses.append(dealerStatus)

            else:
                urlswitherrors.append(url+ "\n" + r"Nonetype for soup.find('script', id='dealer-js-js-extra')")
                writefile('URLSwitherrors',urlswitherrors)
            
        except HTTPError as e:
            if hasattr(e, 'code'):
                errorstring=f"Error code: {e.code}"
            else:
                errorstring = f"General error: {str(e)}"
            print(errorstring)
            urlswitherrors.append(url  + "\n" + errorstring + "\n\n" )
        except URLError as e:
            if hasattr(e, 'reason'):
                errorstring=f"Error code: {e.reason}"
            else:
                errorstring = f"General error: {str(e)}"
            print(errorstring)
            urlswitherrors.append(url  + "\n" + errorstring + "\n\n" )
        else:
           write_log('Logunknown_exception',listofspecificDealersURLS,url)


    writefile(f'urlswitherrors_{distinguisher}',urlswitherrors)
    
    return listofspecificDealersIDs,listofspecificDealersNames,listofspecificDealersURLS,listofspecificDealersAddresses,listofspecificDealersStatuses,listofspecificDealersStates



def extracting_contact_details(listofdealersURL: list,listofspecificDealersStatuses: list,distinguisher: str):
    from urllib.error import URLError, HTTPError
    import pandas as pd

    iteraciones=0

    urlswitherrors=[]
    contactdetails=[]

    print(f'Extracting contact details for: {distinguisher}')

    numerodeurlsaextraer=len(listofdealersURL[:getnumeroofurlaextraer()])

    for index,url in enumerate(listofdealersURL[:numerodeurlsaextraer]):
        contactdetailsforelement=['Empty field']*7
        iteraciones=counterdeprogreso(iteraciones,numerodeurlsaextraer)

        try:
            req = Request(url, headers=getHeaders())
            page = urlopen(req)
            soup = BeautifulSoup(page,"html.parser")
            dealercontact=soup.find_all("div", class_="flexy")
            if  dealercontact!= None:
                for index, item  in enumerate (dealercontact):
                    if 'Email' in item.decode_contents():
                        emailaddress=str(item.find('a')['title'])
                        position = getContactDetailsPosition(emailaddress,contactdetailsforelement)
                        contactdetailsforelement[position]=refiningcontactdetailstext(emailaddress)
                    else:
                        contactdetail=fix_encoding(item.get_text(strip=True))
                        position = getContactDetailsPosition(contactdetail,contactdetailsforelement)
                        contactdetailsforelement[position]=refiningcontactdetailstext(contactdetail)
            else:
                urlswitherrors.append(url+ "\n" + r"Nonetype for soup.find('script', id='dealer-js-js-extra')")
                writefile('URLSwitherrors',urlswitherrors)
            
            contactdetails.append(contactdetailsforelement)

        except HTTPError as e:
            if hasattr(e, 'code'):
                errorstring=f"Error code: {e.code}"
            else:
                errorstring = f"General error: {str(e)}"
            print(errorstring)
            urlswitherrors.append(url  + "\n" + errorstring + "\n\n" )

        except URLError as e:
            if hasattr(e, 'reason'):
                errorstring=f"Error code: {e.reason}"
            else:
                errorstring = f"General error: {str(e)}"
            urlswitherrors.append(url  + "\n" + errorstring + "\n\n" )
        else:
           write_log('mainlog_contacts',contactdetailsforelement,url)

        write_log('logforcontact',contactdetailsforelement,url)  

    writefile('urlswitherrors',urlswitherrors)

    return contactdetails
   

def counterdeprogreso(counter,total):
        urlsbetweenpauses=10 # ;'Number of urls before every stop'
        if (counter != 0) and (counter % urlsbetweenpauses==0):
            time.sleep(5)
        print('\n')
        print(counter,(f'{counter/total:.2%}'))
        return counter+1


def pagesrequests(url: str)-> BeautifulSoup:
    req = Request(url, headers=getHeaders())
    page = urlopen(req)
    soup = BeautifulSoup(page,"html.parser")
    return soup


def runmainurlsextraction():
    maxpageindex=0
    message='Enter the maximum page index to extract from '
    maxpageindex=int(input(message))
    for index in range(maxpageindex+1): 
        soupforrequest=pagesrequests('https://www.henryusa.com/own-a-henry/find-a-henry-dealer/')
        generaldealersinfoextraction(soupforrequest)
        

def promptspecificjobdetailsextraction(distinguisher: str,extractionurlcondition: str):
    print(f'Starting export for: {distinguisher}')

    if extractionurlcondition=="0":
        urlstouse=sampleurls
    elif extractionurlcondition=="1":
        if distinguisher=='US':
            urlstouse=listofdealersurlsUS
        elif distinguisher == 'CA':
            urlstouse=listofdealersurlsCanada
    

    listofspecificDealersIDs,listofspecificDealersNames,listofspecificDealersURLS,listofspecificDealersAddresses,listofspecificDealersStatuses,listofspecificDealersStates=extractingspecificdetails(urlstouse,distinguisher)

    specificdealerexportation(listofspecificDealersIDs,listofspecificDealersNames,listofspecificDealersURLS,listofspecificDealersAddresses,listofspecificDealersStates,distinguisher)
    
    message=f"Press 1 to extract contact details for {distinguisher}. Press any other key to skip: "
    specific_contact_detail= input(message)

    if specific_contact_detail=='1':
            listofcontactdetails=extracting_contact_details(listofspecificDealersURLS,listofspecificDealersStatuses,distinguisher)
            specificdealerexportation_contacts(listofspecificDealersIDs,listofspecificDealersNames,listofspecificDealersURLS,listofspecificDealersAddresses,listofspecificDealersStates,listofcontactdetails,distinguisher)
    

def promptinguser_startprogram():
    start = time.time()

    startcondition=""
    while startcondition != "1" and startcondition != "2":
        message='Press 1 to extract general information, or 2 to extract specific details: '
        startcondition=input(message)
    if startcondition=="1":
        runmainurlsextraction()
        
        'for the US'
        
        dataforexportation=[listofdealersurlsUS,listofdealersTitlesUS]
        data_exportation(f'GeneralListofDealers_US.csv',dataforexportation,['No.','State/Province/Region','URLs'])
       
        'for Canada'
        
        dataforexportation=[listofdealersurlsCanada,listofdealersTitlesCanada]
        data_exportation(f'GeneralListofDealers_CA.csv',dataforexportation,['No.','State/Province/Region','URLs'])
       
        promptspecificjobdetailsextraction(distinguisher='US',extractionurlcondition='1')

        promptspecificjobdetailsextraction(distinguisher='CA',extractionurlcondition='1')
        

    elif startcondition =="2":
        promptspecificjobdetailsextraction(distinguisher='Sample',extractionurlcondition='0')

    end = time.time()
    execution_time = (end - start) / 60
    print(f"Execution Time: {execution_time:.2f} minutes")



def data_exportation(nameoffile: str,arrayofvariables: list,headerforcsv:list) ->None:
    
    lengthoflist=len(arrayofvariables[0])

    import pandas as pd
    df=pd.DataFrame(columns =headerforcsv)

    for index in range(lengthoflist):
        df.loc[index]=[index + 1] + [array[index] for array in arrayofvariables]

    df.to_csv(nameoffile, index=False)




promptinguser_startprogram()


