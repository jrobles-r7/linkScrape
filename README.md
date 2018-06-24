# linkScrape 
![Supported Python versions](https://img.shields.io/badge/python-2.7-blue.svg)

    linkScrape.py
    Description: Enumerates employee names from LinkedIn.com 
    Developers: Nick Sanzotta (@beamr), Jacob Robles (@shellfail)

**Considerations:**

    linkScrape is a pure Web Scraper, that does not utilize LinkedIn's API.
    linkScrape has limitations/bugs when scraping some character sets.
    Your LinkedIn.com account may be flagged or banned.
    Your LinkedIn.com account will need a minimum of 10 connections to to perform company based searches.
    Your LinkedIn.com account has a monthly commercial use limit.

**Installation:**

    git clone https://github.com/NickSanzotta/linkScrape.git
    cd linkScrape
    pip install -r requirements.txt
    python linkScrape.py --help


 **TIPS:**
 
**Use quotes for companies with white space**
 
 `python linkScrape.py -c'Example Company' -r1`
   
<br>

**LinkedIn Company ID search:**

Using a LinkedIn company ID is the most accurate way to search for a company. It's also the only way to search for universities.

`python linkScrape.py -c 100 -r1`

<br>

**Finding a LinkedIn company ID:**

In your browser perform a search for a company on LinkedIn.com. Once you find the company's profile page click the link: 

"<i>See all (Numeral) employees on LinkedIn</i>" 

Next inspect the URL for the LinkedIn company ID, below is an example URL with the company ID highlighted in bold.
<br>

ht<span>tps://</span><span>ww</span>w.linkedin.com/search/results/people/?facetCurrentCompany=%5B%22<b>39624</b>%22%2C%22118552%22%5D&lipi=urn%3Ali%3Apage%3Ad_flagship3_company%3BdmKCXJhuRE2mHw1V0%2BqXhw%3D%3D
  
<br>

**Similar named companies:**

Companies that share similar names, will produce multiple results and require the user to choose one, as shown in the example below.

```
python linkScrape.py -c'Example Company' -r1
  
1: Example Company
2: Example Inc.
3: Example Advertising
            
Please Select a Company: 1
ENTERED: "Example Company"

Company Name: Example Company
Industry / Employees: Printing; 5001-10,000 employees
LinkedIn CompanyID: 100
URL: https://www.linkedin.com/company/100
```
<br>
**Default Values:**

    If a parameter is not defined it's default value will be choosen.
    Default values listed below.
  
    Mangle Option = 7  ex: FLast
    Page Results = 1-3
    Time out value = 3
    
**Usage (CLI):**

    Usage: python linkScrape.py <OPTIONS>
    Example[1]: python linkScrape.py -e LinkedInUser@email.com -c 'Example Company' -r 10 -t 3 -m 7 -d example.com
    Example[2]: python linkScrape.py -e LinkedInUser@email.com -c 'Example Company' -r 5-10 -t 3 -m 7 -d example.com
    Example[3]: python linkScrape.py -e LinkedInUser@email.com -c 100 -r 3 -t 3 -m 7 -d example.com
    Example[4]: python linkScrape.py -m 7 -i ~/Company/names.txt\n"
    Formatted output saved to: linkedIn/linkScrape-data/Company-mangle[x]_time.txt
    
    Login options:
    -e <email> Your LinkedIn.com Email Address.
    -p <pass>  Your LinkedIn.com Password. (If -p parameter is not defined, you'll be prompt to enter a password)
    
    Search options:
    -c <company> Search company name or company ID.
    -r <results> Searches X number of LinkedIn.com pages, or a range of pages (Default is 1-3).
    -t <secs>    Sets timeout value. (Default is 3.)
 
**Usage (Wizard):**

      ENTERED: "Example Company"


       Mangle options:

             -m <mangle>    
                                       1)FirstLast        
                                       2)LastFirst        
                                       3)First.Last       
                                       4)Last.First       
                                       5)First_Last       
                                       6)Last_First       
                                       7)FLast            
                                       8)LFirst           
                                       9)FirstL           
                                      10)F.Last           
                                      11)L.Firstname      
                                      12)FirLa            
                                      13)Lastfir
                                      14)FirstLastnam
                                      15)LastF
                                      16)LasFi
                                      99)All              Mangle using all types

      Enter name Managle choice[ex:7]: 
      ENTERED: "7"

      [*]TIP: This value will determine how many page results will be returned.
      Enter number of pages results[ex:3] or a range of pages [ex:1-3]: 
      ENTERED: "1-3"

      [*]TIP: This value will determine how long of a delay(in seconds) each page will be scraped.
      Enter timeout value[ex:3]: 
      ENTERED: "3"

      [*]TIP: This value will be added to the end of each mangled result[ex:jdoe@example.com].
      Enter Domain suffix[ex:example.com]: example.com
      ENTERED: "example.com"


**Mangle Options:** 
    
    -m <mangle>
        1)FirstLast        
        2)LastFirst        
        3)First.Last       
        4)Last.First       
        5)First_Last       
        6)Last_First       
        7)FLast            
        8)LFirst           
        9)FirstL           
        10)F.Last          
        11)L.Firstname     
        12)FirLa           
        13)Lastfir
        14)FirstLastnam             
        15)LastF
        16)LasFi
        99)All              Mangle using all types

  
    -d <domain> Append @example.com to enumerated user list."
    -i <input>  Use local file instead of LinkedIn.com to perform name Mangle."
    
    -h <help>  Prints this help menu.
