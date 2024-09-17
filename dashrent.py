import pandas as pd
import streamlit as st
import plotly.express as px
import locale

# Lê os dados do CSV
data = pd.read_csv('houses_to_rent_v2.csv')

# Configurações da página do Streamlit
st.set_page_config(layout="wide")
st.title('Dashboard de Imóveis para Alugar')

# Fundo da página
page_bg = '''
    <style>
    .stApp {
        background-color: #f4f4f9;
    }
    .card {
        background-color: white;
        padding: 20px;
        margin-bottom: 20px;
        border-radius: 10px;
        box-shadow: 0px 0px 15px rgba(0,0,0,0.1);
    }
    .metric-card {
        background-color: white;
        padding: 10px;
        border-radius: 10px;
        box-shadow: 0px 0px 15px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    </style>
'''
st.markdown(page_bg, unsafe_allow_html=True)  # Define o fundo da página com cor clara e estética limpa

# Paleta de cores para consistência nos gráficos
colors = px.colors.qualitative.Plotly  # Uso das cores padrão do Plotly para consistência visual

# Exibe logo na barra lateral
st.sidebar.image('logo.png', use_column_width=True)

# Informações na barra lateral
st.sidebar.markdown("**Visualização de dados**")
st.sidebar.markdown("**Alan Barros**")

# Filtro de cidades na barra lateral
cities = data['city'].unique()
selected_city = st.sidebar.multiselect('Selecione uma ou mais cidades', cities, default=cities)
filtered_data = data[data['city'].isin(selected_city)]

# Divisão em colunas para layout
col1, col2 = st.columns(2)

# Coluna 1
with col1:
    # Cartão 1: Total de Imóveis
    if not filtered_data.empty:
        total_imoveis = filtered_data.shape[0]
        st.metric(label="Total de Imóveis", value=total_imoveis)
    else:
        st.write("Selecione uma cidade para análise.")
  
    # Gráfico de distribuição de preços de aluguel
    st.subheader(f"Distribuição de Preços de Aluguel em {', '.join(selected_city)}")
    if not filtered_data.empty:
        # Histograma do preço do aluguel
        fig_rent = px.histogram(filtered_data, x='rent amount (R$)', nbins=20, 
                                title='Distribuição de Aluguel', color_discrete_sequence=[colors[0]])
        # Ajuste do layout do gráfico para fundo limpo e títulos centralizados
        fig_rent.update_layout(paper_bgcolor="white", plot_bgcolor='rgba(0,0,0,0)', title_x=0.5)
        st.plotly_chart(fig_rent)
    else:
        st.write("Selecione uma cidade para análise.")

    # Gráfico de barras empilhadas: Percentual de custos
    st.subheader(f"Composição dos Custos em {', '.join(selected_city)}")
    if not filtered_data.empty:
        # Evita divisão por zero nos custos totais
        filtered_data['total_custo'] = filtered_data[['hoa (R$)', 'rent amount (R$)', 'property tax (R$)', 'fire insurance (R$)']].sum(axis=1)
        filtered_data['total_custo'] = filtered_data['total_custo'].replace(0, 1)  # Substitui por 1 para evitar erro de divisão por zero

        # Calcula o percentual de cada custo no total de aluguel
        filtered_data['hoa_pct'] = (filtered_data['hoa (R$)'] / filtered_data['total_custo']) * 100
        filtered_data['rent_pct'] = (filtered_data['rent amount (R$)'] / filtered_data['total_custo']) * 100
        filtered_data['tax_pct'] = (filtered_data['property tax (R$)'] / filtered_data['total_custo']) * 100
        filtered_data['fire_insurance_pct'] = (filtered_data['fire insurance (R$)'] / filtered_data['total_custo']) * 100

        # Organiza os dados para o gráfico de barras empilhadas
        stacked_data = filtered_data[['city', 'hoa_pct', 'rent_pct', 'tax_pct', 'fire_insurance_pct']].melt(id_vars='city', var_name='Custo', value_name='Percentual')
        custo_mapping = {'hoa_pct': 'HOA', 'rent_pct': 'Aluguel', 'tax_pct': 'Imposto', 'fire_insurance_pct': 'Seguro'}
        stacked_data['Custo'] = stacked_data['Custo'].map(custo_mapping)

        # Gráfico de barras empilhadas
        fig_stacked_bar = px.bar(stacked_data, x='city', y='Percentual', color='Custo',
                                 title='Percentual de Custos no Total do Aluguel',
                                 labels={'Percentual': 'Valor', 'city': 'Cidade'},
                                 color_discrete_map={'HOA': 'lightblue', 'Aluguel': 'red', 'Imposto': 'lightgreen', 'Seguro': 'orange'})

        # Layout ajustado com título centralizado e cores claras para melhor visualização
        fig_stacked_bar.update_layout(paper_bgcolor="white", plot_bgcolor='rgba(0,0,0,0)', title_x=0.5)
        st.plotly_chart(fig_stacked_bar)
    else:
        st.write("Selecione uma cidade para análise.")

    # Gráfico de distribuição de animais por cidade
    st.subheader(f"Distribuição de Animais por Cidade em {', '.join(selected_city)}")
    if not filtered_data.empty:
            grouped_data = filtered_data.groupby(['animal', 'city']).size().reset_index(name='count')
    
    # Gráfico de barras para distribuição de animais
            fig_animals = px.bar(grouped_data, 
                         x='animal', 
                         y='count', 
                         color='city', 
                         barmode='group',  # Barras agrupadas
                         title='Contagem de Animais por Cidade',
                         color_discrete_sequence=colors)  # Usando cores padronizadas

    # Ajustando layout do gráfico de barras
            fig_animals.update_layout(paper_bgcolor="white",  # Fundo branco
                              plot_bgcolor='rgba(0,0,0,0)',  # Fundo transparente
                              title_x=0.5)  # Centraliza o título

            st.plotly_chart(fig_animals)
    else:
            st.write("Selecione uma cidade para análise.")
    



