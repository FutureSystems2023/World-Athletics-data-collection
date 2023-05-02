# **Documentation**

This python script is to automate the results collection from <a href="https://worldathletics.org/">World Athletics website</a>. The website uses GraphQL APIs hosted on AWS. Results will be downloaded and be compiled into one Excel file based on user specified parameters.

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
