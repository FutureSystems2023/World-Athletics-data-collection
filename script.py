import pandas as pd
import requests as re
import config
import json
import argparse
import sys
import warnings
import datetime as dt

from pandas.errors import SettingWithCopyWarning
warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)
warnings.simplefilter(action="ignore", category=FutureWarning)


class API:

    f = open('api.json')
    data = json.load(f)
    apiEndPoint = data['apiEndPoint']
    apiKey = data['apiKey']
    headers = {
        'Accept': '*/*',
        'Content-Type': 'application/json',
        'User-Agent': 'PostmanRuntime/7.29.2',
        'Accept-Encoding': 'gzip, deflate, br',
        'x-api-key': apiKey
    }

    def __init__(self, query, variables=None):
        self.query = query
        self.variables = variables

    def __str__(self):
        return f"API Endpoint: {self.apiEndPoint}\nAPI Key: {self.apiKey}\nQuery:\n[{self.query}]\nVariables:\n[{self.variables}]"

    def fetch_data(self):
        res = re.post(
            url=self.apiEndPoint,
            headers=self.headers,
            json={
                "query": self.query,
                "variables": self.variables
            }
        )
        if res.status_code == 200:
            return res.json()
        else:
            print("Failed calling API!")
            print(res.text)
            exit


def searchCompetitor(query=None, gender=None, disciplineCode=None, environment=None, countryCode=None):
    queryBody = config.searchCompetitorQuery
    queryVariables = {
        "query": query,
        "gender": gender,
        "disciplineCode": disciplineCode,
        "environment": environment,
        "countryCode": countryCode,
    }
    json_data = API(queryBody, queryVariables).fetch_data()
    if json_data['data']['searchCompetitors'] == None:
        print("Search not found for", query, countryCode, ".")
    df = pd.DataFrame.from_dict(json_data['data']['searchCompetitors'])
    return df


def getCompetitorResultsByDiscipline(AthleteID=None, resultsByYearOrderBy=None, resultsByYear=None):
    queryBody = config.getCompetitorResultsByDiscipline
    queryVariables = {
        "id": AthleteID,
        "resultsByYearOrderBy": resultsByYearOrderBy,
        "resultsByYear": resultsByYear
    }

    json_data = API(queryBody, queryVariables).fetch_data()
    if json_data['data']['getSingleCompetitorResultsDiscipline'] != None:
        resultsByEvent = json_data['data']['getSingleCompetitorResultsDiscipline']['resultsByEvent']
    else:
        return "Not Found"
    df = pd.DataFrame()
    for discipline in range(len(resultsByEvent)):
        df_results = pd.DataFrame.from_dict(resultsByEvent[discipline]['results'])
        df_results['discipline'] = resultsByEvent[discipline]['discipline']
        df = pd.concat([df, df_results])
    return df


def getCountryAthletesResults(countryCode="SGP", resultsYear=None):
    if countryCode == "NOT FOUND" or len(countryCode) != 3:
        return pd.DataFrame(["countryCode " + countryCode], )
    if resultsYear == None:
        resultsYear = 2023
    df = pd.DataFrame()
    df_Athletes = searchCompetitor(countryCode=countryCode)
    athletesCount = len(df_Athletes)
    print("API fetched", athletesCount, "athletes for", countryCode)
    athleteActiveInYearCount = 0
    for i, athleteID in df_Athletes['aaAthleteId'].items():
        try:
            df_result = getCompetitorResultsByDiscipline(AthleteID=athleteID, resultsByYear=resultsYear)
            df_result['athlete_name'] = df_Athletes['givenName'][i]
            df_result['athlete_id'] = athleteID
            df_result['athlete_countryCode'] = countryCode
            df = pd.concat([df, df_result])
            athleteActiveInYearCount += 1
        except:
            print(" ".join(["Results for", df_Athletes['givenName'][i], "(" + athleteID + "):", df_result]))
        progressBar(i, athletesCount - 1)
    print("Total active athletes with results in", resultsYear, "is :", athleteActiveInYearCount, "/", athletesCount)
    return df


