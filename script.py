import pandas as pd
import requests as re
import config
import json
import argparse
import sys
import warnings
import datetime as dt
import shutil
import os
import numpy as np

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
            exit()


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


def getCompetitorResultsByDiscipline(AthleteID=None, resultsByYearOrderBy=None, resultsByYear=None, disciplineCode=None):
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
    #Filter by disciplineCode (necessary when athlete has multiple disciplines, results scrapped will be duplicated)
    if disciplineCode:
        for disciplineIndex in range(len(resultsByEvent)):
            if resultsByEvent[disciplineIndex]['disciplineCode'] == disciplineCode:
                df_results = pd.DataFrame.from_dict(resultsByEvent[disciplineIndex]['results'])
                df_results['discipline'] = resultsByEvent[disciplineIndex]['discipline']
                df = pd.concat([df, df_results])
                break
    else:
        for disciplineIndex in range(len(resultsByEvent)):
            df_results = pd.DataFrame.from_dict(resultsByEvent[disciplineIndex]['results'])
            df_results['discipline'] = resultsByEvent[disciplineIndex]['discipline']
            df = pd.concat([df, df_results])
    return df


def getCountryAthletesResults(countryCode="SGP", resultsYear=None, disciplineCode=None, gender=None):
    if countryCode == "NOT FOUND" or len(countryCode) != 3:
        return pd.DataFrame(["countryCode " + countryCode], )
    if resultsYear == None:
        resultsYear = 2023
    df = pd.DataFrame()
    if disciplineCode != None:
        df_Athletes = searchCompetitor(countryCode=countryCode, disciplineCode=disciplineCode, gender=gender)
    else:
        df_Athletes = searchCompetitor(countryCode=countryCode, gender=gender)
    athletesCount = len(df_Athletes)
    print("API fetched", athletesCount, "athletes for", countryCode)
    athleteActiveInYearCount = 0
    if athletesCount == 0:
        return df
    for i, athleteID in df_Athletes['aaAthleteId'].items():
        try:
            df_result = getCompetitorResultsByDiscipline(AthleteID=athleteID, resultsByYear=resultsYear, disciplineCode=disciplineCode)
            df_result['athlete_name'] = " ".join([df_Athletes['givenName'][i], df_Athletes['familyName'][i]])
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


def reverseCountryCoding(countryCode):
    f = open('countryCodes.json')
    data = json.load(f)
    for i in range(len(data['countryCodes'])):
        if data['countryCodes'][i]['code'].upper() == countryCode.upper():
            return data['countryCodes'][i]['name']
    print("Country Name not found. Check Country Name.")
    return "NOT FOUND"


def progressBar(count_value, total, suffix=''):
    bar_length = 100
    if total == 0:
        filled_up_Length = 1
        total = 1
    else:
        filled_up_Length = int(round(bar_length * count_value / float(total)))
    percentage = round(100.0 * count_value/float(total), 1)
    bar = '=' * filled_up_Length + '-' * (bar_length - filled_up_Length)
    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percentage, '%', suffix))
    sys.stdout.flush()
    return


def fetchResults(countries_list=config.countries_list, years_list=config.years_list, disciplines_list=config.disciplines_list, gender=config.gender):
    print("Your arguments are: \nCountries=", countries_list, "\nYears=",
          years_list, "\nDisciplines=", disciplines_list, "\nGender=", gender)

    try:
        writer = pd.ExcelWriter(path=config.scrappedRawFileName, engine='openpyxl')
    except PermissionError:
        print("Unable to write to {}. Please ensure file is closed before running the script.".format(config.scrappedRawFileName))
        return
    except Exception as e:
        print(e)
        return

    for country in countries_list:
        df = pd.DataFrame()
        for year in years_list:
            for discipline in disciplines_list:
                df = pd.concat([df, getCountryAthletesResults(countryCode=getCountryCode(
                    countryName=country), resultsYear=year, disciplineCode=getDisciplineCode(discipline), gender=gender)])
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


