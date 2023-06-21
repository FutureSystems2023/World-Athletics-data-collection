# **Documentation**

This python script is to automate the results collection from <a href="https://worldathletics.org/">World Athletics website</a>. The website uses GraphQL APIs hosted on AWS. Results will be downloaded and be compiled into one Excel file based on user specified parameters. There is primarily 2 ways of scraping data from the IF website, please find out more under <a href="#scraping-operations">scraping operations</a>.

1. <a href="#scraping-by-country">Scraping by Country</a> (Gathering all athletes from a country and then scrape results for each one of them)
2. <a href="#2-scraping-by-athlete">Scraping by Athlete</a> (Gather all athletes results based on provided namelist)

<hr>

## **Requirements (Installation)**

Change into current directory and run pip to install required packages using the following command

<pre><code>pip install -r requirements.txt</code></pre>
<hr>

## **API Endpoint**

API Endpoint is:

<pre><code>https://jpvxtz2frzayfix6m7whizuccm.appsync-api.eu-west-1.amazonaws.com/graphql</code></pre>

Do note that API endpoint or API key may change in the future. Please update this in api.json.

<pre>
    <code>
{
    "apiEndPoint": "https://jpvxtz2frzayfix6m7whizuccm.appsync-api.eu-west-1.amazonaws.com/graphql",
    "apiKey": "da2-ii5irlhy7fd57aptsgby37bt3e"
}
    </code>
</pre>
<hr>

## **Scraping Operations**

### **1. Scraping by Country**
Countries to be scraped are referenced in config.py file. In this operation, script will first go through each country defined. To change this, refer to section on changing parameters.

<br/>

### **2. Scraping by Athlete**
In this operation, user can search and append the cleaned search results to an already populated cleaned results csv file. Script will pull up a search via the API and user will be required to input the index of the athlete to scrape from the search results API. The syntax will be as follow:

<pre>
    <code>
    python script.py -search -append
    </code>
</pre>

User can also scrape by providing a name list of athletes that you would like to scrape. This can be done by using the "-athCSV" switch tag. Follow the on screen console instructions to select the appropriate athlete to scrape. Syntax will be as follow:

<pre>
    <code>
    python script.py -search -athCSV INPUT_NAMELIST_CSV_TO_SEARCH_HERE
    </code>
</pre>

<i>Do note that name list csv file provided in argument **should have a data header**, if not the first name will be skipped.</i>

<hr>

## **Changing Parameters**

For changing parameters, this can be done in config.py and using arguments when calling script.py (use -h switch for more details).
<br>

To change countries to be scrapped, edit the following code block found in config.py:

<pre><code>
countries_list = [
    "Singapore",
    "Philippines",
    "Malaysia",
    "Vietnam",
    "Indonesia",
    "Thailand",
    "Myanmar"
]
</pre></code>

<br>
Currently, the excel file name is generated dynamically using the time when the script is ran. To change the excel file name, edit the following line and ensure that it ends with (".xlsx") file format:

<pre><code>
filename = now + ".xlsx"
</pre></code>
