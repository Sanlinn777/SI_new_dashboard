import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import streamlit as st 
import seaborn as sns

st.set_page_config(page_title="Scheme I referral", page_icon=":bar_chart:", layout="wide")

@st.cache_data # Cache the data to improve performance
def load_data():
   # Load the data
    df = pd.read_excel("SI ver2023_START FROM 2019.xlsx","Data Entry")
    # Drop rows where 'year' is NaN
    df.dropna(subset=['YEAR'], inplace=True)
    # Rename columns
    df.rename(columns={'Quarter\n\nChoose from Drop Down List':'Qtr','Reporting month\n\nChoose from Drop Down List':'Month',
                      'State/ Region\n\nChoose from Drop Down List':'StatesRegions','DISTRICT FORMULA':'District',
                      'Township\n\nChoose from Drop Down List':'Tsp','Name of Private Practitioners and Clinic\n\nType Dr.{space}NAME as priority':'GP',
                     'Age\n\nFill completed age':'Age','Reach to TB Center\n\nChoose from Drop Down List':'ReachToTBCenter',
                      'Feedback\n\nChoose from Drop Down List':'Feedback', 'TB site\n\nChoose from Drop Down List':'TBsite',
                      'Bacteriological test\n\nChoose from Drop Down List':'Bacteriological','Sex\n\nChoose from Drop Down List':'Sex',
                      'Date formula':'Date'},inplace=True)

    #Another Way of Clean and rename columns
    #df.columns = df.columns.str.split('\n').str[0].str.lower().str.replace(' ', '_')

    #Remove unnecessary column
    df.drop(['GP','Remark'], axis= 1, inplace=True)
    # Convert Year to Int
    df['YEAR'] = df['YEAR'].astype(int)
     # Convert 'date' to datetime
    df['Date'] = pd.to_datetime(df['Date'])
    # Data transformations
    df['Sex'].replace('f','F', inplace = True)
    df['TBsite'].replace('Ep','EP', inplace = True)
    df['TBsite'].replace('p','P', inplace = True)
    df['ReachToTBCenter'].replace('y','Y', inplace = True)
    df['Sex'].replace('F','Female', inplace = True)
    df['Sex'].replace('M','Male', inplace = True)
    df['ReachToTBCenter'].replace('Y','Successful_Referral', inplace = True)
    df['ReachToTBCenter'].replace('N','Dropout', inplace = True)
    df['Feedback'].replace('N_TB','Non_TB', inplace = True)
    df['TBsite'].replace('P','Pulmonary', inplace = True)
    df['TBsite'].replace('EP','Extrapulmonary', inplace = True)
    df['Bacteriological'].replace('B','Bact_confirm', inplace = True)
    df['Bacteriological'].replace('C','Clinical_Dx', inplace = True)

    return df

df_si = load_data()

#st.header("Before Filtered")
#st.write(df_si)

# ---- SIDEBAR ----
st.sidebar.header("Please Filter Here:")

df_sr_sort= df_si.sort_values('StatesRegions', ascending= True)

State = st.sidebar.multiselect(
    "Select the State & Region:",
   options=df_sr_sort["StatesRegions"].unique(),
    default= ['Yangon'])

df_tsp_sort = df_si.query( "StatesRegions == @State").sort_values('Tsp', ascending= True)

Township = st.sidebar.multiselect(
    "Select the Township:",
   options= df_tsp_sort["Tsp"].unique(),
    default= df_tsp_sort["Tsp"].unique())

Year = st.sidebar.multiselect(
    "Select the Year:",
   options=df_si["YEAR"].unique(),
    default= df_si["YEAR"].unique())

selected_age = st.sidebar.slider(
    "Select the Age Range:",
    min_value=int(df_si["Age"].min()),
    max_value=int(df_si["Age"].max()),
    value=(int(df_si["Age"].min()), int(df_si["Age"].max())))

selected_sex = st.sidebar.multiselect(
    "Select the Gender:",
    options=df_si["Sex"].unique(),
    default=['Male','Female'])

# Apply filter
df_si = df_si.query( "StatesRegions == @State & Tsp == @Township & YEAR == @Year & Age >= @selected_age[0] & Age <= @selected_age[1] & Sex in @selected_sex"
)


# ---- MAINPAGE ----
st.title(":bar_chart: Scheme 1 Referral")
st.markdown("##")

# Display DataFrame or a message if empty
if df_si.empty:
    st.write('DataFrame is empty!')
    # total_sales = 0
