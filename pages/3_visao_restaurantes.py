#libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
import numpy as np
import folium
from PIL import Image
from streamlit_folium import folium_static
import datetime

st.set_page_config(page_title='Visão Restaurantes',page_icon='🥡', layout='wide')


#-----------------------------------
#Funções
#-----------------------------------
def avg_std_time_on_traffic( df1 ):
    df_aux = (df1.loc[:, ['Time_taken(min)', 'City','Road_traffic_density']]
                .groupby(['City', 'Road_traffic_density'])
                .agg({ 'Time_taken(min)' : ['mean', 'std'] }))
    
    df_aux.columns = ['avg_time', 'std_time']

    df_aux = df_aux.reset_index()

    fig = px.sunburst(df_aux,
                    path=['City', 'Road_traffic_density'],
                    values='avg_time',
                    color='std_time',
                    color_continuous_scale='RdBu',
                    color_continuous_midpoint=np.average(df_aux['std_time'] ) )
    return fig

def avg_std_time_graph( df1 ):
    df_aux = round(df1.loc[:, ['Time_taken(min)', 'City']].groupby('City').agg({ 'Time_taken(min)' : ['mean', 'std'] }),2)

    df_aux.columns = ['avg_time', 'std_time']

    df_aux = df_aux.reset_index()

    fig = go.Figure()

    fig.add_trace(go.Bar( name = 'Control',
                            x=df_aux['City'],
                            y=df_aux['avg_time'],
                            error_y=dict( type = 'data', array=df_aux['std_time' ] ) ) ) #o 'error' é o desvio padrão no gráfico
    fig.update_layout(barmode='group')

    return fig


def avg_std_time_delivery(df1, festival, op):
    """
        Esta função calcula o tempo médio e o desvio padrão do tempo das entregas
        Parâmetros:
            Input:
                -df: dataframe com os dados necessários para o cálculo
                -op: tipo de operação que precisa ser calculado
                    'avg_time': Calcula o tempo médio
                    'std_time': Calcula o desvio padrão do tempo
            Output:
                -df: dataframe com 2 colunas e 1 linha
    """
    
    df1 = df1.loc[df1['Festival'] != 'NaN', :].copy()

    df_aux = (df1.loc[:, ['Time_taken(min)', 'Festival']]
            .groupby(['Festival'])
            .agg({ 'Time_taken(min)' : ['mean', 'std'] }))
    
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    df_aux = round(df_aux.loc[df_aux['Festival'] == festival, op], 2)

    return df_aux


def distance(df1, fig):
    if fig == False:   
        cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']

        df1['Distance'] = round(df1.loc[:, cols]
                    .apply
                    (lambda x: haversine
                    ((x['Restaurant_latitude'], x['Restaurant_longitude'] ),
                    (x['Delivery_location_latitude'], x['Delivery_location_longitude'] )),
                        axis=1),
                    2)

        avg_distance = round(df1['Distance'].mean(),2)

        return avg_distance

    else:
        cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']

        df1['Distance'] = round(df1.loc[:, cols]
                            .apply
                            (lambda x: haversine
                            ((x['Restaurant_latitude'], x['Restaurant_longitude'] ),
                            (x['Delivery_location_latitude'], x['Delivery_location_longitude'] )),
                                axis=1),
                            2)
        df1 = df1.loc[df1['City'] != 'NaN',:]
        distance_mean = df1['Distance'].mean()
        st.markdown(f'#### Distância média das entregas: {round(distance_mean, 2)} km')

        avg_distance = df1.loc[:, ['City', 'Distance']].groupby( 'City' ).mean().reset_index()

        fig = go.Figure( data=[ go.Pie( labels = avg_distance['City'], values = avg_distance['Distance'], pull=[0, 0.1, 0])])

        return fig

            
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
    df1 = df1.loc[df1['City'] != 'NaN'].copy()
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

#-----------------------------------
#cleaning code
#-----------------------------------
df1 = clean_code( df )


# ========================================
#           barra lateral
# ========================================

st.header('Marketplace - Visão Restaurantes')

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
    st.markdown('## Overall Metrics')

    col1, col2, col3, col4, col5, col6 = st.columns( 6 )

    with col1:
        #entregadores únicos
        delivery_unique = df1['Delivery_person_ID'].nunique()
        col1.metric( 'Entregadores únicos', delivery_unique)

    with col2:
        #distância média
        avg_distance = distance(df1, fig=False)
        col2.metric( ' A distância média das entregas', avg_distance)           

    with col3:
        df_aux = avg_std_time_delivery(df1, 'Yes', 'avg_time')
        col3.metric( 'Tempo médio com festival', df_aux)

    with col4:
        df_aux = avg_std_time_delivery(df1, 'Yes', 'std_time')
        col4.metric( 'Desvio padrão com festival', df_aux)

    with col5:
        df_aux = avg_std_time_delivery(df1, 'No', 'avg_time')
        col5.metric( 'Tempo médio sem festival', df_aux)

    with col6:
        df_aux = avg_std_time_delivery(df1, 'No', 'std_time')
        col6.metric( 'Desvio padrão sem festival', df_aux)

    
with st.container():
    df1 = df1.loc[df1['City'] != 'NaN']
    st.markdown( """---""")

    col1, col2 = st.columns( 2 )

    with col1:
        fig = avg_std_time_graph( df1 )
        st.plotly_chart( fig )

    with col2:

        df_aux = round(df1.loc[:, ['Time_taken(min)', 'City','Type_of_order']]
                .groupby(['City', 'Type_of_order'])
                .agg({ 'Time_taken(min)' : ['mean', 'std'] })
                ,2)
        
        df_aux.columns = ['avg_time', 'std_time']
        df_aux = df_aux.reset_index()

        st.dataframe(df_aux)

    
with st.container():
    st.markdown('## Distribuiçao do tempo')

    col1, col2 = st.columns( 2 )

    with col1:
        fig = distance( df1, fig=True )
        st.plotly_chart( fig )

                   
    with col2:
        fig = avg_std_time_on_traffic ( df1 )
        st.plotly_chart( fig )
        
