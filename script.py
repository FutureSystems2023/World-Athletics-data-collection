import pandas as pd
import requests as re
import config
import json
import sys
import openpyxl


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
        writer = pd.ExcelWriter(path=config.filename, engine='openpyxl')
    except PermissionError:
        print("Unable to write to {}. Please ensure file is closed before running the script.".format(config.filename))
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
    df = pd.concat(pd.read_excel(config.filename, sheet_name=None))
    writer = pd.ExcelWriter(path=config.filename, engine='openpyxl', mode='a')
    df.to_excel(writer, sheet_name='ALL_COUNTRIES', index=None)
    writer.close()
    return


# This function is for cleaning timings (instances where there is a random h in the timings and remove any "DNQ" and other strings etc.)
def cleanResults():
    df = pd.read_excel(config.filename, sheet_name="ALL_COUNTRIES")
    df['mark'] = df['mark'].str.replace('h', '0', regex=False)
    df_strRemoved = df[(df['mark'].str.contains('\d', regex=True))]
    df_strRemoved.to_csv("cleanedTest.csv", index=False)
    df_strRemoved['mark'] = df_strRemoved['mark'].apply(lambda x: convertStrToSeconds(x))
    df_strRemoved.to_csv("cleanedTest2.csv", index=False)
    return


def convertStrToSeconds(x):
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
    return seconds


def main():
    # fetchResults()
    # compileResults()
    cleanResults()


if __name__ == "__main__":
    main()