else:
    total_referral = df_si["YEAR"].count()
    st.subheader ('Total Patient Referral: ')
    st.subheader (f"{total_referral}")

    # States and Region Data Frame
    df_new = (df_si.groupby(by = ['StatesRegions'], as_index= False)[['YEAR']].count())
    df_new = df_new.sort_values('YEAR', ascending= False)

    colors=['red', 'black', 'green', 'blue', 'yellow', 'cyan', 'orange', 'grey', 'purple','magenta', 'teal','turquoise', 'violet','pink', 'brown', 'indigo','aqua']

    # States and Regions Bar Plot
    fig_SR, ax = plt.subplots()
    sns.barplot(x=df_new['StatesRegions'], y=df_new['YEAR'], ax=ax, palette=colors)  # Updated column names
    ax.set_xlabel('State and Region')
    ax.set_ylabel('Total Referral')
    ax.set_title('Total Referral of States and Regions')
    plt.xticks(rotation=90)
    st.pyplot(fig_SR)

    #Tsps Data Frame
    df_tsp= df_si.groupby(['Tsp'], as_index= False).agg({'YEAR':'count'})  # Updated column name
    df_tsp = df_tsp.sort_values('YEAR', ascending= False)
    df_tsp.rename(columns={'YEAR':'Total Referral'},inplace=True)

    st.subheader('Township with Highest Referral')
    st.write(df_tsp)

    #Tsps Bar Plot
    fig_tsp, ax = plt.subplots(figsize=(30, 10))
    sns.barplot(x=df_tsp['Tsp'], y=df_tsp['Total Referral'], ax= ax)
    ax.set_xlabel('Townships')
    ax.set_ylabel('Total Referral')
    ax.set_title('Township-wise Referral')
    plt.xticks(rotation=90)
    st.pyplot(fig_tsp)

   
    
    #Sex Classification in Each State and Regions Data Frame
    sex_count_by_region = df_si.groupby(['StatesRegions', 'Sex']).size().reset_index(name='patient_count')
    
    color_map = {'Male': 'blue', 'Female': 'yellow'}

    #Sex Classification in Each State and Regions Gropued Bar Chart
    fig_gender_in_SR = px.bar(sex_count_by_region, x='StatesRegions', y='patient_count', color='Sex', 
             barmode='group', 
             title='Counts of Male and Female Patients in Each State/Region',
             labels={'patient_count': 'Patient Count', 'StatesRegions': 'State and Region', 'Sex': 'Gender'},
             color_discrete_map=color_map)
    st.plotly_chart(fig_gender_in_SR, use_container_width= True)

    #Sex Based Data Frame
    df_sex= df_si.groupby(['Sex'], as_index= False).agg({'YEAR':'count'})

    #Sex Based Pie Plot
    fig_sex, ax= plt.subplots()
    plt.pie(df_sex['YEAR'], labels = df_sex['Sex'], autopct='%.0f' )
    ax.set_title('Gender')

    #Successful Referral Data Frame
    df_referral= df_si.groupby(['ReachToTBCenter'], as_index= False).agg({'YEAR':'count'})

    #Successful Referral Pie Plot
    fig_referral, ax= plt.subplots()
    plt.pie(df_referral['YEAR'], labels = df_referral['ReachToTBCenter'], autopct='%.0f' )
    ax.set_title('Successful Referral')

    #TB Data Frame
    df_TB= df_si.groupby(['Feedback'], as_index= False).agg({'YEAR':'count'})

    #TB Pie Plot
    fig_TB, ax= plt.subplots()
    plt.pie(df_TB['YEAR'], labels = df_TB['Feedback'], autopct='%.0f' )
    ax.set_title('TB Occurence')
    

    #TB Site Data Frame
    df_tbsite= df_si.groupby(['TBsite'], as_index= False).agg({'YEAR':'count'})

    explodes = (0.1, 0.3)

    #TB Site Pie Plot
    fig_tbsite, ax= plt.subplots()
    plt.pie(df_tbsite['YEAR'], explode= explodes, labels = df_tbsite['TBsite'] )
    ax.set_title('Site of TB')
    

    #TB Type Data Frame
    df_TBtype= df_si.groupby(['Bacteriological'], as_index= False).agg({'YEAR':'count'})
    
    #TB Type Pie Plot
    fig_tbtype, ax = plt.subplots()
    plt.pie(df_TBtype['YEAR'], labels = df_TBtype['Bacteriological'], autopct='%.0f' )
    ax. set_title('Type of TB')

    

    # Two Columns
    left_column, right_column = st.columns(2)
    left_column.pyplot(fig_sex, use_container_width=True)
    right_column.pyplot(fig_referral, use_container_width=True)
    left_column.pyplot(fig_TB, use_container_width=True)
    right_column.pyplot(fig_tbsite, use_container_width=True)
    right_column.pyplot(fig_tbtype, use_container_width=True)

    

    
    #Timeline Data Frame
    df_timeline= df_si.groupby(['Year_Qtr'], as_index= False).agg({'YEAR':'count'})

    #Timeline Trend
    fig_trend, ax = plt.subplots(figsize=(20,10))
    plt.plot(df_timeline['Year_Qtr'], df_timeline['YEAR'])
    ax.set_xlabel('Quarter')
    ax.set_ylabel('Total Referral')
    ax.set_title('Quarterly Referral Patients')
    plt.xticks(rotation=90)
    st.pyplot(fig_trend)





        





 