def sortResultsMarkFromSmallestToLargest(resultsFileName):
    df = pd.read_csv(resultsFileName)
    df.sort_values(['athlete_name', 'mark', 'discipline'], ascending=[True, True, True], inplace=True)
    df.to_csv(resultsFileName, index=False)
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
        if df['mark'].dtype != np.float64:
            #Replace dpts with 'h' to 0. Convert dpts to numeric, if error replace with NAN. Lastly, Convert dpts to seconds. 
            df['mark'] = df['mark'].astype(str).str.replace('h', '0', regex=False)
            df['mark'] = df['mark'].apply(lambda x: pd.to_numeric(x, errors='coerce'))
            df_strRemoved = df[df['mark'].notna()]
            df_strRemoved['mark'] = df_strRemoved['mark'].apply(lambda x: convertStrToSeconds(x))
            df_strRemoved.to_csv(outputFileName, index=False)
        else:
            df.to_csv(outputFileName, index=False)
        sortResultsMarkFromSmallestToLargest(resultsFileName=outputFileName)
        print("Results cleaned successfully and saved as", outputFileName)
    except Exception as e:
        print(e)
        exit()
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


def getResultsOfSelectedAthleteFromSearch(query="", discipline="", toCSV=True):
    df = pd.DataFrame()
    if discipline:
        discipline = getDisciplineCode(disciplineName=discipline)
    df_searchedResults = searchCompetitor(query=query, disciplineCode=discipline)
    print("The API found the following athletes matching your query.")
    print(df_searchedResults[["aaAthleteId", "givenName", "familyName", "country"]])
    selection = input(
        "Please input index of athlete to include in scrapping (enter all for selecting all athletes from search results or enter skip to skip the current search query):")
    if selection.lower() != "all" and selection.isnumeric() == True:
        selected_index = int(selection)
        selected_aaAthleteId = df_searchedResults.iloc[selected_index]['aaAthleteId']
        print(" ".join(["Selected:", df_searchedResults.iloc[selected_index]
              ['givenName'], df_searchedResults.iloc[selected_index]['familyName'], "(" + selected_aaAthleteId + ").", "Commencing API Fetch..."]))
        for year in config.years_list:
            try:
                df_result = getCompetitorResultsByDiscipline(AthleteID=selected_aaAthleteId, resultsByYear=year)
                df_result['athlete_name'] = " ".join(
                    [df_searchedResults['givenName'][selected_index], df_searchedResults['familyName'][selected_index]])
                df_result['athlete_id'] = selected_aaAthleteId
                df_result['athlete_countryCode'] = df_searchedResults['country'][selected_index]
                df_result['athlete_country'] = reverseCountryCoding(countryCode=df_searchedResults['country'][selected_index])
                df = pd.concat([df, df_result])
            except:
                print(" ".join(["Results for", df_searchedResults['givenName']
                      [selected_index], "(" + selected_aaAthleteId + "):", df_result]))
        print(df)
    elif selection.lower() == "skip":
        print("Skipping this search query ({0})...".format(query))
        return df
    else:
        print("Selected all athletes from search results.")
        for i, athleteID in df_searchedResults['aaAthleteId'].items():
            for year in config.years_list:
                try:
                    df_result = getCompetitorResultsByDiscipline(AthleteID=athleteID, resultsByYear=year)
                    df_result['athlete_name'] = " ".join([df_searchedResults['givenName'][i], df_searchedResults['familyName'][i]])
                    df_result['athlete_id'] = selected_aaAthleteId
                    df_result['athlete_countryCode'] = df_searchedResults['country'][i]
                    df_result['athlete_country'] = reverseCountryCoding(countryCode=df_searchedResults['country'][i])
                    df = pd.concat([df, df_result])
                except:
                    print(" ".join(["Results for", df_searchedResults['givenName'][i], "(" + athleteID + "):", df_result]))
        print(df)
    if toCSV:
        try:
            df.to_csv("searchResults.csv", index=False)
            print("Saved results to searchResults.csv")
        except Exception as e:
            print(e)
    else:
        return df
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
def filterCleanedResultsByNamelist(df, namelistCSV=config.namelistFileName):
    print("Filtering results by names provided in {0} next...".format(namelistCSV))
    try:
        df_filtered = pd.DataFrame(columns=df.columns)
        df_namelist = pd.read_csv(namelistCSV)
        for i in range(len(df_namelist)):
            df_filtered = pd.concat([df_filtered, df[df['athlete_name'] == df_namelist.iloc[i, 0]]])
        print("Filtering operations by namelist finished successfully (before rows: {0}, rows left: {1}).".format(
            len(df), len(df_filtered)))
        return df_filtered
    except Exception as e:
        print(e)
        exit()


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


