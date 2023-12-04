#libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
import folium
from PIL import Image
from streamlit_folium import folium_static
from pandas.core.reshape import concat
import datetime

st.set_page_config(page_title='Visão Entregadores',page_icon='🛵', layout='wide')


#-----------------------------------
#Funções
#-----------------------------------


def top_delivers( df1, top_asc ):
    df2 = (df1.loc[:, ['Delivery_person_ID','Time_taken(min)','City']]
        .groupby(['City', 'Delivery_person_ID'])
        .mean()
        .sort_values(['City','Time_taken(min)'],ascending=top_asc)
        .reset_index())         

    df_aux01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
    df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
    df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)

    df3 = pd.concat( [df_aux01, df_aux02, df_aux03]).reset_index(drop = True)

    return df3

def clean_code(df1):
    """ 
        Função de limpeza do df1

        Tipos de limpeza:
        1. Remoção dos dados NaN
        2. Mudança do tipo da coluna de dados
        3. Remoção dos espaços das variáveis de texto
        4. Formatação da doluna de datas
        5. Limpeza da coluna de tempo (remoção do texto da variável numérica)
        
        Imput: Dataframe
        Output: Dataframe

    """

    #excluir linhas com a idade dos entregadores vazia:
    linhas_selecionadas = df1['Delivery_person_Age'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1 = df1.loc[df1['City'] != 'NaN', :].copy()
    df1 = df1.loc[df1['Road_traffic_density'] != 'NaN', :].copy()
    df1 = df1.loc[df1['Weatherconditions']!= 'NaN', :].copy()


    #Convertendo as colunas nos tipos corretos
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
    df1['Order_Date'] = pd.to_datetime( df1["Order_Date"], format='%d-%m-%Y')


    #excluir linhas vazias da coluna 'multiple_deliveries':
    linhas_selecionadas = df1['multiple_deliveries'] != 'NaN '
    df1 =df1.loc[linhas_selecionadas, :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

    #removendo os espaços das colunas
    #preciso arrumar o Index já que retirei algumas linhas do df1
    #se eu quiser que o df1 não mantenha o index original, tenho que colocar -> reset_index(Drop = True)

    # df1 = df1.reset_index()
    # for i in range(0, len(df1)):
    #   df1.loc[i,'ID'] = df1.loc[i,'ID'].strip()

    #maneira mais rápida de retirar os espaços dos valores:

    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()

    #limpando a coluna de Time_taken:

    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split( '(min) ')[1] )
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

    return(df1)

#-----------------------------------
#import dataset
#-----------------------------------
df = pd.read_csv('dataset/train.csv')

#cleaning dataset
df1 = clean_code( df )

# ========================================
#           barra lateral
# ========================================

st.header('Marketplace - Visão Entregadores')

#logo
# image_path = 'C:\\Users\\gabri\\OneDrive\\Documents\\repos\\ftc\\ciclo_6\\'
image = Image.open('logo.jpg')
st.sidebar.image( image, width=280 )

#st.sidebar.image

st.sidebar.markdown( '# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown( """---""")

st.sidebar.markdown( '## Selecione uma data limite')

date_slider = st.sidebar.slider('Até qual valor?', 
                  value = datetime.datetime(2022, 4, 13), 
                  min_value = datetime.datetime(2022, 2, 11),
                  max_value = datetime.datetime(2022, 4, 6),
                  format='DD-MM-YYYY')

st.sidebar.markdown( """---""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições de trânsito?',
    ['Low', 'Medium', 'High', 'Jam'],
    default = ['Low', 'Medium', 'High', 'Jam'] )

st.sidebar.markdown("""---""")

#configurando o sllider da barra lateral:
#filtro de data:
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]
#teste para ver se deu certo:

#filtro de tráfego:
linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[linhas_selecionadas, :]

# ========================================
#           layout no streamlit
# ========================================


with st.container():
    st.title( 'Overall Metrics' )
    col1, col2, col3, col4 = st.columns( 4, gap='large')
    #idades:
    with col1:
        #A maior idade dos entregadores
        maior_idade = df1['Delivery_person_Age'].max()
        col1.metric('Maior idade', maior_idade)

    with col2:
        #A menor idade dos entregadores
        menor_idade = df1['Delivery_person_Age'].min()
        col2.metric('Menor idade', menor_idade)
    
    #veículos:
    with col3:
        #A melhor condição de veículo
        melhor_condicao = df1['Vehicle_condition'].max()
        col3.metric('Melhor condição', melhor_condicao)

    with col4:
        #A pior condição de veículo
        pior_condicao = df1['Vehicle_condition'].min()
        col4.metric('Pior condição', pior_condicao)

with st.container():
    st.markdown("""---""")

    st.header('Avaliações')

    col1, col2 = st.columns( 2 )
    with col1:
        st.markdown( '##### Avaliações média por entregador')
        avaliacao_media = round(df1.loc[:, ['Delivery_person_ID', 'Delivery_person_Ratings']]
                                .groupby('Delivery_person_ID')
                                .mean()
                                .sort_values('Delivery_person_Ratings', ascending=False)
                                .reset_index(),
                                2)
        st.dataframe(avaliacao_media)

    with col2:
        #trânsito:
        st.markdown( '##### Avaliação média por trânsito')
        df_avg_std_transito = (df1.loc[:, ['Delivery_person_Ratings','Road_traffic_density']]
                              .groupby('Road_traffic_density')
                              .agg( {'Delivery_person_Ratings': ['mean', 'std']} ) )
        
        #mudança de nome das colunas:
        df_avg_std_transito.columns = ['delivery_mean', 'delivery_std']

        #reset do index:
        df_avg_std_transito = df_avg_std_transito.reset_index()

        #mostrando o df no streamlit:
        st.dataframe(df_avg_std_transito)

        #clima:
        st.markdown( '##### Avaliação por clima')
        #o .agg (='aggregation') agrega as funções que quero realizar na mesma coluna
        #.agg( {<coluna que recebe a operação: ['uma lista de operações a serem aplicadas na coluna' ]})

        df_avg_std_rating_weather = (df1.loc[: , ['Delivery_person_Ratings', 'Weatherconditions']]
                                     .groupby('Weatherconditions')
                                     .agg( {'Delivery_person_Ratings': ['mean', 'std', 'min', 'max']} ) )
        
        #renomeando as colunas:
        df_avg_std_rating_weather.columns = ['delivery_mean', 'delivery_std','min','max']

        #reset do index:
        df_avg_std_rating_weather = df_avg_std_rating_weather.reset_index()

        #mostrando o df no streamlit:
        st.dataframe(df_avg_std_rating_weather)


with st.container():
    st.markdown("""---""")
    st.header('Velocidade de entrega')

    col1, col2 = st.columns( 2 )

    with col1:
        st.markdown('##### Entregadores mais rápidos')
        df3 = top_delivers( df1, top_asc=True )
        st.dataframe( df3 )


    with col2:
        st.markdown('##### Entregadores mais lentos')
        df3 = top_delivers( df1, top_asc=False )
        st.dataframe( df3 )

            

                


