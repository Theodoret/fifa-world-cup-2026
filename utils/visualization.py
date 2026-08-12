"""
Shared visualization helpers.
"""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def plot_bar(df: pd.DataFrame, x: str, y: str, title: str = "",
             color: str = None, height: int = 400) -> go.Figure:
    """Standard bar chart."""
    fig = px.bar(df, x=x, y=y, title=title, color=color, height=height)
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
    return fig


def plot_line(df: pd.DataFrame, x: str, y: str, title: str = "",
              color: str = None, height: int = 400) -> go.Figure:
    """Standard line chart."""
    fig = px.line(df, x=x, y=y, title=title, color=color, height=height)
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
    return fig


def plot_scatter(df: pd.DataFrame, x: str, y: str, title: str = "",
                 color: str = None, size: str = None, height: int = 400) -> go.Figure:
    """Standard scatter plot."""
    fig = px.scatter(df, x=x, y=y, title=title, color=color, size=size, height=height)
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
    return fig


def plot_pie(values: list, names: list, title: str = "", height: int = 400) -> go.Figure:
    """Standard pie chart."""
    fig = px.pie(values=values, names=names, title=title, height=height)
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
    return fig


def plot_heatmap(corr_matrix: pd.DataFrame, title: str = "", height: int = 500) -> go.Figure:
    """Correlation heatmap."""
    fig = px.imshow(corr_matrix, text_auto=".2f", aspect="auto",
                    title=title, height=height, color_continuous_scale="RdBu_r")
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
    return fig