import yfinance as yf
import pandas as pd
from datetime import datetime
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

# Definindo as moedas, seus nomes e cores
cryptos = {
    'BTC-USD': {'name': 'Bitcoin', 'color': 'blue'},
    'BNB-USD': {'name': 'Binance Coin', 'color': 'orange'},
    'BCH-USD': {'name': 'Bitcoin Cash', 'color': 'cyan'},
    'DOGE-USD': {'name': 'Dogecoin', 'color': 'red'},
    'ETH-USD': {'name': 'Ethereum', 'color': 'gold'},
    'SOL-USD': {'name': 'Solana', 'color': 'lightgreen'},
    'USDT-USD': {'name': 'Tether', 'color': 'purple'},
    'XMR-USD': {'name': 'Monero', 'color': 'white'},
    'XRP-USD': {'name': 'Ripple', 'color': 'gray'},
}

data_inicial = '2024-06-01'
data_atual = datetime.now().strftime('%Y-%m-%d')

# Coletando os dados
dados = []
for crypto in cryptos.keys():
    dados_crypto = yf.download(crypto, start=data_inicial, end=data_atual, auto_adjust=False)
    for data, linha in dados_crypto.iterrows():
        adj_close_valor = linha['Adj Close'].item() if isinstance(linha['Adj Close'], pd.Series) else linha['Adj Close']
        dados.append({
            'Date': data,
            'Crypto': crypto,
            'Adj Close': round(adj_close_valor, 3)
        })

df = pd.DataFrame(dados)


df['Month'] = df['Date'].dt.month
df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')

# Setando uma coluna para pegar porcentagem diaria
df['Percent'] = df.groupby('Crypto')['Adj Close'].pct_change() * 100

# Inicializando o app Dash
app = Dash(__name__)

style_layout = {
    'borderRadius': '15px',
    'width': '250px',
    'height': '35px',
    'margin': '5px',
    'color': 'black',
    'display': 'inline-block',
    'textAlign': 'center',
    'fontSize': '22px'
}

app.layout = html.Div(style={
    'backgroundColor': '#202630',
    'color': '#58ecba',
    'textAlign': 'center',
    'height': '150vh',
    'padding': '30px'
}, children=[
    html.H1("Dashboard de Criptomoedas", style={'textAlign': 'center', 'fontSize': '32px'}),
    html.H3("Período de 01/06/2024 -- Atual", style={'textAlign': 'center', 'fontSize': '24px'}),
    html.Div(children='''Selecione uma moeda e o tipo de gráfico.''', style={'textAlign': 'center', 'fontSize': '24px'}),

    dcc.Dropdown(
        id='crypto-dropdown',
        options=[{'label': 'Todas as Moedas', 'value': 'ALL'}] +
                [{'label': cryptos[coin]['name'], 'value': coin} for coin in cryptos],
        value='ALL',
        style=style_layout,
    ),
    dcc.Dropdown(
        id='graph-dropdown',
        options=[
            {'label': 'Gráfico de Linha', 'value': 'line'},
            {'label': 'Gráfico de Barra', 'value': 'bar'},
            {'label': 'Gráfico de Dispersão', 'value': 'scatter'},
            {'label': 'Gráfico de Box Plot', 'value': 'box'},
            {'label': 'Gráfico Linha PCT', 'value': 'line-pct'},
            {'label': 'Gráfico Barra PCT', 'value': 'bar-pct'},
        ],
        value='line',
        style=style_layout,
    ),
    dcc.Graph(id='crypto-graph', config={'displayModeBar': False}, style={'height': '75vh'}),

    # Seção de perguntas
    html.Div(style={
            'marginTop': '30px',
            'textAlign': 'center'},
        children=[
        html.H1("QUESTIONÁRIO DE PERFIL"),

        html.Div("Qual é a sua experiência com criptomoedas?", style={'textAlign': 'center', 'padding': '10px', 'fontSize': '24px', 'fontWeight': 'bold'}),
        dcc.RadioItems(
            id='experience-radio',
            options=[
                {'label': 'A) Comecei há menos de 1 ano.', 'value': 1},
                {'label': 'B) Invisto entre 1 a 3 anos.', 'value': 2},
                {'label': 'C) Mais de 3 anos de experiência.', 'value': 3},
            ],
            value=1,
            labelStyle={'display': 'block', 'fontSize': '20px'}
        ),

        html.Div("Você tem uma estratégia de investimento?", style={'textAlign': 'center', 'padding': '10px', 'fontSize': '24px', 'fontWeight': 'bold'}),
        dcc.RadioItems(
            id='strategy-radio',
            options=[
                {'label': 'A) Não tenho estratégia, sigo dicas.', 'value': 1},
                {'label': 'B) Pesquisa básica e acompanho notícias.', 'value': 2},
                {'label': 'C) Uso análise e desenvolvo um plano.', 'value': 3},
            ],
            value=1,
            labelStyle={'display': 'block', 'fontSize': '20px'}
        ),

        html.Div("Como você lida com a volatilidade do mercado?", style={'textAlign': 'center', 'padding': '10px', 'fontSize': '24px', 'fontWeight': 'bold'}),
        dcc.RadioItems(
            id='volatility-radio',
            options=[
                {'label': 'A) Fico preocupado e evito as oscilações.', 'value': 1},
                {'label': 'B) Já enfrentei perdas, mas aprendo com elas.', 'value': 2},
                {'label': 'C) Lido bem com a volatilidade e com perdas.', 'value': 3},
            ],
            value=1,
            labelStyle={'display': 'block', 'fontSize': '20px'}
        ),

        html.Div(id='investor-level', style={'marginTop': '20px', 'textAlign': 'center', 'fontWeight': 'bold', 'fontSize': '24px'})
    ])
])

