import pandas as pd
import requests as re
import os
import urllib.parse
import json
import sys


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
    queryBody = """
    query SearchCompetitors($query: String, $gender: GenderType, $disciplineCode: String, $environment: String, $countryCode: String) {
        searchCompetitors(query: $query, gender: $gender, disciplineCode: $disciplineCode, environment: $environment, countryCode: $countryCode) {
            aaAthleteId
            familyName
            givenName
            birthDate
            disciplines
            iaafId
            gender
            country
            urlSlug
            __typename
            }
        }
    """
    queryVariables = {
        "query": query,
        "gender": gender,
        "disciplineCode": disciplineCode,
        "environment": environment,
        "countryCode": countryCode,
    }

    json_data = API(queryBody, queryVariables).fetch_data()
    df = pd.DataFrame.from_dict(json_data['data']['searchCompetitors'])
    return df


def getCompetitorResultsByDiscipline(AthleteID=None, resultsByYearOrderBy=None, resultsByYear=None):
    queryBody = """
    query ($id: Int, $resultsByYearOrderBy: String, $resultsByYear: Int) {
         getSingleCompetitorResultsDiscipline(id: $id, resultsByYear: $resultsByYear, resultsByYearOrderBy: $resultsByYearOrderBy) {    parameters {
                   resultsByYear
                   resultsByYearOrderBy
                   __typename
                   }
                   activeYears
                    resultsByEvent {
                        indoor
                        disciplineCode
                        disciplineNameUrlSlug
                        typeNameUrlSlug
                        discipline
                        withWind
                        results {
                            date
                            competition
                            venue
                            country        
                            category
                            race        
                            place        
                            mark       
                            wind     
                            notLegal      
                            resultScore      
                            remark 
                            __typename    
                            }      
                            __typename    
                        }    
                            __typename
        }
    }
    """

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
    return "NOT FOUND"


def getDisciplineCode(disciplineName=""):
    f = open('disciplineCodes.json')
    data = json.load(f)
    for i in range(len(data['disciplineCodes'])):
        if data['disciplineCodes'][i]['name'].lower().strip() == disciplineName.lower().strip():
            return data['disciplineCodes'][i]['code']
    return "NOT FOUND"


def progressBar(count_value, total, suffix=''):
    bar_length = 100
    filled_up_Length = int(round(bar_length * count_value / float(total)))
    percentage = round(100.0 * count_value/float(total), 1)
    bar = '=' * filled_up_Length + '-' * (bar_length - filled_up_Length)
    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percentage, '%', suffix))
    sys.stdout.flush()


def main():
    df = getCountryAthletesResults(countryCode=getCountryCode(countryName="askjdsand"))
    df.to_excel("test.xlsx", sheet_name="RAW", engine='openpyxl', index=False)


if __name__ == "__main__":
    main()