def filterResults(targetFileName="cleanedResults.csv", namelistCSV=config.namelistFileName):
    print("Commencing filtering operations of {0} using namelist ({1})...".format(targetFileName, namelistCSV))
    df = filterCleanedResultsByDiscipline(targetFileName=targetFileName)
    df = filterCleanedResultsByNamelist(df, namelistCSV=namelistCSV)
    generateFinalFilteredXlsx(df)


def compileIntoFolder(folderName=config.compiledFolderName, namelistCSV=config.namelistFileName):
    print("Compiling output to folder '{0}'...".format(folderName))
    if not os.path.exists(os.path.join(os.getcwd(), folderName)):
        os.mkdir(os.path.join(os.getcwd(), folderName))
    shutil.move(os.path.join(os.getcwd(), namelistCSV), os.path.join(os.getcwd(), folderName, namelistCSV))
    shutil.move(os.path.join(os.getcwd(), config.finalFilteredCleanedFileName),
                os.path.join(os.getcwd(), folderName, config.finalFilteredCleanedFileName))
    return


def appendSeachResultsToCleanedResultsCSV():
    print("Appending seach results to cleanedResults.csv...")
    df_cleanedResults = pd.read_csv("cleanedResults.csv")
    df_searchResults = pd.read_csv("searchResultsCleaned.csv")
    df = pd.concat([df_cleanedResults, df_searchResults])
    df.to_csv("cleanedResults.csv", index=False)
    return


def searchOperation(**kwargs):
    if kwargs['athlete'] or kwargs['discipline']:
        search_athleteName = kwargs['athlete']
        search_discipline = kwargs['discipline']
        print("Athlete to search for: {0}. Discipline: {1}".format(search_athleteName, search_discipline))
        getResultsOfSelectedAthleteFromSearch(query=search_athleteName, discipline=search_discipline)
        cleanResults(targetFileName="searchResults.csv", sheet_name="searchResults", outputFileName="searchResultsCleaned.csv")
        if kwargs['append']:
            appendSeachResultsToCleanedResultsCSV()
    elif kwargs['athleteCSV']:
        try:
            df_athleteCSV = pd.read_csv(kwargs['athleteCSV'])
            df_search = pd.DataFrame()
            for i, search_athleteName in enumerate(df_athleteCSV.iloc[:, 0]):
                print("Searching {0} of {1} athletes specified. Search term: {2}".format(i, len(df_athleteCSV), search_athleteName))
                df_search = pd.concat([df_search, getResultsOfSelectedAthleteFromSearch(query=search_athleteName, toCSV=False)])
            df_search.to_csv("searchResults.csv", index=False)
            cleanResults(targetFileName="searchResults.csv", sheet_name="searchResults", outputFileName="searchResultsCleaned.csv")
        except Exception as e:
            print(e)
            exit()
    return


def scrapeOnlyOperation(**kwargs):
    '''
    if kwargs['discipline']:
        fetchResults()
        compileResults()
        cleanResults()
    else:
    '''
    fetchResults()
    compileResults()
    cleanResults()
    return


