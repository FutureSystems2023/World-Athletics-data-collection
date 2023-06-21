import streamlit as st
import time
import json
import pandas as pd
import subprocess
import script
import sys

st.header("This site scrapes data from: https://worldathletics.org/")

def read_json_file(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)
    return data

def countryCodes():
    file_path = "countryCodes.json"
    json_data = read_json_file(file_path)
    df = pd.DataFrame(json_data)
    country_names = df['countryCodes'].apply(lambda x: x['name'])
    countrycodes = country_names.tolist()
    return countrycodes

def disciplineCodes():
    file_path = "disciplineCodes.json"
    json_data = read_json_file(file_path)
    df_disciplinecodes = pd.DataFrame(json_data)
    disciplineCodes = df_disciplinecodes['disciplineCodes'].apply(lambda x: x['name'])
    disciplinecodes = disciplineCodes.tolist()
    return disciplinecodes

# To write the config file that takes in the Countrycodes and Disciplinecodes
def write_config_file(options, options2):
    filename = 'config.py'
    with open(filename, "w") as file:
        file.write(
            '''import time
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
disciplines_list = ''')
        json.dump(options2, file)

        file.write("\n")
        file.write('''
# Define Countries to get results from
countries_list =''')
        json.dump(options, file)

        file.write("\n")
        file.write('''
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
    """'''

        )
# To create the csv file for namelist
def create_csv_file(data, filename):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)

# To run script.py
def run_script():
    command = [sys.executable, "script.py"]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

    while True:
        output = process.stdout.readline()
        if output == "" and process.poll() is not None:
            break
        if output:
            st.code(output.strip())

def main():
    st.title("Script Execution")

    run_button = st.button("Run Script")
    if run_button:
        st.text("Running script...")
        run_script()
        st.text("Script execution completed.")

def namelistcall():
    st.write("Key in the athelete name, format follow as per website")
    namelist = pd.DataFrame(
        [
            {"athlete_names": ""},
        ]
    )
    edited_df = st.data_editor(namelist, num_rows="dynamic") # 👈 An editable dataframe

genre = st.radio(
"Step1: With or Without namelist",
('With', 'Without'))

with st.form("To write config.py"):
    options = st.multiselect(
        'Step2: Select the country(ies)',
        countryCodes()
    )

    options2 = st.multiselect(
        'Step3: Select the discipline(s)',
        disciplineCodes()
    )

    # st.write('Step3: Key in the athelete name, format follow as per website')
    # agree = st.checkbox("With namelist", on_change = namelistcall())

    # genre = st.radio(
    # "Step3: With or Without namelist",
    # ('With', 'Without'))

    if genre == "With":
        st.write("Key in the athelete name, format follow as per website")
        namelist = pd.DataFrame(
            [
                {"athlete_names": ""},
            ]
        )
        edited_df = st.data_editor(namelist, num_rows="dynamic") # 👈 An editable dataframe
    

    # To write the config.py
    submitted = st.form_submit_button("Submit")
    if submitted:
        create_csv_file(edited_df, "namelist.csv")
        st.write('Countries', options, 'Disciplines', options2)
        write_config_file(options, options2)
        st.write(edited_df)




if __name__ == "__main__":
    main()