def getCountryCode(countryName=""):
    f = open('countryCodes.json')
    data = json.load(f)
    for i in range(len(data['countryCodes'])):
        if data['countryCodes'][i]['name'].lower() == countryName.lower():
            return data['countryCodes'][i]['code']
    print("Country Code not found. Check Country Name.")
    return "NOT FOUND"


def getDisciplineCode(disciplineName=""):
    f = open('disciplineCodes.json')
    data = json.load(f)
    for i in range(len(data['disciplineCodes'])):
        if data['disciplineCodes'][i]['name'].lower().strip() == disciplineName.lower().strip():
            return data['disciplineCodes'][i]['code']
    print("Discipline Code not found. Check Discipline Name.")
    return "NOT FOUND"


def progressBar(count_value, total, suffix=''):
    bar_length = 100
    filled_up_Length = int(round(bar_length * count_value / float(total)))
    percentage = round(100.0 * count_value/float(total), 1)
    bar = '=' * filled_up_Length + '-' * (bar_length - filled_up_Length)
    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percentage, '%', suffix))
    sys.stdout.flush()


def fetchResults():
    print("Your arguments are: \nCountries=", config.countries_list, "\nYears=", config.years_list)

    try:
        writer = pd.ExcelWriter(path=config.scrappedRawFileName, engine='openpyxl')
    except PermissionError:
        print("Unable to write to {}. Please ensure file is closed before running the script.".format(config.scrappedRawFileName))
        return
    except Exception as e:
        print(e)
        return

    countries_list = config.countries_list
    for country in countries_list:
        df = pd.DataFrame()
        for year in config.years_list:
            df = pd.concat([df, getCountryAthletesResults(countryCode=getCountryCode(countryName=country), resultsYear=year)])
        df['athlete_country'] = country
        df.to_excel(writer, sheet_name=country, index=False)
    writer.close()
    print("Results fetched successfully!")
    return


def compileResults():
    print("Compiling results into one sheet...")
    df = pd.concat(pd.read_excel(config.scrappedRawFileName, sheet_name=None))
    writer = pd.ExcelWriter(path=config.scrappedRawFileName, engine='openpyxl', mode='a')
    df.to_excel(writer, sheet_name='ALL_COUNTRIES', index=None)
    writer.close()
    return


# This function is for cleaning timings (instances where there is a random h in the timings and remove any "DNQ" and other strings etc.)
def cleanResults(targetFileName=config.scrappedRawFileName, sheet_name="ALL_COUNTRIES", outputFileName="cleanedResults.csv"):
    print("Commencing data cleaning operations for {0}...".format(targetFileName))
    try:
        if targetFileName == config.scrappedRawFileName:
            df = pd.read_excel(targetFileName, sheet_name=sheet_name, engine="openpyxl")
        else:
            df = pd.read_csv(targetFileName)
        print("Attempting to remove non-numeric results (e.g. DNF, DQ, etc.) and converting results to seconds...")
        df['mark'] = df['mark'].str.replace('h', '0', regex=False)
        df_strRemoved = df[(df['mark'].str.contains('\d', regex=True))]
        df_strRemoved['mark'] = df_strRemoved['mark'].apply(lambda x: convertStrToSeconds(x))
        df_strRemoved.to_csv(outputFileName, index=False)
        print("Results cleaned successfully and saved as", outputFileName)
    except Exception as e:
        print(e)
    return