@app.callback(
    Output('crypto-graph', 'figure'),
    Input('crypto-dropdown', 'value'),
    Input('graph-dropdown', 'value')
)
def update_graph(selected_crypto, graph_type):
    if selected_crypto is None:
        return px.bar(title="Nenhuma moeda selecionada.")
    if selected_crypto == 'ALL':
        data = df

    else:
        data = df[df['Crypto'] == selected_crypto]

    # Verifica se há dados para plotar
    if data.empty:
        return px.bar(title="Nenhum dado disponível para plotar.")

    # Criando gráficos com Plotly Express
    if graph_type == 'line':
        fig = px.line(data, x='Date', y='Adj Close', color='Crypto',
                      color_discrete_map={crypto: cryptos[crypto]['color'] for crypto in cryptos})

    elif graph_type == 'bar':
        data = data.groupby(['Month', 'Crypto'])['Adj Close'].mean().reset_index()
        fig = px.bar(data, x='Month', y='Adj Close', color='Crypto',
                      color_discrete_map={crypto: cryptos[crypto]['color'] for crypto in cryptos}, barmode='group')

    elif graph_type == 'scatter':
        fig = px.scatter(data, x='Date', y='Adj Close', color='Crypto',
                         color_discrete_map={crypto: cryptos[crypto]['color'] for crypto in cryptos})

    elif graph_type == 'box':
        fig = px.box(data, x='Crypto', y='Adj Close', color='Crypto',
                     color_discrete_map={crypto: cryptos[crypto]['color'] for crypto in cryptos})

    elif graph_type == 'line-pct':
        fig = px.line(data, x='Date', y='Percent', color='Crypto',
                      color_discrete_map={crypto: cryptos[crypto]['color'] for crypto in cryptos})

    elif graph_type == 'bar-pct':
        data = data.groupby(['Month', 'Crypto'])['Percent'].mean().reset_index()
        fig = px.bar(data, x='Month', y='Percent', color='Crypto', barmode='group',
                      color_discrete_map={crypto: cryptos[crypto]['color'] for crypto in cryptos})



    # Atualizando layout do gráfico
    fig.update_layout(
        plot_bgcolor='#202630',
        paper_bgcolor='#272e40',
        font_color='#58ecba',
        title={
            'text': 'Preço de fechamento ajustado ao longo do tempo!',
            'font': {
                'size': 22,
            },
        },
    )

    return fig

@app.callback(
    Output('investor-level', 'children'),
    Input('experience-radio', 'value'),
    Input('strategy-radio', 'value'),
    Input('volatility-radio', 'value')
)
def update_investor_level(exp, strat, volat):
    # Calculando a média das respostas
    avg_score = (exp + strat + volat) / 3

    # Definindo o nível do investidor
    if avg_score <= 1.5:
        level = "INICIANTE"
    elif avg_score <= 2.5:
        level = "INTERMEDIÁRIO"
    else:
        level = "AVANÇADO"

    return f"Baseado nas respostas o seu nível é: {level}"

if __name__ == '__main__':
    app.run_server(port=8049, debug=True)