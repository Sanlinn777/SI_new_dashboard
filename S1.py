from ast import List
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import streamlit as st 
import seaborn as sns
from matplotlib.ticker import MaxNLocator

st.set_page_config(page_title="Scheme I referral", page_icon=":bow_and_arrow:", layout="wide")

#Def for Age Group Columns
def categorize_age_group(age):
    if age >= 0 and age < 5:
        return '0-4 yrs'
    elif age >=5 and age < 15:
        return '5-14 yrs'
    elif age >= 15 and age <= 60:
        return '15-60 yrs'
    else:
        return '> 60 yrs'
    
def categorize_age_group_detail(age):
    if age >= 0 and age < 5:
        return '0-4 yrs'
    elif age >=5 and age < 10:
        return '5-9 yrs'
    elif age >= 10 and age < 15:
        return '10-14 yrs'
    elif age >= 15 and age < 25:
        return '15-24 yrs'
    elif age >= 25 and age < 35:
        return '25-34 yrs'
    elif age >= 35 and age < 45:
        return '35-44 yrs'
    elif age >= 45 and age < 55:
        return '45-54 yrs'
    elif age >= 55 and age < 65:
        return '55-64 yrs'
    else:
        return '> 65 yrs'

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
                      'Date formula':'Date', 'Type of Referral\n\nChoose from Drop Down List':'Type_of_Referral'},inplace=True)

    #Another Way of Clean and rename columns
    #df.columns = df.columns.str.split('\n').str[0].str.lower().str.replace(' ', '_')

    #Remove unnecessary column
    df.drop(['GP','Remark', 'Referral Register No.'], axis= 1, inplace=True)
    # Convert Year to Int
    df['YEAR'] = df['YEAR'].astype(int)
     # Convert 'date' to datetime
    df['Date'] = pd.to_datetime(df['Date'])
    # Data transformations
    df['Type_of_Referral']= df['Type_of_Referral'].str.upper()
    df['Sex']= df['Sex'].str.upper()
    df['ReachToTBCenter']= df['ReachToTBCenter'].str.upper()
    df['Feedback']= df['Feedback'].str.upper()
    df['TBsite']= df['TBsite'].str.upper()
    df['Bacteriological']= df['Bacteriological'].str.upper()

    df['Sex'].replace('F','Female', inplace = True)
    df['Sex'].replace('M','Male', inplace = True)
    df['ReachToTBCenter'].replace('Y','Successful_Referral', inplace = True)
    df['ReachToTBCenter'].replace('N','Dropout', inplace = True)
    df['Feedback'].replace('N_TB','Non_TB', inplace = True)
    df['TBsite'].replace('P','Pulmonary', inplace = True)
    df['TBsite'].replace('EP','Extrapulmonary', inplace = True)
    df['Bacteriological'].replace('B','Bact_confirm', inplace = True)
    df['Bacteriological'].replace('C','Clinical_Dx', inplace = True)
    
    df['StatesRegions'].replace('NayPyitaw','Naypyitaw', inplace = True)   
    
    df['TB_cat']= df['TBsite']+" "+ df['Bacteriological']
    df['age_group'] = df['Age'].apply(categorize_age_group)
    df['age_group_detail'] = df['Age'].apply(categorize_age_group_detail)

    return df

df_si = load_data()


   
    




   
    


def child(age):
    if age >= 0 and age < 15:
        return 'child'
    
    else:
        return 'adult'
   
    
df_si['child'] = df_si['Age'].apply(child)

#st.header("Before Filtered")
#st.write(df_si)


# ---- SIDEBAR ----
def handle_all_selection(selection, options):
    if 'All' in selection:
        return options  # Returns all options if 'All' is selected
    return selection  # Otherwise, return the selection


df_sr_sort= df_si.sort_values('StatesRegions', ascending= True)

st.sidebar.header("Please Filter Here:")


Referral_Type = st.sidebar.multiselect(
    "Select the ReferraL Type:",
   options=df_si["Type_of_Referral"].unique(),
    default= ['SI'])


State_options = list(df_sr_sort["StatesRegions"].unique())
State = st.sidebar.multiselect(
    "Select the State & Region:",
   options=['All'] + State_options,
    default= ['Yangon'])

State = handle_all_selection(State, State_options)

df_tsp_sort = df_si.query( "StatesRegions == @State").sort_values('Tsp', ascending= True)


Township_options = list(df_tsp_sort["Tsp"].unique())
Township = st.sidebar.multiselect(
    "Select the Township:",
    options= ['All'] + Township_options,
    default= ['All'])

Township = handle_all_selection(Township, Township_options)


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
df_si = df_si.query( "Type_of_Referral == @Referral_Type & StatesRegions == @State & Tsp == @Township & YEAR == @Year & Age >= @selected_age[0] & Age <= @selected_age[1] & Sex in @selected_sex"
)


# ---- MAINPAGE ----
st.title(":bow_and_arrow: All Type of Scheme 1 Referral")
st.markdown("##")

