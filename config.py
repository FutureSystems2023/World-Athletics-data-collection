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

# Define gender to scrape (female or male, leave blank to scrape both)
gender = "female"

# Define disciplines to scrape
disciplines_list = [
    "100 Metres",
    "200 Metres",
]
'''
disciplines_list = [
    "100 Metres",
    "200 Metres",
    "400 Metres",
    "800 Metres",
    "100 Metres Hurdles",
    "110 Metres Hurdles",
    "400 Metres Hurdles",
    "Pole Vault",
    "High Jump"
]
'''

# Define Countries to get results from
countries_list = [
    "Afghanistan",
    "Bangladesh",
    "Bhutan",
    "Bahrain",
    "Brunei",
    "Cambodia",
    "Dpr Of Korea",
    "Timor Leste",
    "Hong Kong, China",
    "Indonesia",
    "India",
    "Islamic Republic of Iran",
    "Iraq",
    "Jordan",
    "Japan",
    "Kazakhstan",
    "Kirghizistan",
    "Pr Of China",
    "Korea",
    "Saudi Arabia",
    "Kuwait",
    "Laos",
    "Lebanon",
    "Macao",
    "Malaysia",
    "Maldives",
    "Mongolia",
    "Myanmar",
    "Nepal",
    "Oman",
    "Pakistan",
    "Philippines",
    "Palestine",
    "Qatar",
    "Singapore",
    "Sri Lanka",
    "Syria",
    "Thailand",
    "Tajikistan",
    "Turkmenistan",
    "Chinese Taipei",
    "United Arab Emirates",
    "Uzbekistan",
    "Vietnam",
    "Republic Of Yemen"
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
