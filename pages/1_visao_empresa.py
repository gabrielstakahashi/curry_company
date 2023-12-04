#libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
import folium
from PIL import Image
from streamlit_folium import folium_static
import datetime


st.set_page_config(page_title='Visão Empresa',page_icon='🏢', layout='wide')

#-----------------------------------
#Funções
#-----------------------------------
def country_maps ( df1 ):
            
            df_aux = (df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']]
                    .groupby(['City','Road_traffic_density'])
                    .median()
                    .reset_index())

            map = folium.Map()

            for index, location_info in df_aux.iterrows():
                folium.Marker([location_info['Delivery_location_latitude'],
                            location_info['Delivery_location_longitude']],
                            popup=location_info[['City', 'Road_traffic_density']]).add_to(map)
            
                #para imprimir o mapa no streamlit preciso importar o livro 'streamlit_folium' -> 'folium_static()'
            folium_static( map, width=800, height=500)
                
            
def order_share_by_week ( df1 ):
              
            df_aux01 = (df1.loc[:, ['ID', 'week_of_year']]
                        .groupby('week_of_year')
                        .count()
                        .reset_index())
            
            df_aux02 = (df1.loc[:, ['Delivery_person_ID', 'week_of_year']]
                        .groupby('week_of_year')
                        .nunique()
                        .reset_index())
            
            df_aux = pd.merge(df_aux01, df_aux02, how='inner')
            df_aux['order_by_deliver'] = round(df_aux['ID']/df_aux['Delivery_person_ID'], 2)
            fig5 = px.line(df_aux, x='week_of_year', y='order_by_deliver')

            return fig5

def order_by_week ( df1 ):
            #preciso organizar as datas em semanas
            #criar uma coluna de semana
            #'strftime' não é um atributo de 'series' => " 'Series' object has no attribute 'strftime' "
            #então preciso transformar a 'series' em data usando o '.dt'
        
            df1['week_of_year'] = df1 ['Order_Date'].dt.strftime(' %U ')
            cols = ['ID', 'week_of_year']
            df_aux = df1.loc[:, cols].groupby('week_of_year').count().reset_index()
            df_aux.head()
            #criar gráfico de linhas:
            fig4 = px.line(df_aux, x='week_of_year', y='ID')
            
            return fig4

def traffic_order_city(df1):
            df_aux = (df1.loc[:, ['ID', 'City', 'Road_traffic_density']]
                        .groupby(['City', 'Road_traffic_density'])
                        .count()
                        .reset_index())

            fig3 = px.scatter( df_aux, x = 'City', y = 'Road_traffic_density', size = 'ID', color = 'City')

            return fig3


def traffic_order_share(df1):
            df_aux = ( df1.loc[:, ['ID', 'Road_traffic_density']]
                      .groupby('Road_traffic_density')
                      .count()
                      .reset_index() )

            #remover da 'Road_traffic_density' o 'Nan':
            df_aux = df_aux.loc[df_aux['Road_traffic_density'] != "NaN", :]

            #preciso encontrar a distribuição dos pedidos, ou seja, a %:
            df_aux['entregas_perc'] = df_aux['ID']/df_aux['ID'].sum()

            #criar gráfico de pizza
            fig2 = px.pie(df_aux, values = 'entregas_perc', names = 'Road_traffic_density')
            return fig2

def order_metric(df1):
              
            cols = ['ID', 'Order_Date']

            #preciso resetar o index pra que a coluna pra que o 'Order_Date' se torne
            df_aux = df1.loc[:, cols].groupby(['Order_Date']).count().reset_index()

            #desenha gráfico de linhas
            #para mostrar o gráfico no streamlit preciso usar uma função própria do streamlit --> st.plotly_chart()

            fig1 = px.bar(df_aux, x='Order_Date', y='ID')

            return fig1

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

#------------------------------------------ Início da estrutura lógica do código ------------------------------------------
#=========================================================================================================================#

#-------------------
#import dataset
#-------------------

df = pd.read_csv('dataset/train.csv')

#-------------------
#Limpando os dados
#-------------------

df1 = clean_code( df )



#Visão Empresa:

# coluna 'ID' e 'Order_Date':

cols = ['ID', 'Order_Date']

#preciso resetar o index pra que a coluna pra que o 'Order_Date' se torne
df_aux = df1.loc[:, cols].groupby(['Order_Date']).count().reset_index()



px.bar(df_aux, x='Order_Date', y='ID')

# ========================================
#           barra lateral
# ========================================

st.header('Marketplace - Visão Empresa')

#logo
# image_path = 'C:\\Users\\gabri\\OneDrive\\Documents\\repos\\ftc\\ciclo_6\\'
image = Image.open('logo.jpg')
st.sidebar.image( image, width=280 )

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

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

#visão gerencial:
with tab1:
    with st.container():
        fig1 = order_metric( df1 )
        st.markdown('# Orders by day:')
        st.plotly_chart(fig1, use_container_width=True) #use_container_width=True --> faz com que o gráfico fique na largura do container.

    with st.container():
        col1, col2 = st.columns( 2 )

        with col1:
            
            fig2 = traffic_order_share( df1 )
            st.markdown( '### Traffic order share')       
            st.plotly_chart( fig2, use_container_width=True)        


        with col2:
            st.markdown( '### Traffic order city')
            fig3 = traffic_order_city(df1)
            st.plotly_chart( fig3, use_container_width=True)



#visão tática:
with tab2:
    with st.container():
        #orders by week:
        st.markdown('# Orders by week')
        fig4 = order_by_week( df1 )
        st.plotly_chart(fig4, use_container_width=True)

        
    with st.container():
        #order share by week:
        st.markdown('# Orders share by week')
        fig5 = order_share_by_week ( df1 )
        st.plotly_chart(fig5, use_container_width=True)     



#visão geográfica:
with tab3:
    st.markdown('# Country maps')

    #criando o mapa
    country_maps( df1 )





