from typing import Optional

import streamlit as st


def load_global_style() -> None:
    st.markdown(
        """
        <style>
            .app-title {
                font-size: 2.8rem;
                font-weight: 700;
                color: #1e3a8a;
                margin-bottom: 0.5rem;
                text-align: center;
            }
            .app-subtitle {
                font-size: 1.2rem;
                color: #374151;
                margin-bottom: 1.5rem;
                text-align: center;
                font-weight: 400;
            }
            .app-description {
                font-size: 1rem;
                color: #6b7280;
                margin-bottom: 2rem;
                text-align: center;
            }
            .metric-card {
                background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
                border-radius: 12px;
                padding: 1.5rem;
                text-align: center;
                border: 1px solid #e5e7eb;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                transition: transform 0.2s;
            }
            .metric-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.15);
            }
            .metric-label {
                font-size: 0.9rem;
                color: #6b7280;
                margin-bottom: 0.5rem;
                font-weight: 500;
            }
            .metric-value {
                font-size: 1.8rem;
                font-weight: 700;
                color: #1f2937;
            }
            .upload-section {
                background: #f0f9ff;
                border: 2px dashed #3b82f6;
                border-radius: 12px;
                padding: 2rem;
                text-align: center;
                margin: 1rem 0;
            }
            .download-section {
                background: #f0fdf4;
                border-radius: 12px;
                padding: 1.5rem;
                margin-top: 1rem;
                border: 1px solid #bbf7d0;
            }
            .stButton button {
                border-radius: 8px;
                font-weight: 600;
                transition: all 0.2s;
            }
            .stButton button:hover {
                transform: translateY(-1px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            }
            div[data-testid="stDataFrame"] {
                border-radius: 8px;
                overflow: hidden;
            }
            .stTabs [data-baseweb="tab-list"] {
                gap: 8px;
            }
            .stTabs [data-baseweb="tab"] {
                border-radius: 8px 8px 0 0;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_page_header(title: str, subtitle: Optional[str] = None, description: Optional[str] = None) -> None:
    load_global_style()
    st.markdown(f'<div class="app-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="app-subtitle">{subtitle}</div>', unsafe_allow_html=True)
    if description:
        st.markdown(f'<div class="app-description">{description}</div>', unsafe_allow_html=True)


def render_metric_card(label: str, value: str, icon: str = "") -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{icon} {value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_upload_section(label: str, help_text: str) -> None:
    st.markdown(
        f"""
        <div class="upload-section">
            <h4 style="color: #1e40af; margin-bottom: 0.5rem;">📤 {label}</h4>
            <p style="color: #64748b; margin: 0;">{help_text}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_download_section() -> None:
    st.markdown('<div class="download-section"><h4 style="color: #166534; margin-bottom: 1rem;">📥 Download Hasil</h4></div>', unsafe_allow_html=True)
