import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
import pandas as pd
from collections import Counter

df = pd.read_parquet("D:/projeto_lapes/datalake/diamond/pacientes_dimond.parquet")

pathology_list = ['cardiomegaly','emphysema','effusion','hernia','nodule','pneumothorax','atelectasis','pleural_thickening','mass','edema','consolidation','infiltration','fibrosis','pneumonia']
for pathology in pathology_list:
    df[pathology] = df['patologia'].apply(lambda x: 1 if pathology in x.lower() else 0)

df['nothing'] = df['patologia'].apply(lambda x: 1 if 'no finding' in x.lower() else 0)
df = df[(df['idades'].between(0, 120)) & (df['genero'].isin(['Male', 'Female']))]
df['faixa_etaria'] = pd.cut(df['idades'], bins=range(0, 110, 10))

labels = df['patologia'].dropna().str.split('|').explode().str.lower()
top10 = Counter(labels).most_common(10)
labels_names = [item[0] for item in top10]
labels_counts = [item[1] for item in top10]

faixa_df = df['faixa_etaria'].value_counts().sort_index().reset_index()
faixa_df.columns = ['faixa_etaria', 'count']
faixa_df['faixa_etaria'] = faixa_df['faixa_etaria'].astype(str)

vp_df = df['angulo_de_vista'].value_counts().reset_index()
vp_df.columns = ['angulo_de_vista', 'count']

app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "dashboard - raios-x"

colorblind_palette = px.colors.qualitative.Safe

app.layout = html.Div([
    dcc.Store(id="theme-store", data={"theme": "vapor"}),
    html.Link(id='theme-link', rel='stylesheet', href='https://bootswatch.com/5/vapor/bootstrap.min.css'),
    html.Div([
        html.H1("dashboard de bi - raios-x", className="text-center mb-4"),
        html.Div([
        ], className="d-flex justify-content-center mb-4"),
        dcc.Tabs(id='tabs', value='tab1', children=[
            dcc.Tab(label='distribuição de idade', value='tab1'),
            dcc.Tab(label='idade por gênero (violin)', value='tab2'),
            dcc.Tab(label='faixa etária', value='tab3'),
            dcc.Tab(label='angulo de vista', value='tab4'),
            dcc.Tab(label='top 10 labels (barra)', value='tab5'),
            dcc.Tab(label='top 10 labels (pizza)', value='tab6'),
        ]),
        html.Div(id='tabs-content')
    ], className="container")
])

def create_figures(theme):
    bg_color = '#22252a'
    font_color = 'white'
    plot_bgcolor = '#22252a'
    paper_bgcolor = '#22252a'
    template = 'plotly_dark'

    fig1 = px.histogram(df, x="idades", nbins=30, title="distribuição da idade dos pacientes",
                        color_discrete_sequence=colorblind_palette, template=template)
    fig1.update_layout(plot_bgcolor=plot_bgcolor, paper_bgcolor=paper_bgcolor, font_color=font_color)

    fig2 = px.violin(df, y="idades", x="genero", color="genero", box=True, points="all",
                     title="distribuição da idade por gênero",
                     color_discrete_sequence=colorblind_palette, template=template)
    fig2.update_layout(plot_bgcolor=plot_bgcolor, paper_bgcolor=paper_bgcolor, font_color=font_color)

    fig3 = px.bar(faixa_df, x='faixa_etaria', y='count', title='distribuição por faixa etária',
                  color_discrete_sequence=[colorblind_palette[1]], template=template)
    fig3.update_layout(plot_bgcolor=plot_bgcolor, paper_bgcolor=paper_bgcolor, font_color=font_color)

    fig4 = px.bar(vp_df, x='angulo_de_vista', y='count', title='distribuição por angulo_de_vista',
                  color_discrete_sequence=[colorblind_palette[2]], template=template)
    fig4.update_layout(plot_bgcolor=plot_bgcolor, paper_bgcolor=paper_bgcolor, font_color=font_color)

    fig5 = px.bar(x=labels_counts, y=labels_names, orientation='h', title='top 10 patologia mais comuns',
                  color_discrete_sequence=[colorblind_palette[3]], template=template)
    fig5.update_layout(plot_bgcolor=plot_bgcolor, paper_bgcolor=paper_bgcolor, font_color=font_color)

    fig6 = px.pie(names=labels_names, values=labels_counts, title='top 10 patologias mais comuns',
                  color_discrete_sequence=colorblind_palette, template=template)
    fig6.update_layout(font_color=font_color, paper_bgcolor=paper_bgcolor)

    return {
        'tab1': fig1,
        'tab2': fig2,
        'tab3': fig3,
        'tab4': fig4,
        'tab5': fig5,
        'tab6': fig6
    }

@app.callback(
    Output("theme-link", "href"),
    Output("theme-store", "data"),
    Input("toggle-theme", "n_clicks"),
    State("theme-store", "data")
)
def toggle_theme(n, data):
    return "https://bootswatch.com/5/vapor/bootstrap.min.css", {"theme": "vapor"}

@app.callback(
    Output('tabs-content', 'children'),
    Input('tabs', 'value'),
    State('theme-store', 'data')
)
def render_content(tab, data):
    theme = data.get("theme", "vapor")
    figs = create_figures(theme)
    return dcc.Graph(figure=figs[tab])

if __name__ == '__main__':
    app.run(debug=True)