# Display DataFrame or a message if empty
if df_si.empty:
    st.write('DataFrame is empty!')
    # total_sales = 0
else:
    total_referral = df_si["YEAR"].count()
    st.subheader ('Total Patient Referral: ')
    st.subheader (f"{total_referral}")

    
    #Yearly Data Frame
    df_yr_trend= df_si.groupby(['YEAR'], as_index= False).agg({'Tsp':'count'})

    #Yearly Trend
    fig_yr = px.line(df_yr_trend,x='YEAR',y='Tsp',title='Yearly Referral Patients')
    fig_yr.update_xaxes(tick0= 0,dtick = 1 )
    st.plotly_chart(fig_yr, use_container_width= True)

    #fig_yr_trend, ax = plt.subplots(figsize=(20,10))
    #plt.plot(df_yr_trend['YEAR'], df_yr_trend['Tsp'])
    #ax.set_xlabel('Year')
    #ax.set_ylabel('Total Referral')
    #ax.set_title('Yearly Referral Patients')
    #ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    #plt.xticks(rotation=90)
    #st.pyplot(fig_yr_trend)


    #Quarter Data Frame
    df_timeline= df_si.groupby(['Qtr'], as_index= False).agg({'YEAR':'count'})

    #Quarterly Trend
    fig_trend = px.line(df_timeline, x='Qtr',y='YEAR',title='Quarterly Referral Patients', 
                        labels={'YEAR':'Patients'})
    st.plotly_chart(fig_trend,use_container_width= True)

    #fig_trend, ax = plt.subplots(figsize=(20,10))
    #plt.plot(df_timeline['Qtr'], df_timeline['YEAR'])
    #ax.set_xlabel('Quarter')
    #ax.set_ylabel('Total Referral')
    #ax.set_title('Quarterly Referral Patients')
    #plt.xticks(rotation=90)
    #st.pyplot(fig_trend)
    
    # States and Region Data Frame
    df_new = (df_si.groupby(by = ['StatesRegions'], as_index= False)[['YEAR']].count())
    df_new = df_new.sort_values('YEAR', ascending= False)

    colors=['red', 'black', 'green', 'blue', 'yellow', 'cyan', 'orange', 'grey', 'purple','magenta', 'teal','turquoise', 'violet','pink', 'brown', 'indigo','aqua']

    # States and Regions Bar Plot
    fig_SR=  px.bar(df_new,x = 'StatesRegions', y= 'YEAR', labels={'YEAR':'Patients'},
                        title='Total Referral of States and Regions', color='StatesRegions', 
                             color_discrete_sequence=px.colors.diverging.balance)
    fig_SR.update_layout(showlegend=False)

    st.plotly_chart(fig_SR, use_container_width= True)

    #Tsps Data Frame
    df_tsp= df_si.groupby(['Tsp'], as_index= False).agg({'YEAR':'count'}).sort_values(
        'YEAR', ascending= False)  # Updated column name
    df_tsp.insert(0, 'Serial No', range(1, 1 + len(df_tsp)))
    df_tsp.rename(columns={'YEAR':'Total Referral'},inplace=True)

    st.subheader('Township with Highest Referral')
    st.dataframe(df_tsp, hide_index=True, use_container_width= True)
    

    #Tsps Bar Plot
    fig_tsp = px.bar(df_tsp,x = 'Tsp', y= 'Total Referral',
                        title='Township-wise Referral', color='Tsp', 
                             color_discrete_sequence=px.colors.qualitative.Alphabet)
    fig_tsp.update_layout(showlegend=False)

    st.plotly_chart(fig_tsp, use_container_width= True)

   
    
    #Sex Classification in Each State and Regions Data Frame
    sex_count_by_region = df_si.groupby(['StatesRegions', 'Sex']).size().reset_index(name='patient_count')
    
    color_map = {'Male': 'blue', 'Female': 'yellow'}

    #Sex Classification in Each State and Regions Gropued Bar Chart
    fig_gender_in_SR = px.bar(sex_count_by_region, x='StatesRegions', y='patient_count', color='Sex', 
             barmode='group', 
             title='Counts of Male and Female Patients in Each State/Region',
             labels={'patient_count': 'Patient Count', 'StatesRegions': 'State and Region', 'Sex': 'Gender'},
             color_discrete_map=color_map)
    fig_gender_in_SR.update_layout(showlegend=False)

    #st.plotly_chart(fig_gender_in_SR, use_container_width= True)

    #Sex Based Data Frame
    df_sex= df_si.groupby(['Sex'], as_index= False).agg({'YEAR':'count'})

    #Sex Based Pie Plot
    colors= {'Male':'blue','Female':'orange'}
    fig_sex = px.pie(df_sex, names= 'Sex',values='YEAR',labels={'YEAR':'Patients'},
                            title='Gender of the Referral Patients',
                    color= 'Sex',color_discrete_map= colors)
    
    st.plotly_chart(fig_sex,use_container_width= True)

    #Age Group Dataframes
    df_child= df_si.groupby(['child'], as_index= False).agg({'YEAR':'count'})

    df_age_group= df_si.groupby(['age_group'], as_index= False).agg({'YEAR':'count'})

    df_age_group_detail= df_si.groupby(['age_group_detail'], as_index= False).agg({'YEAR':'count'})


    #Age Group Charts

    colors= {'adult':'blue','child':'orange'}
    fig_child = px.pie(df_child, names= 'child',values='YEAR',labels={'YEAR':'Patients'},
                        title="Presumptive Childhood TB Referral (<15 yrs)",
                  color= 'child',color_discrete_map= colors)
    fig_child.update_traces(pull=[0, 0.2])
    st.plotly_chart(fig_child, use_container_width= True)
    
    fig_age_group = px.histogram(df_age_group, x= 'age_group',y='YEAR',labels={'YEAR':'Patients'},
                        title='Age category of Presumptive Referral Patients',color='age_group', color_discrete_sequence=px.colors.diverging.oxy,
                             category_orders=dict(age_group=['0-4 yrs','5-14 yrs','15-60 yrs','> 60 yrs']))
    fig_age_group.update_layout(showlegend=False)

    st.plotly_chart(fig_age_group, use_container_width= True)


    fig_age_group_detail = px.histogram(df_age_group_detail, x= 'age_group_detail',y='YEAR',labels={'YEAR':'Patients'},
                        title='Age category detail of Presumptive Referral Patients', color='age_group_detail', 
                             color_discrete_sequence=px.colors.sequential.thermal,barmode='overlay',
                             category_orders=dict(age_group_detail=['0-4 yrs','5-9 yrs','10-14 yrs','15-24 yrs','25-34 yrs',
                                                             '35-44 yrs','45-54 yrs','55-64 yrs','> 65 yrs']))
    fig_age_group_detail.update_layout(showlegend=False)

    st.plotly_chart(fig_age_group_detail, use_container_width= True)



    #Successful Referral Data Frame
    df_referral= df_si.groupby(['ReachToTBCenter'], as_index= False).agg({'YEAR':'count'})

    #Successful Referral Pie Plot
    colors= {'Dropout':'teal','Successful_Referral':'red'}
    fig_referral = px.pie(df_referral, names= 'ReachToTBCenter',values='YEAR',labels={'YEAR':'Patients'},
                        title='Drop out in Referral Patients',
                color= 'ReachToTBCenter',color_discrete_map= colors)
    fig_referral.update_traces(pull=[0.4,0])
    st.plotly_chart(fig_referral, use_container_width= True)

    #TB Data Frame
    df_TB= df_si.groupby(['Feedback'], as_index= False).agg({'YEAR':'count'})

    #TB Pie Plot
    colors= {'Non_TB':'purple','TB':'orange'}
    fig_TB = px.pie(df_TB, names= 'Feedback',values='YEAR',labels={'YEAR':'Patients'},
                        title='TB Occurence in Referral Patients',
                color= 'Feedback',color_discrete_map= colors, hole= 0.3)

    st.plotly_chart(fig_TB, use_container_width= True)

    #TB Site Data Frame
    df_tbsite= df_si.groupby(['TBsite'], as_index= False).agg({'YEAR':'count'})


    #TB Site Pie Plot
    colors= {'Extrapulmonary':'orange','Pulmonary':'teal'}
    fig_TBsite = px.pie(df_tbsite, names= 'TBsite',values='YEAR',labels={'YEAR':'Patients'},
                        title='TB site',
                color= 'TBsite',color_discrete_map= colors)
    fig_TBsite.update_traces(pull=[0.4,0])
    st.plotly_chart(fig_TBsite, use_container_width= True)
    

    #TB Type Data Frame
    df_TBtype= df_si.groupby(['Bacteriological'], as_index= False).agg({'YEAR':'count'})
    
    #TB Type Pie Plot
    colors= {'Bact_confirm':'cyan','Clinical_Dx':'magenta'}
    fig_TBtype = px.pie(df_TBtype, names= 'Bacteriological',values='YEAR',labels={'YEAR':'Patients'},
                        title='Bacteriological Dx of TB',
                color= 'Bacteriological',color_discrete_map= colors)

    st.plotly_chart(fig_TBtype, use_container_width= True)

    

    #TB category Dataframe
    df_TB_cat= df_si.groupby(['TB_cat'], as_index= False).agg({'YEAR':'count'})

    #TB Category Pie Plot
    colors= {'Extrapulmonary Bact_confirm':'blue','Extrapulmonary Clinical_Dx':'orange','Pulmonary Bact_confirm':'teal',
         'Pulmonary Clinical_Dx':'grey'}
    fig_TB_cat = px.pie(df_TB_cat, names= 'TB_cat',values='YEAR',labels={'YEAR':'Patients'},
                        title='Category of TB',
                color= 'TB_cat',color_discrete_map= colors)
    fig_TB_cat.update_traces(pull=[0.5,0.3,0.1,0])
    st.plotly_chart(fig_TB_cat, use_container_width= True)
    

    
    





        





 
