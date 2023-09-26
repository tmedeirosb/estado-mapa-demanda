import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from collections import Counter

# Load the cleaned data
#@st.cache
def load_data():
    df = pd.read_excel('rel_demanda_resposta_unica-anonimo.xlsx')  # Insira o caminho correto para o arquivo
    return df

df = load_data()

# Sidebar multi-select for filtering
def multiselect_filter(df_filtered, attribute):
    # For specific columns, consider unique values separated by ";"
    if attribute in ['NÍVEL DE ENSINO', 'MODALIDADE', 'COMPONENTES CURRICULARES EM CASO DE SALA DE AULA']:
        # Normalize strings and remove duplicates
        options = set(val.strip().lower() for val in df_filtered[attribute].dropna().str.split(';').explode() if isinstance(val, str))
    else:
        options = sorted(df_filtered[attribute].dropna().unique().tolist())
    
    values = st.sidebar.multiselect(f"Selecione {attribute}", options)
    if values:  # If the user has selected any value, filter the DataFrame
        if attribute in ['NÍVEL DE ENSINO', 'MODALIDADE', 'COMPONENTES CURRICULARES EM CASO DE SALA DE AULA']:
            df_filtered = df_filtered[df_filtered[attribute].apply(lambda x: any(val.lower() in x.lower() for val in values if isinstance(val, str) and isinstance(x, str)))]
        else:
            df_filtered = df_filtered[df_filtered[attribute].isin(values)]
    return df_filtered


# Applying filters
df_filtered = df.copy()
attributes = ['DIREC', 'UNIDADE DE LOTAÇÃO', 'FUNÇÃO', 'NÍVEL DE ENSINO', 'MODALIDADE', 'COMPONENTES CURRICULARES EM CASO DE SALA DE AULA']
for attribute in attributes:
    df_filtered = multiselect_filter(df_filtered, attribute)

# Sidebar selectbox for aggregation (hue in the plot)
attributs_agg = ['DIREC', 'UNIDADE DE LOTAÇÃO', 'FUNÇÃO']
aggregation = st.sidebar.selectbox('Agregação', ['Nenhuma'] + attributs_agg)

# Define columns_to_compare based on user specification
columns_to_compare = [
    'Gestão Escolar (Marcar NO MÁXIMO 3 opções de temáticas de seu interesse de formação)', 
    'Prática pedagógica (Marcar NO MÁXIMO 5 opções de temáticas de seu interesse de formação)', 
    'Educação profissional (Marcar NO MÁXIMO 2 opções de temáticas de seu interesse de formação)', 
    'Educação de Jovens e Adultos (Marcar NO MÁXIMO 2 opções de temáticas de seu interesse de formação)', 
    'Educação Escolar do Campo (Marcar NO MÁXIMO 2 opções de temáticas de seu interesse de formação)', 
    'Biblioteca Escolar (Marcar NO MÁXIMO 1 opção de temática de seu interesse de formação)', 
    'Tecnologia Educacional (Marcar NO MÁXIMO 2 opções de temáticas de seu interesse de formação)', 
    'Educação Especial (Marcar NO MÁXIMO 4 opções de temáticas de seu interesse de formação)', 
    'Educação para Paz e Direito Humanos (Marcar NO MÁXIMO 3 opções de temáticas de seu interesse de formação)'
]

# Main button to visualize the plot
if st.button('Visualizar'):
    for column in columns_to_compare:
        # Check if there are non-NaN values
        if df_filtered[column].notna().any():
            # Check if aggregation is needed
            if aggregation != 'Nenhuma':
                # Group by aggregation column and then count the frequency of each unique value within each group
                grouped = df_filtered.dropna(subset=[column]).groupby(aggregation)[column] \
                    .apply(lambda x: x.str.split(';').explode()).reset_index()
                plot_df = grouped.groupby([aggregation, column]).size().reset_index(name='Contagem')
                
                # Plot the bar graph with aggregation
                plt.figure(figsize=(10,6))
                sns.barplot(x='Contagem', y=column, data=plot_df, hue=aggregation, palette="viridis", ci=None)
                plt.title(f'Contagem de Respostas para {column} - Agregado por {aggregation}')
            else:
                # Initialize a Counter object to hold the counts of each unique value
                counter = Counter()
                
                # Get the values in the column, drop NaN and split them by ";"
                values = df_filtered[column].dropna().str.split(';')
                
                # Count the frequency of each unique value
                for value_list in values:
                    counter.update(value_list)
                
                # Prepare data for plotting
                labels = list(counter.keys())
                counts = list(counter.values())
                
                # Create a DataFrame for plotting
                plot_df = pd.DataFrame({column: labels, 'Contagem': counts})
                
                # Plot the bar graph without aggregation
                plt.figure(figsize=(10,6))
                sns.barplot(x='Contagem', y=column, data=plot_df, palette="viridis")
                plt.title(f'Contagem de Respostas para {column}')
            
            # Common plot settings
            plt.xlabel('Contagem')
            plt.ylabel('Respostas')
            
            # Add count annotations to each bar
            ax = plt.gca()
            for p in ax.patches:
                width = p.get_width()
                if not pd.isna(width):  # Check if width is not NaN before annotating
                    ax.annotate(f'{int(width)}', (width, p.get_y() + p.get_height()/2), ha='left', va='center')
            
            # Show the plot
            st.pyplot(plt)
            plt.clf()