def convertStrToSeconds(x):
    # Data type is float (already in seconds, no conversion needed)
    if isinstance(x, str):
        # HH:MM:SS or HH:MM:SS.ms
        if x.count(":") == 2:
            colonIndex_1st = x.find(":")
            colonIndex_2nd = x.rfind(":")
            seconds = float(x[0:colonIndex_1st]) * 3600 + float(x[colonIndex_1st + 1:colonIndex_2nd]) * 60 + float(x[colonIndex_2nd + 1:])
        # MM:SS or MM:SS:ms
        elif x.count(":") == 1:
            colonIndex = x.find(":")
            seconds = float(x[0:colonIndex]) * 60 + float(x[colonIndex + 1:])
        else:
            seconds = float(x)
    elif isinstance(x, int) or isinstance(x, float):
        seconds = float(x)

    return seconds


def getResultsOfSelectedAthleteFromSearch(query="", discipline=""):
    df = pd.DataFrame()
    if discipline:
        discipline = getDisciplineCode(disciplineName=discipline)
    df_searchedResults = searchCompetitor(query=query, disciplineCode=discipline)
    print("The API found the following athletes matching your query.")
    print(df_searchedResults[["aaAthleteId", "givenName", "familyName", "country"]])
    selection = input("Please input index of athlete to include in scrapping (enter all for selecting all athletes from search results):")
    if selection.lower() != "all" and selection.isnumeric() == True:
        selected_index = int(selection)
        selected_aaAthleteId = df_searchedResults.iloc[selected_index]['aaAthleteId']
        print(" ".join(["Selected:", df_searchedResults.iloc[selected_index]
              ['givenName'], df_searchedResults.iloc[selected_index]['familyName'] + ".", "Commencing API Fetch..."]))
        for year in config.years_list:
            try:
                df_result = getCompetitorResultsByDiscipline(AthleteID=selected_aaAthleteId, resultsByYear=year)
                df_result['athlete_name'] = " ".join(
                    [df_searchedResults['givenName'][selected_index], df_searchedResults['familyName'][selected_index]])
                df_result['athlete_id'] = selected_aaAthleteId
                df_result['athlete_countryCode'] = df_searchedResults['country'][selected_index]
                df = pd.concat([df, df_result])
            except:
                print(" ".join(["Results for", df_searchedResults['givenName']
                      [selected_index], "(" + selected_aaAthleteId + "):", df_result]))
        print(df)
    else:
        print("Selected all athletes from search results.")
        for i, athleteID in df_searchedResults['aaAthleteId'].items():
            for year in config.years_list:
                try:
                    df_result = getCompetitorResultsByDiscipline(AthleteID=athleteID, resultsByYear=year)
                    df_result['athlete_name'] = " ".join([df_searchedResults['givenName'][i], df_searchedResults['familyName'][i]])
                    df_result['athlete_id'] = selected_aaAthleteId
                    df_result['athlete_countryCode'] = df_searchedResults['country'][i]
                    df = pd.concat([df, df_result])
                except:
                    print(" ".join(["Results for", df_searchedResults['givenName'][i], "(" + athleteID + "):", df_result]))
        print(df)
    try:
        df.to_csv("searchResults.csv", index=False)
        print("Saved results to searchResults.csv")
    except Exception as e:
        print(e)
    return


# List all unique disciplines in cleaned results and allow user to select disciplines
def filterCleanedResultsByDiscipline(targetFileName):
    print("Filtering results by discipline first...")
    df = pd.read_csv(targetFileName)
    df_uniqueDisciplines = pd.DataFrame(df["discipline"].unique(), columns=["Disciplines"])
    print(df_uniqueDisciplines)
    try:
        selected_index = int(input("Please select index of discipline for filtering:"))
        selected_discipline = df_uniqueDisciplines["Disciplines"][selected_index]
        print("Selected discipline ({}) for filtering of results".format(df_uniqueDisciplines["Disciplines"][selected_index]))
        df_filtered = df[df["discipline"] == selected_discipline]
        print("Filtering operations by discipline finished successfully (before rows: {0}, rows left: {1}).".format(
            len(df), len(df_filtered)))
        return df_filtered
    except Exception as e:
        print(e)
        return