# Coluna 2
with col2:
    # Cartão 2: Valor médio do aluguel
    if not filtered_data.empty:
        valor_médio_aluguel = round(filtered_data['rent amount (R$)'].mean())
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
        valor_formatado = locale.currency(int(valor_médio_aluguel), grouping=True, symbol='R$')
        st.metric(label="Preço médio aluguel", value=valor_formatado)
    else:
        st.write("Selecione uma cidade para análise.")

    # Gráfico de Preço médio por Cidade e Número de Quartos
    st.subheader(f"Preço médio por Cidade e Número de Quartos em {', '.join(selected_city)}")
    if not filtered_data.empty:
        # Média dos preços por cidade e número de quartos
        city_rooms_total = filtered_data.groupby(['city', 'rooms'])['total (R$)'].mean().reset_index()

        # Gráfico de barras agrupadas com cores consistentes
        fig_city_rooms = px.bar(city_rooms_total, 
                                x='city', 
                                y='total (R$)', 
                                color='rooms', 
                                barmode='group', 
                                title='Preço médio por Cidade e Número de Quartos', 
                                labels={'total (R$)': 'Preço médio', 'city': 'Cidade', 'rooms': 'Quartos'},
                                color_discrete_sequence=colors)

        # Ajuste de layout para centralizar título e limpar o fundo
        fig_city_rooms.update_layout(paper_bgcolor="white", plot_bgcolor='rgba(0,0,0,0)', title_x=0.5)
        st.plotly_chart(fig_city_rooms)
    else:
        st.write("Selecione uma cidade para análise.")

    # Gráfico de proporção de imóveis mobiliados
    st.subheader(f"Proporção por móveis em {', '.join(selected_city)}")
    if not filtered_data.empty:
        # Gráfico de pizza para proporção de imóveis mobiliados
        furniture_counts = filtered_data['furniture'].value_counts()
        fig_furniture = px.pie(furniture_counts, 
                               values=furniture_counts.values, 
                               names=furniture_counts.index, 
                               title='Proporção de móveis', 
                               color_discrete_sequence=colors)

        # Ajuste de layout para melhor clareza visual
        fig_furniture.update_layout(paper_bgcolor="white", plot_bgcolor='rgba(0,0,0,0)', title_x=0.5)
        st.plotly_chart(fig_furniture)
    else:
        st.write("Necessário escolher uma cidade.")


    # Tabela com estatísticas descritivas dos imóveis
    st.subheader(f"Estatísticas Descritivas dos Imóveis em {', '.join(selected_city)}")
    if not filtered_data.empty:
        # Estatísticas básicas das colunas selecionadas
        stats = filtered_data[['area', 'rooms', 'bathroom', 'parking spaces', 'rent amount (R$)', 'total (R$)']].describe().transpose()
        stats.columns = ['Contagem', 'Média', 'Desvio Padrão', 'Mínimo', '25%', '50%', '75%', 'Máximo']
        st.dataframe(stats)
    else:
        st.write("Selecione uma cidade para análise.")



   
    



    
    

    


