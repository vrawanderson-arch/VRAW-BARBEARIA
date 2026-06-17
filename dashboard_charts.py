import plotly.express as px
import pandas as pd


def create_advanced_dashboard(df_agendamentos):
    """Cria gráficos avançados para o dashboard usando Plotly"""

    if df_agendamentos.empty:
        return None, None, None

    # Gráfico 1 - Status
    fig_status = px.pie(
        df_agendamentos,
        names="status",
        hole=0.4,
        title="Distribuição por Status"
    )

    # Gráfico 2 - Receita
    precos = {
        "Corte feminino": 80,
        "Corte masculino": 40,
        "Coloração": 150,
        "Manicure": 30,
        "Pedicure": 30,
        "Combo Mani + Pedi": 50,
        "Design de sobrancelha": 45,
        "Escova progressiva": 250,
        "Outro": 50
    }

    df_agendamentos["valor_estimado"] = (
        df_agendamentos["servico"]
        .map(precos)
        .fillna(50)
    )

    receita_servico = (
        df_agendamentos
        .groupby("servico")["valor_estimado"]
        .sum()
        .reset_index()
    )

    fig_receita = px.bar(
        receita_servico,
        x="servico",
        y="valor_estimado",
        title="Receita Estimada por Serviço"
    )

    # Gráfico 3 - Evolução temporal
    df_agendamentos["data_curta"] = pd.to_datetime(
        df_agendamentos["data"],
        format="mixed",
        errors="coerce"
    ).dt.date

    df_agendamentos = df_agendamentos.dropna(
        subset=["data_curta"]
    )

    evolucao = (
        df_agendamentos
        .groupby("data_curta")
        .size()
        .reset_index(name="quantidade")
    )

    fig_evolucao = px.line(
        evolucao,
        x="data_curta",
        y="quantidade",
        title="Evolução de Agendamentos",
        markers=True
    )

    return fig_status, fig_receita, fig_evolucao