def filterOnlyOperation(**kwargs):
    if kwargs['targetFileName']:
        if kwargs['namelistCSV']:
            filterResults(targetFileName=kwargs['targetFileName'], namelistCSV=kwargs['namelistCSV'])
        else:
            if os.path.isfile(os.path.join(os.getcwd(), kwargs['targetFileName'][:-4] + " namelist.csv")):
                filterResults(targetFileName=kwargs['targetFileName'], namelistCSV=kwargs['targetFileName'][:-4] + " namelist.csv")
            else:
                filterResults(targetFileName=kwargs['targetFileName'])
    else:
        if kwargs['namelistCSV']:
            filterResults(namelistCSV=kwargs['namelistCSV'])
        else:
            filterResults()
    if kwargs['compileIntoFolder']:
        if kwargs['namelistCSV'] and kwargs['namelistCSV'][len(kwargs['namelistCSV'])-12:] == "namelist.csv":
            compileIntoFolder(folderName=kwargs['namelistCSV'][:-13], namelistCSV=kwargs['namelistCSV'])
        else:
            compileIntoFolder()
    return


def normalOperation(**kwargs):
    fetchResults()
    compileResults()
    cleanResults()
    filterResults()
    if kwargs['compileIntoFolder']:
        if kwargs['namelistCSV'] and kwargs['namelistCSV'][:-12] == "namelist.csv":
            compileIntoFolder(folderName=kwargs['namelistCSV'][:-13], namelistCSV=kwargs['namelistCSV'])
        else:
            compileIntoFolder()
    return


def parseScriptArguments():
    description = "This is a python script to automate data collection and cleaning of World Athletics results retrieved from World Athletics website's backend API."
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-ath", "--Athlete", help="Define Athlete for Search")
    parser.add_argument("-disc", "--Discipline", help="Define Discipline for Search")
    parser.add_argument("-o", "--OutputName", help="Define Output file name of Scrapped Results (without '.xlsx' extension)")
    parser.add_argument("-tf", "--TargetFileName",
                        help="Target File Name (default is cleanedResults.csv) for performing filtering operations on using namelist.csv and discipline supplied. Please include '.csv' extension in argument.")
    parser.add_argument("-nl", "--NameListCSV",
                        help="Name List CSV file (default is namelist.csv) that will be used for performing filtering operations on cleaned results data. Please include '.csv' extension in argument and ensure '* namelist.csv' naming convention.")
    parser.add_argument("-c", "--CompileIntoFolder", action='store_true',
                        help="Compile filtered namelist CSV and filtered data into a folder specified by user. Please ensure argument is a legal folder name.")
    parser.add_argument("-cleanonly", "--CleanOnly", action='store_true',
                        help="Clean existing scrappedRawResults.xlsx and output into cleanedResults.csv.")
    parser.add_argument("-filteronly", "--FilterOnly", action='store_true',
                        help="Filter existing cleanedResults.csv by discipline specified. Scrapping will not be performed prior.")
    parser.add_argument("-scrapeonly", "--ScrapeOnly", action='store_true',
                        help="Scape and clean data only. Will not perform filtering by discipline or namelist.csv.")
    parser.add_argument("-search", "--SearchAthlete", action='store_true',
                        help="Search athlete using API and return results as searchResults.csv.")
    parser.add_argument("-append", "--AppendToCleanedResults", action='store_true',
                        help="Append search results to cleanedResults.csv.")
    parser.add_argument("-athCSV", "--AthleteCSV", help="Define Athlete CSV file for searches.")
    args = parser.parse_args()

    global search_athleteName
    global search_discipline
    search_athleteName = ""
    search_discipline = ""

    if args.SearchAthlete:
        searchOperation(athlete=args.Athlete, discipline=args.Discipline, append=args.AppendToCleanedResults, athleteCSV=args.AthleteCSV)
    elif args.CleanOnly:
        cleanResults()
    elif args.FilterOnly:
        filterOnlyOperation(targetFileName=args.TargetFileName, namelistCSV=args.NameListCSV, compileIntoFolder=args.CompileIntoFolder)
    elif args.ScrapeOnly:
        scrapeOnlyOperation(discipline=args.Discipline)
    else:
        normalOperation(compileIntoFolder=args.CompileIntoFolder, namelistCSV=args.NameListCSV)
    return


def main():
    parseScriptArguments()
    print("Script ran successfully.")


if __name__ == "__main__":
    main()
