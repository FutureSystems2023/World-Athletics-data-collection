import time
now = time.strftime("%H%M%S", time.localtime())

# filename = now + ".xlsx"
scrappedRawFileName = "scrappedRawResults.xlsx"

# filename = "finalFilteredCleanedResults_" + now + ".xlsx"
finalFilteredCleanedFileName = "finalFilteredCleanedResults.xlsx"

# This file will be used For filtering names from scrapped cleaned data.
namelistFileName = "namelist.csv"

# This is where all files will be compiled to if compiled switch was provided as CLI argument.
compiledFolderName = "Filtered"

# Define disciplines to scrape
disciplines_list = [
    "100 Metres",
    "Pole Vault",
    "200 Metres",
    "1500 Metres"
]

# Define Countries to get results from
countries_list = [
    "Singapore",
    "Philippines",
    "Malaysia",
    "Vietnam",
    "Indonesia",
    "Thailand",
    "Myanmar",
    "Cambodia",
    "Laos",
    "Brunei",
    "Timor Leste",
]

# Define which years to get results for
years_list = [
    2019,
    2020,
    2021,
    2022,
    2023,
]


# Define searchCompetitor GraphQL Query here
searchCompetitorQuery = """
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


# Define getCompetitorResultsByDiscipline GraphQL Query here
getCompetitorResultsByDiscipline = """
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
