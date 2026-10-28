import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Curso Superior", layout="wide")

estados = {
    "Minas Gerais": "MG",
    "Espírito Santo": "ES",
    "Rio de Janeiro": "RJ",
    "São Paulo": "SP",
    "Paraná": "PR",
    "Mato Grosso do Sul": "MS",
}


@st.cache_data
def carregar_dados():
    df = pd.read_excel("Tabela_3_Areas_gerais_de_formacao_na_graduacao.xlsx", header=None, skiprows=3, nrows=33)
    df.columns = [
        "Estado",
        "Total_Total", "Total_Homens", "Total_Mulheres",
        "Exatas_Total", "Exatas_Homens", "Exatas_Mulheres",
        "Saude_Total", "Saude_Homens", "Saude_Mulheres",
    ]
    df = df[df["Estado"].isin(estados.keys())]
    df["UF"] = df["Estado"].map(estados)
    df["Humanas_Homens"] = df["Total_Homens"] - df["Exatas_Homens"] - df["Saude_Homens"]
    df["Humanas_Mulheres"] = df["Total_Mulheres"] - df["Exatas_Mulheres"] - df["Saude_Mulheres"]

    df_longo = df.melt(
        id_vars=["UF"],
        value_vars=[
            "Exatas_Homens", "Exatas_Mulheres",
            "Saude_Homens", "Saude_Mulheres",
            "Humanas_Homens", "Humanas_Mulheres",
        ],
        var_name="Coluna",
        value_name="Pessoas",
    )
    df_longo["Área"] = df_longo["Coluna"].str.split("_").str[0].replace("Saude", "Saúde")
    df_longo["Sexo"] = df_longo["Coluna"].str.split("_").str[1]
    df_longo["Ano"] = 2022

    pop = pd.read_excel("CD2022_Populacao_2010_Compatibilizada_20231222.ods", header=None, skiprows=3)
    pop = pop[[1, 7]]
    pop.columns = ["UF", "População"]
    pop["População"] = pd.to_numeric(pop["População"], errors="coerce")
    pop = pop.groupby("UF")["População"].sum().reset_index()
    pop = pop[pop["UF"].isin(estados.values())]

    return df_longo, pop


df, pop = carregar_dados()

st.sidebar.header("Filtros")
filtro_estado = st.sidebar.multiselect("Estado", list(estados.values()), default=list(estados.values()))
filtro_ano = st.sidebar.selectbox("Ano", [2022])
filtro_area = st.sidebar.multiselect("Área do conhecimento", ["Exatas", "Humanas", "Saúde"], default=["Exatas", "Humanas", "Saúde"])
filtro_sexo = st.sidebar.multiselect("Sexo", ["Homens", "Mulheres"], default=["Homens", "Mulheres"])

df_filtro = df[
    (df["UF"].isin(filtro_estado))
    & (df["Ano"] == filtro_ano)
    & (df["Área"].isin(filtro_area))
    & (df["Sexo"].isin(filtro_sexo))
]
pop_filtro = pop[pop["UF"].isin(filtro_estado)]

st.title("Ensino Superior - Sudeste, Paraná e Mato Grosso do Sul")
st.write("Fonte: IBGE - Censo Demográfico 2022")

total_pessoas = df_filtro["Pessoas"].sum()
total_pop = pop_filtro["População"].sum()
taxa = total_pessoas / total_pop * 100 if total_pop > 0 else 0

df_estados = df[(df["UF"].isin(filtro_estado)) & (df["Ano"] == filtro_ano)]
exatas = df_estados[df_estados["Área"] == "Exatas"]
humanas = df_estados[df_estados["Área"] == "Humanas"]
pct_mulheres_exatas = exatas[exatas["Sexo"] == "Mulheres"]["Pessoas"].sum() / exatas["Pessoas"].sum() * 100 if exatas["Pessoas"].sum() > 0 else 0
pct_mulheres_humanas = humanas[humanas["Sexo"] == "Mulheres"]["Pessoas"].sum() / humanas["Pessoas"].sum() * 100 if humanas["Pessoas"].sum() > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric(label="Pessoas com nível superior", value=f"{total_pessoas:,.0f}".replace(",", "."))
col2.metric(label="Taxa de graduação", value=f"{taxa:.1f}%")
col3.metric(label="Mulheres diplomadas em Exatas", value=f"{pct_mulheres_exatas:.1f}%")
col4.metric(label="Mulheres diplomadas em Humanas", value=f"{pct_mulheres_humanas:.1f}%")

df_taxa = df_filtro.groupby("UF")["Pessoas"].sum().reset_index()
df_taxa = df_taxa.merge(pop_filtro, on="UF")
df_taxa["Taxa"] = df_taxa["Pessoas"] / df_taxa["População"] * 100

fig_linha = px.line(
    df_taxa,
    x="UF",
    y="Taxa",
    markers=True,
    title=f"Taxa de graduação por estado ({filtro_ano})",
)
st.plotly_chart(fig_linha, use_container_width=True)

df_genero = df_filtro.groupby(["Área", "Sexo"])["Pessoas"].sum().reset_index()
df_genero["Percentual"] = df_genero["Pessoas"] / df_genero.groupby("Área")["Pessoas"].transform("sum") * 100

fig_barra = px.bar(
    df_genero,
    x="Área",
    y="Percentual",
    color="Sexo",
    barmode="stack",
    title="Proporção de gênero por área do curso (%)",
)
st.plotly_chart(fig_barra, use_container_width=True)

st.header("Notícias")

col_a, col_b, col_c = st.columns(3)

with col_a:
    st.subheader("Fuga de cérebros")
    st.image("https://revistapesquisa.fapesp.br/wp-content/uploads/2026/05/rpf-fuga-de-cerebros-2026-06-1140b.jpg")
    st.markdown("[Estudo aponta que 1,2% dos doutores que se formaram no Brasil estava fora do país em 2025 - Revista Pesquisa FAPESP](https://revistapesquisa.fapesp.br/estudo-aponta-que-12-dos-doutores-que-se-formaram-no-brasil-estava-fora-do-pais-em-2025)")

with col_b:
    st.subheader("Escassez de profissionais de TI")
    st.image("https://midias.correiobraziliense.com.br/_midias/jpg/2024/08/24/675x450/1_tecnologia_da_informacao-39594849.jpg")
    st.markdown("[Brasil enfrenta apagão de profissionais de TI - Correio Braziliense](https://www.correiobraziliense.com.br/economia/2024/08/6927263-brasil-enfrenta-apagao-de-profissionais-de-ti.html)")

with col_c:
    st.subheader("Mulheres em STEM")
    st.image("https://fastcompanybrasil.com/wp-content/uploads/2026/09/mulheres_tecnologia_STEM.jpg")
    st.markdown("[Mulheres estão entrando em STEM. O problema é fazê-las chegar ao topo - Fast Company Brasil](https://fastcompanybrasil.com/impacto/mulheres-estao-entrando-em-stem-o-problema-e-faze-las-chegar-ao-topo/)")
