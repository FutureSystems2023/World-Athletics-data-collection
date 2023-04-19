import pandas as pd
import requests as re
from requests.auth import HTTPBasicAuth
import os
import urllib.parse
import json

class API:
    
    apiEndPoint = "https://jpvxtz2frzayfix6m7whizuccm.appsync-api.eu-west-1.amazonaws.com/graphql"
    apiKey = "da2-ii5irlhy7fd57aptsgby37bt3e"
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
        

def searchCompetitor(query = None, gender = None, disciplineCode = None, environment = None, countryCode = None):
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
        "query":query,
        "gender":gender,
        "disciplineCode":disciplineCode,
        "environment":environment,
        "countryCode":countryCode,
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
        "id":AthleteID,
        "resultsByYearOrderBy":resultsByYearOrderBy,
        "resultsByYear":resultsByYear
    }
     
    json_data = API(queryBody, queryVariables).fetch_data()
    resultsByEvent = json_data['data']['getSingleCompetitorResultsDiscipline']['resultsByEvent']
    df = pd.DataFrame()
    for discipline in range(len(resultsByEvent)):
        df_results = pd.DataFrame.from_dict(resultsByEvent[discipline]['results'])
        df_results['discipline'] = resultsByEvent[discipline]['discipline']
        df = pd.concat([df, df_results])
    return df


def getSingaporeAthletes():
    df = pd.DataFrame()
    df_Athletes = searchCompetitor(countryCode="SGP")
    for athleteID in df_Athletes['aaAthleteId']:
        print(athleteID)


def main():
    getSingaporeAthletes()
    df = getCompetitorResultsByDiscipline(AthleteID=14472153, resultsByYear=2022)
    df.to_excel("test.xlsx", sheet_name="RAW", engine='openpyxl', index=False)


if __name__ == "__main__":
    main()