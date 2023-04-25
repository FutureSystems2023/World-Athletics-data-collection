filename = "test.xlsx"

# Define Countries to get results from
countries_list = [
    "Singapore",
    "Philippines",
    # "Malaysia",
    # "Vietnam",
    # "Indonesia",
    # "Thailand",
    # "Myanmar"
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