# Filter cleaned results by namelist provided by namelist.csv (only run this def after running filterCleanedResultsByDiscipline())
def filterCleanedResultsByNamelist(df):
    print("Filtering results by names provided in {0} next...".format(config.namelistFileName))
    try:
        df_filtered = pd.DataFrame(columns=df.columns)
        df_namelist = pd.read_csv(config.namelistFileName)
        for i in range(len(df_namelist)):
            df_filtered = pd.concat([df_filtered, df[df['athlete_name'] == df_namelist.iloc[i, 0]]])
        print("Filtering operations by namelist finished successfully (before rows: {0}, rows left: {1}).".format(
            len(df), len(df_filtered)))
        return df_filtered
    except Exception as e:
        print(e)
        return


def generateFinalFilteredXlsx(df):
    print("Generating final filtered and cleaned results excel file...")
    try:
        writer = pd.ExcelWriter(path=config.finalFilteredCleanedFileName, engine='openpyxl')
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df_2019to2023 = df
        df_2022to2023 = df[(df["date"].dt.year == 2022) | (df["date"].dt.year == 2023)]
        df_2023 = df[(df["date"].dt.year == 2023)]
        df_2019to2023.to_excel(writer, sheet_name="Competitors 2019-2023", index=False)
        df_2022to2023.to_excel(writer, sheet_name="Competitors 2022-2023", index=False)
        df_2023.to_excel(writer, sheet_name="Competitors 2023", index=False)
        writer.close()
        print("Final filtered and cleaned results compiled successfully. Saved as {0}.".format(config.finalFilteredCleanedFileName))
    except PermissionError:
        print("Unable to write to {}. Please ensure file is closed before running the script.".format(config.scrappedRawFileName))
        return
    except Exception as e:
        print(e)
        return


def filterResults(targetFileName="cleanedResults.csv"):
    print("Commencing filtering operations of cleanedResults.csv...")
    df = filterCleanedResultsByDiscipline(targetFileName=targetFileName)
    df = filterCleanedResultsByNamelist(df)
    generateFinalFilteredXlsx(df)


def parseScriptArguments():
    description = "This is a python script to automate data collection and cleaning of World Athletics results retrieved from World Athletics website's backend API."
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-ath", "--Athlete", help="Define Athlete for Search")
    parser.add_argument("-disc", "--Discipline", help="Define Discipline for Search")
    parser.add_argument("-o", "--OutputName", help="Define Output file name of Scrapped Results (without '.xlsx' extension)")
    parser.add_argument("-tf", "--TargetFileName",
                        help="Target File Name (default is cleanedResults.csv) for performing filtering operations on using namelist.csv and discipline supplied")
    parser.add_argument("-filteronly", "--FilterOnly", action='store_true',
                        help="Filter existing cleanedResults.csv by discipline specified. Scrapping will not be performed prior.")
    parser.add_argument("-scrapeonly", "--ScrapeOnly", action='store_true',
                        help="Scape only. Will not perform filtering by discipline or namelist.csv.")
    args = parser.parse_args()

    global search_athleteName
    global search_discipline
    search_athleteName = ""
    search_discipline = ""

    if args.Athlete or args.Discipline:
        search_athleteName = args.Athlete
        search_discipline = args.Discipline
        print("Athlete to search for: {0}. Discipline: {1}".format(search_athleteName, search_discipline))
        getResultsOfSelectedAthleteFromSearch(query=search_athleteName, discipline=search_discipline)
        cleanResults(targetFileName="searchResults.csv", sheet_name="searchResults", outputFileName="searchResultsCleaned.csv")
    elif args.FilterOnly:
        if args.TargetFileName:
            filterResults(targetFileName=args.TargetFileName)
        else:
            filterResults()
    elif args.ScrapeOnly:
        fetchResults()
        compileResults()
        cleanResults()
    else:
        fetchResults()
        compileResults()
        cleanResults()
        filterResults()

    return


def main():
    parseScriptArguments()


if __name__ == "__main__":
    main()
