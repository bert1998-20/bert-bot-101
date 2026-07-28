import os
from io import BytesIO
import base64

import requests
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Metric

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors


st.set_page_config(
    page_title="SEO DASHBOARD",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_dotenv()


# =========================
# CSS - COMPLETE FIX
# =========================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #0a0e1a 0%, #1a1f36 50%, #0d1117 100%);
    color: #ffffff;
}

.block-container {
    padding-top: 1rem;
    padding-left: 2rem;
    padding-right: 2rem;
    max-width: 1440px;
    margin: 0 auto;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f1524 0%, #1a2035 100%);
    border-right: 1px solid rgba(255, 255, 255, 0.06);
    padding: 1.5rem 0.5rem;
}

h1, h2, h3, h4, h5, h6, p, label, div {
    color: #2ed070 !important;
    font-family: 'Inter', sans-serif !important;
}

/* ===== SIDEBAR DROPDOWN - COMPLETE FIX ===== */

.stSelectbox {
    margin-bottom: 0.5rem;
}

/* The main selectbox container - DARK BACKGROUND */
.stSelectbox > div {
    background: #1a2035 !important;
    border-radius: 8px !important;
    border: 1px solid rgba(34, 197, 94, 0.3) !important;
}

.stSelectbox > div:hover {
    border-color: rgba(34, 197, 94, 0.6) !important;
}

/* The selected value text - GREEN */
.stSelectbox > div > div {
    color: #22c55e !important;
}

.stSelectbox > div > div > div {
    color: #22c55e !important;
}

.stSelectbox > div > div > div > div {
    color: #22c55e !important;
}

.stSelectbox [data-testid="stMarkdownContainer"] {
    color: #22c55e !important;
}

.stSelectbox [data-baseweb="select"] {
    color: #22c55e !important;
    background: transparent !important;
}

.stSelectbox [data-baseweb="select"] > div {
    color: #22c55e !important;
    background: transparent !important;
}

/* Force all text to green */
.stSelectbox * {
    color: #22c55e !important;
}

/* Dropdown menu - DARK */
.stSelectbox > div > div:last-child {
    background: #0f1524 !important;
    border: 1px solid rgba(34, 197, 94, 0.2) !important;
    border-radius: 8px !important;
    max-height: 300px !important;
    overflow-y: auto !important;
}

/* Dropdown options - GREEN */
.stSelectbox > div > div:last-child div {
    color: #22c55e !important;
    padding: 8px 12px !important;
    background: transparent !important;
}

/* Hover - brighter green */
.stSelectbox > div > div:last-child div:hover {
    background: rgba(34, 197, 94, 0.15) !important;
    color: #4ade80 !important;
}

/* Selected option */
.stSelectbox > div > div:last-child div[aria-selected="true"] {
    background: rgba(34, 197, 94, 0.25) !important;
    color: #4ade80 !important;
}

/* Scrollbar */
.stSelectbox > div > div:last-child::-webkit-scrollbar {
    width: 4px;
}
.stSelectbox > div > div:last-child::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.05);
}
.stSelectbox > div > div:last-child::-webkit-scrollbar-thumb {
    background: rgba(34, 197, 94, 0.3);
    border-radius: 4px;
}

/* ===== DATE INPUT - COMPLETE FIX ===== */

/* The main date input container */
.stDateInput {
    margin-bottom: 0.5rem;
}

/* The date input wrapper */
.stDateInput > div {
    background: #1a2035 !important;
    border-radius: 8px !important;
    border: 1px solid rgba(34, 197, 94, 0.3) !important;
}

.stDateInput > div:hover {
    border-color: rgba(34, 197, 94, 0.6) !important;
}

/* The actual input field */
.stDateInput > div > div {
    background: transparent !important;
}

.stDateInput > div input {
    color: #22c55e !important;
    background: transparent !important;
    font-weight: 500 !important;
}

/* Date input label/placeholder */
.stDateInput label {
    color: #94a3b8 !important;
}

/* ===== DATE PICKER CALENDAR POPUP - CRITICAL FIX ===== */

/* The calendar popover container */
.stDateInput [data-baseweb="popover"] {
    background: #0f1524 !important;
    border: 1px solid rgba(34, 197, 94, 0.2) !important;
    border-radius: 8px !important;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.5) !important;
}

/* The calendar wrapper */
.stDateInput [data-baseweb="calendar"] {
    background: #0f1524 !important;
    border: none !important;
    border-radius: 8px !important;
}

/* ALL text inside the calendar - FORCE GREEN */
.stDateInput [data-baseweb="calendar"] * {
    color: #22c55e !important;
    background: transparent !important;
}

/* Calendar header (month/year) */
.stDateInput [data-baseweb="calendar"] [role="button"] {
    color: #22c55e !important;
}

.stDateInput [data-baseweb="calendar"] [role="button"]:hover {
    color: #4ade80 !important;
    background: rgba(34, 197, 94, 0.1) !important;
}

/* Calendar day cells */
.stDateInput [data-baseweb="calendar"] div[role="gridcell"] {
    color: #22c55e !important;
    background: transparent !important;
}

.stDateInput [data-baseweb="calendar"] div[role="gridcell"]:hover {
    background: rgba(34, 197, 94, 0.15) !important;
    border-radius: 4px !important;
}

/* Selected date in calendar */
.stDateInput [data-baseweb="calendar"] div[aria-selected="true"] {
    background: rgba(34, 197, 94, 0.25) !important;
    color: #4ade80 !important;
    border-radius: 4px !important;
}

/* Today's date highlight */
.stDateInput [data-baseweb="calendar"] div[aria-current="date"] {
    border: 1px solid #22c55e !important;
    border-radius: 4px !important;
}

/* Calendar weekdays header */
.stDateInput [data-baseweb="calendar"] [role="columnheader"] {
    color: #4ade80 !important;
    font-weight: 600 !important;
}

/* Calendar navigation buttons */
.stDateInput [data-baseweb="calendar"] [aria-label*="previous"] {
    color: #22c55e !important;
}

.stDateInput [data-baseweb="calendar"] [aria-label*="next"] {
    color: #22c55e !important;
}

.stDateInput [data-baseweb="calendar"] [aria-label*="previous"]:hover,
.stDateInput [data-baseweb="calendar"] [aria-label*="next"]:hover {
    background: rgba(34, 197, 94, 0.1) !important;
    border-radius: 4px !important;
}

/* Calendar month/year dropdown inside */
.stDateInput [data-baseweb="calendar"] select {
    background: #1a2035 !important;
    color: #22c55e !important;
    border: 1px solid rgba(34, 197, 94, 0.2) !important;
    border-radius: 4px !important;
}

.stDateInput [data-baseweb="calendar"] select option {
    background: #0f1524 !important;
    color: #22c55e !important;
}

/* Force all calendar text to green */
.stDateInput [data-baseweb="popover"] * {
    color: #22c55e !important;
}

/* Time picker if visible */
.stDateInput [data-baseweb="timepicker"] {
    background: #0f1524 !important;
}

.stDateInput [data-baseweb="timepicker"] * {
    color: #22c55e !important;
}

/* ===== SIDEBAR RADIO BUTTONS ===== */

.stRadio {
    margin-bottom: 0.5rem;
}

.stRadio > div {
    background: rgba(255, 255, 255, 0.05) !important;
    border-radius: 8px !important;
    padding: 0.5rem !important;
}

.stRadio label {
    color: #e2e8f0 !important;
    font-weight: 500 !important;
}

.stRadio label:hover {
    color: #22c55e !important;
}

/* ===== SIDEBAR LABELS ===== */
.sidebar-label {
    font-size: 0.7rem;
    color: #94a3b8 !important;
    text-transform: uppercase;
    font-weight: 700;
    letter-spacing: 0.08em;
    margin-bottom: 0.3rem;
    margin-top: 0.5rem;
}

/* ===== DASHBOARD HEADER ===== */
.dashboard-header {
    background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 24px;
    padding: 2rem 2.5rem;
    margin-bottom: 2rem;
    backdrop-filter: blur(20px);
    position: relative;
    overflow: hidden;
}

.dashboard-header::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 500px;
    height: 500px;
    background: radial-gradient(circle, rgba(34, 197, 94, 0.08) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
}

.dashboard-title {
    font-size: 2.5rem;
    font-weight: 900;
    background: linear-gradient(135deg, #ffffff 0%, #94a3b8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.02em;
    margin-bottom: 0.25rem;
}

.dashboard-subtitle {
    color: #94a3b8 !important;
    font-size: 0.95rem;
    font-weight: 500;
    letter-spacing: 0.02em;
}

.dashboard-badge {
    display: inline-block;
    background: rgba(34, 197, 94, 0.15);
    color: #22c55e;
    padding: 0.25rem 1rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    border: 1px solid rgba(34, 197, 94, 0.2);
    margin-top: 0.5rem;
}

/* ===== SECTION TITLES ===== */
.section-title {
    font-size: 1.25rem;
    font-weight: 700;
    margin-top: 2.5rem;
    margin-bottom: 1.25rem;
    padding: 0.75rem 1.25rem;
    background: linear-gradient(135deg, rgba(34, 197, 94, 0.08) 0%, rgba(34, 197, 94, 0.02) 100%);
    border-left: 4px solid #22c55e;
    border-radius: 8px;
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.section-title::before {
    content: '▸';
    color: #22c55e;
    font-size: 1.5rem;
    font-weight: 300;
}

.section-title-ai {
    font-size: 1.3rem;
    font-weight: 700;
    margin-top: 2.5rem;
    margin-bottom: 1.25rem;
    padding: 0.75rem 1.5rem;
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(59, 130, 246, 0.15));
    border: 1px solid rgba(139, 92, 246, 0.2);
    border-radius: 12px;
    display: flex;
    align-items: center;
    gap: 12px;
    backdrop-filter: blur(10px);
}

.section-title-ai::before {
    content: '🤖';
    font-size: 1.5rem;
}

/* ===== KPI CARDS ===== */
.kpi-card {
    background: linear-gradient(145deg, rgba(255,255,255,0.06) 0%, rgba(255,255,255,0.02) 100%);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 16px;
    padding: 1.5rem;
    backdrop-filter: blur(10px);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
    min-height: 120px;
}

.kpi-card:hover {
    transform: translateY(-2px);
    border-color: rgba(255, 255, 255, 0.12);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.kpi-card::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--accent-color, #22c55e), var(--accent-color-secondary, #16a34a));
    opacity: 0.8;
}

.kpi-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    font-weight: 700;
    letter-spacing: 0.08em;
    color: #94a3b8;
    margin-bottom: 0.5rem;
}

.kpi-value {
    font-size: 2rem;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.02em;
    margin-bottom: 0.25rem;
}

.kpi-delta {
    font-size: 0.75rem;
    color: #94a3b8;
    font-weight: 500;
}

.kpi-icon {
    position: absolute;
    right: 1rem;
    top: 1rem;
    font-size: 1.5rem;
    opacity: 0.2;
}

/* ===== AI CARDS ===== */
.ai-card {
    background: linear-gradient(145deg, rgba(139, 92, 246, 0.08), rgba(59, 130, 246, 0.05));
    border: 1px solid rgba(139, 92, 246, 0.15);
    border-radius: 20px;
    padding: 1.5rem;
    backdrop-filter: blur(20px);
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
    min-height: 140px;
}

.ai-card:hover {
    transform: translateY(-6px) scale(1.02);
    border-color: rgba(139, 92, 246, 0.3);
    box-shadow: 0 20px 60px rgba(139, 92, 246, 0.2);
}

.ai-card::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -50%;
    width: 100%;
    height: 100%;
    background: radial-gradient(circle, rgba(139, 92, 246, 0.08), transparent 70%);
    pointer-events: none;
}

.ai-card .value {
    font-size: 2.2rem;
    font-weight: 900;
    background: linear-gradient(135deg, #c4b5fd, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.02em;
}

.ai-card .label {
    font-size: 0.7rem;
    color: #94a3b8;
    text-transform: uppercase;
    font-weight: 700;
    letter-spacing: 0.08em;
}

.ai-card .icon {
    font-size: 2rem;
    opacity: 0.6;
    position: absolute;
    right: 1.2rem;
    top: 1.2rem;
}

.ai-insight-card {
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.9), rgba(30, 41, 59, 0.9));
    border: 1px solid rgba(139, 92, 246, 0.12);
    border-radius: 16px;
    padding: 1.25rem 1.5rem;
    backdrop-filter: blur(20px);
    transition: all 0.3s ease;
}

.ai-insight-card:hover {
    border-color: rgba(139, 92, 246, 0.25);
    transform: translateX(4px);
}

.badge {
    display: inline-block;
    padding: 0.2rem 0.8rem;
    border-radius: 20px;
    font-size: 0.6rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.badge-positive {
    background: rgba(34, 197, 94, 0.15);
    color: #22c55e;
    border: 1px solid rgba(34, 197, 94, 0.2);
}

.badge-negative {
    background: rgba(239, 68, 68, 0.15);
    color: #ef4444;
    border: 1px solid rgba(239, 68, 68, 0.2);
}

.badge-neutral {
    background: rgba(251, 146, 60, 0.15);
    color: #fb923c;
    border: 1px solid rgba(251, 146, 60, 0.2);
}

.badge-info {
    background: rgba(59, 130, 246, 0.15);
    color: #60a5fa;
    border: 1px solid rgba(59, 130, 246, 0.2);
}

/* ===== ALERT CARDS ===== */
.alert-card {
    background: rgba(15, 23, 42, 0.92);
    border: 1px solid rgba(148, 163, 184, 0.22);
    border-left: 5px solid #22c55e;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
    transition: all 0.3s ease;
}

.alert-card:hover {
    border-color: rgba(255, 255, 255, 0.12);
    transform: translateX(4px);
}

.alert-warning {
    border-left-color: #f59e0b;
}

.alert-danger {
    border-left-color: #ef4444;
}

.alert-success {
    border-left-color: #22c55e;
}

.alert-title {
    font-size: 0.9rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 0.25rem;
}

.alert-body {
    font-size: 0.85rem;
    color: #94a3b8;
    line-height: 1.5;
}

/* ===== GLASS CARDS ===== */
.glass-card {
    background: rgba(255, 255, 255, 0.03);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 16px;
    padding: 1.5rem;
    transition: all 0.3s ease;
}

.glass-card:hover {
    border-color: rgba(255, 255, 255, 0.12);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.2);
}

/* ===== TOP PAGE CARDS ===== */
.top-page-card {
    background: linear-gradient(145deg, rgba(255,255,255,0.04) 0%, rgba(255,255,255,0.01) 100%);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 12px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
    transition: all 0.3s ease;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.top-page-card:hover {
    border-color: rgba(255, 255, 255, 0.12);
    transform: translateX(4px);
    background: rgba(255, 255, 255, 0.06);
}

.top-page-rank {
    font-weight: 700;
    color: #22c55e;
    font-size: 0.9rem;
    min-width: 30px;
}

.top-page-url {
    color: #e2e8f0;
    font-size: 0.85rem;
    flex: 1;
    margin: 0 1rem;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.top-page-clicks {
    font-weight: 700;
    color: #facc15;
    font-size: 0.9rem;
    min-width: 60px;
    text-align: right;
}

.top-page-position {
    font-weight: 700;
    color: #34d399;
    font-size: 0.9rem;
    min-width: 50px;
    text-align: right;
}

/* ===== DATA BADGES ===== */
.data-loaded-badge {
    display: inline-block;
    padding: 0.1rem 0.6rem;
    border-radius: 12px;
    font-size: 0.7rem;
    font-weight: 700;
    margin-left: 0.5rem;
}

.data-loaded-badge.success {
    background: rgba(34, 197, 94, 0.2);
    color: #22c55e;
}

.data-loaded-badge.error {
    background: rgba(239, 68, 68, 0.2);
    color: #ef4444;
}

.data-loaded-badge.warning {
    background: rgba(251, 146, 60, 0.2);
    color: #fb923c;
}

/* ===== DOWNLOAD CONTAINERS ===== */
.download-container {
    background: rgba(255, 255, 255, 0.03);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 12px;
    padding: 1rem;
    transition: all 0.3s ease;
    text-align: center;
    height: 100%;
}

.download-container:hover {
    border-color: rgba(255, 255, 255, 0.12);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}

.download-btn {
    width: 100%;
    padding: 0.75rem !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    cursor: pointer;
    transition: all 0.3s ease !important;
    text-align: center;
    display: inline-block;
    text-decoration: none;
    color: white !important;
    letter-spacing: 0.02em;
}

.download-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.2);
}

.download-btn-gsc {
    background: linear-gradient(135deg, #3b82f6, #1d4ed8);
}

.download-btn-ahrefs {
    background: linear-gradient(135deg, #f97316, #c2410c);
}

.download-btn-combined {
    background: linear-gradient(135deg, #22c55e, #16a34a);
}

.download-btn-metrics {
    background: linear-gradient(135deg, #8b5cf6, #6d28d9);
}

.warning-text {
    color: #94a3b8;
    font-size: 0.8rem;
    padding: 0.5rem;
    text-align: center;
}

/* ===== DATA FRAMES ===== */
[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid rgba(255, 255, 255, 0.06);
}

[data-testid="stDataFrame"] thead tr th {
    background: rgba(255, 255, 255, 0.05) !important;
    color: #e2e8f0 !important;
    font-weight: 600 !important;
    font-size: 0.75rem !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding: 0.75rem 1rem !important;
}

[data-testid="stDataFrame"] tbody tr td {
    padding: 0.75rem 1rem !important;
    color: #cbd5e1 !important;
    font-size: 0.85rem !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.04) !important;
}

[data-testid="stDataFrame"] tbody tr:hover {
    background: rgba(255, 255, 255, 0.03) !important;
}

/* ===== ANIMATION ===== */
@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
}

.live-indicator {
    animation: pulse 2s infinite;
}

/* ===== RESPONSIVE ===== */
@media (max-width: 768px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }
    
    .dashboard-title {
        font-size: 1.8rem;
    }
    
    .kpi-value {
        font-size: 1.5rem;
    }
}

/* ===== BUTTONS ===== */
.stButton button {
    background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.6rem 1.5rem !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    transition: all 0.3s ease !important;
    letter-spacing: 0.02em;
    width: 100%;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
}

.stButton button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 20px rgba(37, 99, 235, 0.3) !important;
}

.stDownloadButton button {
    background: linear-gradient(135deg, #22c55e, #16a34a) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.6rem 1.5rem !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    transition: all 0.3s ease !important;
    letter-spacing: 0.02em;
    width: 100%;
    box-shadow: 0 4px 12px rgba(34, 197, 94, 0.2);
}

.stDownloadButton button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 20px rgba(34, 197, 94, 0.3) !important;
}

/* ===== SCROLLBAR ===== */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}

::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.15);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 255, 255, 0.25);
}
</style>
""", unsafe_allow_html=True)

# =========================
# CONFIG
# =========================

SERPAPI_KEY = os.getenv("SERPAPI_KEY") or st.secrets.get("SERPAPI_KEY", "")
AHREFS_API_KEY = os.getenv("AHREFS_API_KEY") or st.secrets.get("AHREFS_API_KEY", "")

SCOPES = [
    "https://www.googleapis.com/auth/webmasters.readonly",
    "https://www.googleapis.com/auth/analytics.readonly"
]

SITES = {
    "bingo101official.org": {
        "gsc_url": "https://bingo101official.org/",
        "ga4_property_id": "399573638",
        "default_keyword": "Bingo 101",
        "category": "Bingo",
        "ahrefs_target": "Bingo 101"
    },
    "bingo101official.net": {
        "gsc_url": "https://bingo101official.net/",
        "ga4_property_id": "399573638",
        "default_keyword": "Bingo 101",
        "category": "Bingo",
        "ahrefs_target": "Bingo 101"
    },
    "rumble-rummy.net": {
        "gsc_url": "http://rumble-rummy.net/",
        "ga4_property_id": "399573638",
        "default_keyword": "rumble rummy",
        "category": "rumble rummy",
        "ahrefs_target": "rumble rummy"
    },
  
}

SITE_METRICS_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ2lub4F_fMu-V_F6EMlqJOHpPIpRWhsKxgpjQOBkkTsppku31ZIIu-0yfWGFo7WVSek2xMYMd_lsop/pub?output=csv"


# =========================
# SIDEBAR
# =========================

st.sidebar.markdown("""
<div style="text-align: center; padding: 0.5rem 0 1.5rem 0;">
    <div style="font-size: 2.2rem; font-weight: 900; background: linear-gradient(135deg, #22c55e, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -0.02em;">SEO</div>
    <div style="font-size: 0.65rem; color: #94a3b8; letter-spacing: 0.15em; text-transform: uppercase; margin-top: 0.25rem;">Command Center</div>
</div>
""", unsafe_allow_html=True)

# Site Selection
st.sidebar.markdown('<div class="sidebar-label">📍 Site Selection</div>', unsafe_allow_html=True)

# Use a different approach - using a list and index
site_list = list(SITES.keys())
selected_index = st.sidebar.selectbox(
    "",
    range(len(site_list)),
    format_func=lambda x: site_list[x],
    label_visibility="collapsed",
    key="site_selector"
)
selected_site = site_list[selected_index]
site_config = SITES[selected_site]

st.sidebar.markdown("---")

# Time Period
st.sidebar.markdown('<div class="sidebar-label">⏱️ Time Period</div>', unsafe_allow_html=True)

from datetime import date, timedelta

period = st.sidebar.radio(
    "",
    ["30 Days", "90 Days", "6 Months", "12 Months"],
    label_visibility="collapsed"
)

today = date.today()

if period == "30 Days":
    default_start = today - timedelta(days=30)
elif period == "90 Days":
    default_start = today - timedelta(days=90)
elif period == "6 Months":
    default_start = today - timedelta(days=180)
else:
    default_start = today - timedelta(days=365)

# Date Range
st.sidebar.markdown('<div class="sidebar-label">📅 Date Range</div>', unsafe_allow_html=True)

# Use columns for better layout
col1, col2 = st.sidebar.columns(2)

with col1:
    gsc_end = st.date_input("End", today, key=f"end_{period}", label_visibility="collapsed")

with col2:
    gsc_start = st.date_input("Start", default_start, key=f"start_{period}", label_visibility="collapsed")

GSC_START_DATE = str(gsc_start)
GSC_END_DATE = str(gsc_end)

previous_start = pd.to_datetime(gsc_start) - pd.Timedelta(days=7)
previous_end = pd.to_datetime(gsc_end) - pd.Timedelta(days=7)

PREVIOUS_START_DATE = str(previous_start.date())
PREVIOUS_END_DATE = str(previous_end.date())

GA4_START_DATE = "30daysAgo"
GA4_END_DATE = "today"

st.sidebar.markdown("---")

# Data Status
st.sidebar.markdown('<div class="sidebar-label">📊 Data Status</div>', unsafe_allow_html=True)

if st.sidebar.button("🔄 Refresh Data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()


# =========================
# AUTH
# =========================

@st.cache_resource
def google_login():
    creds = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES
    )
    return creds


creds = google_login()


# =========================
# HELPERS
# =========================

def safe_number(value, default=0):
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def flatten_dict(data, parent_key="", sep="_"):
    items = []
    if isinstance(data, dict):
        for key, value in data.items():
            new_key = f"{parent_key}{sep}{key}" if parent_key else key
            if isinstance(value, dict):
                items.extend(flatten_dict(value, new_key, sep=sep).items())
            else:
                items.append((new_key, value))
    return dict(items)


def get_value_by_possible_keys(data, possible_keys, default="N/A"):
    if not isinstance(data, dict):
        return default
    flat = flatten_dict(data)
    for key in possible_keys:
        if key in flat:
            return flat[key]
    lowered = {str(k).lower(): v for k, v in flat.items()}
    for key in possible_keys:
        if str(key).lower() in lowered:
            return lowered[str(key).lower()]
    return default


def clean_number(value):
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.replace('₱', '').replace('$', '').replace(',', '').replace(' ', '').strip()
        try:
            return float(cleaned)
        except:
            return 0
    return 0


# =========================
# DATA FUNCTIONS
# =========================

@st.cache_data(ttl=60)
def get_gsc_data(site_url, start_date, end_date):
    service = build("searchconsole", "v1", credentials=creds)
    request = {
        "startDate": start_date,
        "endDate": end_date,
        "dimensions": ["date"],
        "rowLimit": 1000
    }
    response = service.searchanalytics().query(
        siteUrl=site_url,
        body=request
    ).execute()
    rows = []
    for row in response.get("rows", []):
        rows.append({
            "Date": row["keys"][0],
            "Clicks": row.get("clicks", 0),
            "Impressions": row.get("impressions", 0),
            "CTR": round(row.get("ctr", 0) * 100, 2),
            "Position": round(row.get("position", 0), 2)
        })
    return pd.DataFrame(rows)


@st.cache_data(ttl=60)
def get_gsc_queries(site_url, start_date, end_date):
    service = build("searchconsole", "v1", credentials=creds)
    request = {
        "startDate": start_date,
        "endDate": end_date,
        "dimensions": ["query"],
        "rowLimit": 250
    }
    response = service.searchanalytics().query(
        siteUrl=site_url,
        body=request
    ).execute()
    rows = []
    for row in response.get("rows", []):
        rows.append({
            "Keyword": row["keys"][0],
            "Clicks": row.get("clicks", 0),
            "Impressions": row.get("impressions", 0),
            "CTR": round(row.get("ctr", 0) * 100, 2),
            "Position": round(row.get("position", 0), 2)
        })
    return pd.DataFrame(rows)


@st.cache_data(ttl=60)
def get_gsc_pages(site_url, start_date, end_date):
    service = build("searchconsole", "v1", credentials=creds)
    request = {
        "startDate": start_date,
        "endDate": end_date,
        "dimensions": ["page"],
        "rowLimit": 250
    }
    response = service.searchanalytics().query(
        siteUrl=site_url,
        body=request
    ).execute()
    rows = []
    for row in response.get("rows", []):
        rows.append({
            "Page": row["keys"][0],
            "Clicks": row.get("clicks", 0),
            "Impressions": row.get("impressions", 0),
            "CTR": round(row.get("ctr", 0) * 100, 2),
            "Position": round(row.get("position", 0), 2)
        })
    return pd.DataFrame(rows)


@st.cache_data(ttl=60)
def get_ga4_data(property_id):
    client = BetaAnalyticsDataClient(credentials=creds)
    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[
            DateRange(start_date=GA4_START_DATE, end_date=GA4_END_DATE)
        ],
        metrics=[
            Metric(name="sessions"),
            Metric(name="activeUsers"),
            Metric(name="totalUsers"),
            Metric(name="screenPageViews")
        ]
    )
    response = client.run_report(request)
    if not response.rows:
        return {
            "sessions": 0,
            "active_users": 0,
            "total_users": 0,
            "pageviews": 0
        }
    row = response.rows[0]
    return {
        "sessions": int(row.metric_values[0].value),
        "active_users": int(row.metric_values[1].value),
        "total_users": int(row.metric_values[2].value),
        "pageviews": int(row.metric_values[3].value)
    }


@st.cache_data(ttl=60)
def get_metrics_data():
    try:
        df = pd.read_csv(SITE_METRICS_URL)
        if df.empty:
            return pd.DataFrame()
        
        df.columns = df.columns.str.strip()
        
        month_col = None
        reg_col = None
        ftd_col = None
        pl_col = None
        
        for col in df.columns:
            col_lower = col.lower().strip()
            if 'month' in col_lower or 'date' in col_lower:
                month_col = col
            elif 'regist' in col_lower or 'reg' in col_lower:
                reg_col = col
            elif 'ftd' in col_lower:
                ftd_col = col
            elif 'profit' in col_lower or 'loss' in col_lower or 'pl' in col_lower:
                pl_col = col
        
        if month_col:
            df = df.rename(columns={month_col: 'Month'})
        if reg_col:
            df = df.rename(columns={reg_col: 'Registrations'})
        if ftd_col:
            df = df.rename(columns={ftd_col: 'FTD'})
        if pl_col:
            df = df.rename(columns={pl_col: 'Profit/Loss'})
        
        required_cols = ['Month', 'Registrations', 'FTD', 'Profit/Loss']
        for col in required_cols:
            if col not in df.columns:
                df[col] = 0
        
        for col in ['Registrations', 'FTD', 'Profit/Loss']:
            if col in df.columns:
                df[col] = df[col].apply(clean_number)
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        df = df.dropna(subset=['Month'], how='all')
        df = df[df['Month'].astype(str).str.strip() != '']
        
        if df.empty:
            return pd.DataFrame()
        
        st.sidebar.success(f"✅ Metrics loaded: {len(df)} rows")
        return df
        
    except Exception as e:
        st.sidebar.error(f"❌ Error loading metrics: {str(e)}")
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def ahrefs_get(endpoint, params):
    if not AHREFS_API_KEY:
        return None, "Missing AHREFS_API_KEY"
    url = f"https://api.ahrefs.com/v3/site-explorer/{endpoint}"
    headers = {
        "Authorization": f"Bearer {AHREFS_API_KEY}",
        "Accept": "application/json"
    }
    response = requests.get(url, headers=headers, params=params, timeout=45)
    if response.status_code != 200:
        return None, f"Ahrefs API Error {response.status_code}"
    return response.json(), None


@st.cache_data(ttl=86400)
def get_ahrefs_domain_rating(target):
    return ahrefs_get("domain-rating", {
        "target": target,
        "date": GSC_END_DATE,
        "output": "json"
    })


@st.cache_data(ttl=86400)
def get_ahrefs_backlinks(target):
    return ahrefs_get("all-backlinks", {
        "target": target,
        "mode": "domain",
        "limit": 10000,
        "select": "url_from,url_to,domain_rating_source,traffic",
        "output": "json"
    })


@st.cache_data(ttl=86400)
def get_ahrefs_refdomains(target):
    return ahrefs_get("refdomains", {
        "target": target,
        "mode": "domain",
        "limit": 1000,
        "output": "json"
    })


@st.cache_data(ttl=86400)
def get_ahrefs_organic_keywords(target):
    return ahrefs_get("organic-keywords", {
        "target": target,
        "mode": "domain",
        "date": pd.Timestamp.today().strftime("%Y-%m-%d"),
        "country": "ph",
        "limit": 100,
        "select": "keyword,keyword_country,best_position,volume,sum_traffic,best_position_url",
        "output": "json"
    })


def json_to_dataframe(data):
    if not data:
        return pd.DataFrame()
    if isinstance(data, dict):
        for key in ["pages", "keywords", "backlinks", "refdomains", "rows", "items", "data"]:
            if key in data and isinstance(data[key], list):
                return pd.DataFrame(data[key])
        if all(not isinstance(v, (dict, list)) for v in data.values()):
            return pd.DataFrame([data])
        flat = flatten_dict(data)
        return pd.DataFrame([flat])
    if isinstance(data, list):
        return pd.DataFrame(data)
    return pd.DataFrame()


# =========================
# HTML EXPORT FUNCTIONS
# =========================

def dataframe_to_html(df, title, include_index=False):
    if df.empty:
        return f"<p>No {title} data available.</p>"
    df_display = df.copy()
    for col in df_display.columns:
        if df_display[col].dtype in ['float64', 'float32']:
            df_display[col] = df_display[col].apply(lambda x: f"{x:,.2f}" if pd.notna(x) else "N/A")
        elif df_display[col].dtype in ['int64', 'int32']:
            df_display[col] = df_display[col].apply(lambda x: f"{x:,}" if pd.notna(x) else "N/A")
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
            .container {{ max-width: 1400px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
            h1 {{ color: #1a1a2e; border-bottom: 3px solid #22c55e; padding-bottom: 10px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 14px; }}
            th {{ background: #1a1a2e; color: white; padding: 12px; text-align: left; }}
            td {{ padding: 10px 12px; border-bottom: 1px solid #e5e7eb; }}
            tr:hover {{ background: #f0f4ff; }}
            .section {{ margin: 20px 0; border: 1px solid #e5e7eb; border-radius: 8px; padding: 20px; }}
            .badge {{ display: inline-block; padding: 4px 12px; background: #22c55e; color: white; border-radius: 20px; font-size: 12px; }}
            .footer {{ margin-top: 30px; padding: 20px; border-top: 1px solid #e5e7eb; text-align: center; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header" style="display: flex; justify-content: space-between; align-items: center;">
                <h1>{title}</h1>
                <span class="badge">Export Date: {date.today().strftime('%Y-%m-%d')}</span>
            </div>
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #22c55e;">
                <strong>Site:</strong> {selected_site}<br>
                <strong>Date Range:</strong> {GSC_START_DATE} to {GSC_END_DATE}
            </div>
    """
    
    html += f"""
            <div class="section">
                <h2>Data Overview</h2>
                <p><strong>Total Records:</strong> {len(df):,}</p>
                <p><strong>Columns:</strong> {', '.join(df.columns)}</p>
            </div>
            <div class="section">
                <h2>Data Table</h2>
                <div style="overflow-x: auto; max-height: 500px; overflow-y: auto;">
                {df_display.to_html(index=include_index, classes='table')}
                </div>
            </div>
            <div class="footer">
                <p>Generated by SEO Family Dashboard • Data from Google Search Console & Ahrefs</p>
                <p>This report is for internal use only.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html


def create_html_download(df, title, filename_prefix):
    if df.empty:
        return None
    html_content = dataframe_to_html(df, title)
    b64 = base64.b64encode(html_content.encode()).decode()
    href = f'data:text/html;base64,{b64}'
    return href, f"{filename_prefix}_{selected_site}_{date.today().strftime('%Y%m%d')}.html"


# =========================
# LOAD DATA
# =========================

gsc_url = site_config["gsc_url"]
ga4_property_id = site_config["ga4_property_id"]
ahrefs_target = site_config["ahrefs_target"]

# Load GSC Data
try:
    gsc_df = get_gsc_data(gsc_url, GSC_START_DATE, GSC_END_DATE)
    if not gsc_df.empty:
        st.sidebar.markdown(f'<span class="data-loaded-badge success">✅ GSC: {len(gsc_df)} rows</span>', unsafe_allow_html=True)
    else:
        st.sidebar.markdown('<span class="data-loaded-badge warning">⚠️ GSC: No data</span>', unsafe_allow_html=True)
except:
    gsc_df = pd.DataFrame()
    st.sidebar.markdown('<span class="data-loaded-badge error">❌ GSC Error</span>', unsafe_allow_html=True)

try:
    queries_df = get_gsc_queries(gsc_url, GSC_START_DATE, GSC_END_DATE)
    if not queries_df.empty:
        st.sidebar.markdown(f'<span class="data-loaded-badge success">✅ Queries: {len(queries_df)}</span>', unsafe_allow_html=True)
except:
    queries_df = pd.DataFrame()
    st.sidebar.markdown('<span class="data-loaded-badge error">❌ Queries Error</span>', unsafe_allow_html=True)

try:
    previous_queries_df = get_gsc_queries(gsc_url, PREVIOUS_START_DATE, PREVIOUS_END_DATE)
except:
    previous_queries_df = pd.DataFrame()

try:
    pages_df = get_gsc_pages(gsc_url, GSC_START_DATE, GSC_END_DATE)
    if not pages_df.empty:
        st.sidebar.markdown(f'<span class="data-loaded-badge success">✅ Pages: {len(pages_df)}</span>', unsafe_allow_html=True)
except:
    pages_df = pd.DataFrame()
    st.sidebar.markdown('<span class="data-loaded-badge error">❌ Pages Error</span>', unsafe_allow_html=True)

try:
    ga4_data = get_ga4_data(ga4_property_id)
    st.sidebar.markdown(f'<span class="data-loaded-badge success">✅ GA4: {ga4_data["sessions"]:,} sessions</span>', unsafe_allow_html=True)
except:
    ga4_data = {"sessions": 0, "active_users": 0, "total_users": 0, "pageviews": 0}
    st.sidebar.markdown('<span class="data-loaded-badge error">❌ GA4 Error</span>', unsafe_allow_html=True)

# Load Metrics Data
try:
    metrics_df = get_metrics_data()
    if not metrics_df.empty:
        st.sidebar.markdown(f'<span class="data-loaded-badge success">✅ Metrics: {len(metrics_df)} rows</span>', unsafe_allow_html=True)
    else:
        st.sidebar.markdown('<span class="data-loaded-badge warning">⚠️ Metrics: Empty</span>', unsafe_allow_html=True)
except:
    metrics_df = pd.DataFrame()
    st.sidebar.markdown('<span class="data-loaded-badge error">❌ Metrics Error</span>', unsafe_allow_html=True)

serp_df = pd.DataFrame()
serp_error = None

# Load Ahrefs Data
try:
    ahrefs_dr_data, ahrefs_dr_error = get_ahrefs_domain_rating(ahrefs_target)
    if ahrefs_dr_data:
        st.sidebar.markdown('<span class="data-loaded-badge success">✅ Ahrefs DR</span>', unsafe_allow_html=True)
    else:
        st.sidebar.markdown('<span class="data-loaded-badge warning">⚠️ Ahrefs DR</span>', unsafe_allow_html=True)
except:
    ahrefs_dr_data, ahrefs_dr_error = None, "Error"

ahrefs_backlinks_data, ahrefs_backlinks_error = get_ahrefs_backlinks(ahrefs_target)
ahrefs_refdomains_data, ahrefs_refdomains_error = get_ahrefs_refdomains(ahrefs_target)
ahrefs_keywords_data, ahrefs_keywords_error = get_ahrefs_organic_keywords(ahrefs_target)

ahrefs_backlinks_df = json_to_dataframe(ahrefs_backlinks_data)
ahrefs_refdomains_df = json_to_dataframe(ahrefs_refdomains_data)
ahrefs_keywords_df = json_to_dataframe(ahrefs_keywords_data)


# =========================
# CALCULATIONS
# =========================

if not gsc_df.empty:
    total_clicks = int(gsc_df["Clicks"].sum())
    total_impressions = int(gsc_df["Impressions"].sum())
    avg_ctr = round((total_clicks / total_impressions) * 100, 2) if total_impressions else 0
    avg_position = round(gsc_df["Position"].mean(), 2)
else:
    total_clicks = 0
    total_impressions = 0
    avg_ctr = 0
    avg_position = 0

unique_queries = len(queries_df) if not queries_df.empty else 0

# Get metrics from your data
if not metrics_df.empty:
    latest_row = metrics_df.iloc[-1]
    latest_month = str(latest_row['Month']) if pd.notna(latest_row['Month']) else 'N/A'
    latest_registrations = int(latest_row['Registrations']) if pd.notna(latest_row['Registrations']) else 0
    latest_ftd = int(latest_row['FTD']) if pd.notna(latest_row['FTD']) else 0
    latest_profit_loss = float(latest_row['Profit/Loss']) if pd.notna(latest_row['Profit/Loss']) else 0
    
    total_registrations = int(metrics_df['Registrations'].sum()) if 'Registrations' in metrics_df.columns else 0
    total_ftd = int(metrics_df['FTD'].sum()) if 'FTD' in metrics_df.columns else 0
    total_profit_loss = float(metrics_df['Profit/Loss'].sum()) if 'Profit/Loss' in metrics_df.columns else 0
    ftd_rate = (total_ftd / total_registrations * 100) if total_registrations > 0 else 0
    metrics_count = len(metrics_df)
else:
    latest_month = 'N/A'
    latest_registrations = 0
    latest_ftd = 0
    latest_profit_loss = 0
    total_registrations = 0
    total_ftd = 0
    total_profit_loss = 0
    ftd_rate = 0
    metrics_count = 0

health_score = 0

ahrefs_domain_rating = get_value_by_possible_keys(
    ahrefs_dr_data,
    ["domain_rating", "domainRating", "domain_rating_domain_rating", "metrics_domain_rating"],
    "N/A"
)

ahrefs_rank = get_value_by_possible_keys(
    ahrefs_dr_data,
    ["ahrefs_rank", "ahrefsRank", "domain_rating_ahrefs_rank", "metrics_ahrefs_rank"],
    "N/A"
)

if not ahrefs_backlinks_df.empty and "url_from" in ahrefs_backlinks_df.columns:
    ahrefs_refdomains = (
        ahrefs_backlinks_df["url_from"]
        .astype(str)
        .str.extract(r"https?://([^/]+)")[0]
        .nunique()
    )
else:
    ahrefs_refdomains = 0

ahrefs_backlinks_count = len(ahrefs_backlinks_df) if not ahrefs_backlinks_df.empty else 0


def calculate_seo_score(avg_ctr, avg_position, sessions):
    score = 0
    score += min(avg_ctr * 4, 30)
    if avg_position <= 3:
        score += 30
    elif avg_position <= 10:
        score += 22
    elif avg_position <= 20:
        score += 14
    else:
        score += 6
    if sessions >= 1000:
        score += 15
    elif sessions >= 500:
        score += 10
    elif sessions >= 100:
        score += 6
    else:
        score += 2
    return round(min(score, 100), 1)


seo_score = calculate_seo_score(avg_ctr, avg_position, ga4_data["sessions"])
rank_position = "N/A"


# =========================
# KEYWORD WINNER / LOSER TRACKING
# =========================

if not queries_df.empty and not previous_queries_df.empty:
    keyword_compare_df = queries_df.merge(
        previous_queries_df[["Keyword", "Position"]],
        on="Keyword",
        how="inner",
        suffixes=("_Current", "_Previous")
    )
    keyword_compare_df["Position Change"] = (
        keyword_compare_df["Position_Previous"] - keyword_compare_df["Position_Current"]
    ).round(2)
    top_gainers_df = keyword_compare_df[
        keyword_compare_df["Position Change"] > 0
    ].sort_values("Position Change", ascending=False).head(10)
    top_losers_df = keyword_compare_df[
        keyword_compare_df["Position Change"] < 0
    ].sort_values("Position Change", ascending=True).head(10)
else:
    keyword_compare_df = pd.DataFrame()
    top_gainers_df = pd.DataFrame()
    top_losers_df = pd.DataFrame()


# =========================
# AI SEO ALERTS
# =========================

def generate_ai_alerts():
    alerts = []

    if avg_ctr < 3 and total_impressions > 1000:
        alerts.append({
            "level": "danger",
            "title": "⚠️ CTR Opportunity Detected",
            "body": "Your impressions are strong but CTR is low. Review title tags and meta descriptions for top pages."
        })

    if avg_position > 10:
        alerts.append({
            "level": "warning",
            "title": "📊 Ranking Needs Improvement",
            "body": "Average position is outside page one. Prioritize internal links, content refresh, and topical relevance."
        })

    if ga4_data["sessions"] < 100:
        alerts.append({
            "level": "warning",
            "title": "📉 GA4 Traffic Is Still Low",
            "body": "Sessions are below 100 for the selected GA4 range. Compare with GSC clicks to check tracking or engagement gaps."
        })

    if rank_position == "N/A":
        alerts.append({
            "level": "warning",
            "title": "🔍 SERP Visibility Not Found",
            "body": "The selected website was not found in the top 10 organic results for the tracked keyword."
        })

    if ahrefs_dr_error:
        alerts.append({
            "level": "warning",
            "title": "🔗 Ahrefs Data Not Loaded",
            "body": "Ahrefs API key or endpoint access may need checking. GSC and GA4 data are still working."
        })

    if not metrics_df.empty:
        if latest_profit_loss < 0:
            alerts.append({
                "level": "danger",
                "title": f"💰 Negative Profit/Loss: ₱{abs(latest_profit_loss):,.2f}",
                "body": f"The latest month ({latest_month}) shows a loss. Review your financial performance."
            })
        elif latest_profit_loss > 10000:
            alerts.append({
                "level": "success",
                "title": f"💰 Strong Profit: ₱{latest_profit_loss:,.2f}",
                "body": f"Your latest month ({latest_month}) shows strong profitability!"
            })
        
        if latest_registrations < 100 and latest_registrations > 0:
            alerts.append({
                "level": "warning",
                "title": f"📊 Low Registrations: {latest_registrations}",
                "body": f"Latest month ({latest_month}) only had {latest_registrations:,} registrations. Consider increasing marketing."
            })

    if not alerts:
        alerts.append({
            "level": "success",
            "title": "✅ SEO Status Looks Stable",
            "body": "No major warning detected based on current data."
        })

    return alerts


alerts = generate_ai_alerts()


# =========================
# PDF REPORT
# =========================

def generate_pdf_report():
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 50

    pdf.setFillColor(colors.HexColor("#0f172a"))
    pdf.rect(0, 0, width, height, fill=True, stroke=False)

    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(40, y, "SEO PERFORMANCE REPORT")

    y -= 30
    pdf.setFont("Helvetica", 11)
    pdf.setFillColor(colors.HexColor("#cbd5e1"))
    pdf.drawString(40, y, f"Website: {selected_site}")
    y -= 18
    pdf.drawString(40, y, f"Date Range: {GSC_START_DATE} to {GSC_END_DATE}")
    y -= 18
    pdf.drawString(40, y, f"Previous Range: {PREVIOUS_START_DATE} to {PREVIOUS_END_DATE}")

    y -= 45
    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica-Bold", 15)
    pdf.drawString(40, y, "Executive Summary")

    y -= 25
    pdf.setFont("Helvetica", 10)

    summary_items = [
        f"SEO Score: {seo_score}/100",
        f"Total Clicks: {total_clicks:,}",
        f"Total Impressions: {total_impressions:,}",
        f"Average CTR: {avg_ctr}%",
        f"Average Position: {avg_position}",
        f"GA4 Sessions: {ga4_data['sessions']:,}",
        f"Latest Month: {latest_month}",
        f"Latest Registrations: {latest_registrations:,}",
        f"Latest FTD: {latest_ftd:,}",
        f"Latest Profit/Loss: ₱{latest_profit_loss:,.2f}",
        f"FTD Rate: {ftd_rate:.1f}%",
        f"SERP Rank: {rank_position}",
        f"Ahrefs DR: {ahrefs_domain_rating}",
        f"Ahrefs Rank: {ahrefs_rank}",
        f"Ahrefs Referring Domains: {ahrefs_refdomains}",
        f"Ahrefs Backlinks: {ahrefs_backlinks_count}",
    ]

    for item in summary_items:
        pdf.drawString(55, y, item)
        y -= 15

    y -= 15
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(40, y, "Top Keyword Gainers")
    y -= 20
    pdf.setFont("Helvetica", 9)

    if not top_gainers_df.empty:
        for _, row in top_gainers_df.head(7).iterrows():
            pdf.drawString(55, y, f"{row['Keyword']} (+{row['Position Change']})")
            y -= 13
    else:
        pdf.drawString(55, y, "No keyword gainers found.")
        y -= 13

    y -= 15
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(40, y, "Top Keyword Losers")
    y -= 20
    pdf.setFont("Helvetica", 9)

    if not top_losers_df.empty:
        for _, row in top_losers_df.head(7).iterrows():
            pdf.drawString(55, y, f"{row['Keyword']} ({row['Position Change']})")
            y -= 13
    else:
        pdf.drawString(55, y, "No keyword losers found.")
        y -= 13

    y -= 15
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(40, y, "Recommended SEO Actions")
    y -= 18
    pdf.setFont("Helvetica", 9)

    actions = [
        "Review keywords with low CTR but high impressions.",
        "Improve internal links for keywords ranking between positions 4 and 20.",
        "Refresh pages with declining keyword positions.",
        "Review Ahrefs backlinks and referring domains for authority growth.",
        "Continue monitoring performance metrics."
    ]

    for i, action in enumerate(actions, 1):
        pdf.drawString(55, y, f"{i}. {action}")
        y -= 13

    pdf.setFont("Helvetica", 8)
    pdf.setFillColor(colors.HexColor("#94a3b8"))
    pdf.drawRightString(width - 25, 20, "Generated by SEO Family Dashboard")

    pdf.save()
    buffer.seek(0)
    return buffer


# =========================
# HEADER
# =========================

st.markdown(f"""
<div class="dashboard-header">
    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap;">
        <div>
            <div class="dashboard-title">Seo Tracking Dashboard</div>
            <div class="dashboard-subtitle">Performance intelligence & analytics dashboard</div>
            <div style="display: flex; gap: 0.75rem; margin-top: 0.75rem; flex-wrap: wrap;">
                <span class="dashboard-badge live-indicator">● Live</span>
                <span class="dashboard-badge" style="background: rgba(59, 130, 246, 0.15); color: #3b82f6; border-color: rgba(59, 130, 246, 0.2);">● {selected_site}</span>
                <span class="dashboard-badge" style="background: rgba(251, 146, 60, 0.15); color: #fb923c; border-color: rgba(251, 146, 60, 0.2);">● {period}</span>
            </div>
        </div>
        <div style="text-align: right; margin-top: 0.5rem;">
            <div style="font-size: 0.7rem; color: #94a3b8; letter-spacing: 0.05em; text-transform: uppercase;">Last Updated</div>
            <div style="font-size: 0.85rem; color: #e2e8f0; font-weight: 600;">{pd.Timestamp.now().strftime('%B %d, %Y • %H:%M')}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# =========================
# BUSINESS INTELLIGENCE SECTION
# =========================

st.markdown('<div class="section-title-ai"> Bert Bot</div>', unsafe_allow_html=True)

if not metrics_df.empty:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status_class = "badge-positive" if latest_registrations > 100 else "badge-negative" if latest_registrations < 50 else "badge-neutral"
        status_text = "🚀 GROWING" if latest_registrations > 100 else "📉 LOW" if latest_registrations < 50 else "📊 STEADY"
        st.markdown(f"""
        <div class="ai-card">
            <div class="icon">👤</div>
            <div style="margin-top: 0.5rem;">
                <div class="label">Registrations</div>
                <div class="value">{latest_registrations:,}</div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.5rem;">
                    <span style="font-size: 0.75rem; color: #94a3b8;">Total: {total_registrations:,}</span>
                    <span class="badge {status_class}">{status_text}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        status_class = "badge-positive" if latest_ftd > 20 else "badge-negative" if latest_ftd < 10 else "badge-neutral"
        status_text = "HIGH" if latest_ftd > 20 else "📉 LOW" if latest_ftd < 10 else "📊 MODERATE"
        st.markdown(f"""
        <div class="ai-card">
            <div class="icon"></div>
            <div style="margin-top: 0.5rem;">
                <div class="label">First Time Deposits</div>
                <div class="value">{latest_ftd:,}</div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.5rem;">
                    <span style="font-size: 0.75rem; color: #94a3b8;">Rate: {ftd_rate:.1f}%</span>
                    <span class="badge {status_class}">{status_text}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if latest_profit_loss > 0:
            status_class = "badge-positive"
            status_text = "📈 PROFIT"
            icon = "💰"
        elif latest_profit_loss < 0:
            status_class = "badge-negative"
            status_text = "📉 LOSS"
            icon = "⚠️"
        else:
            status_class = "badge-neutral"
            status_text = "⚖️ BREAK-EVEN"
            icon = "📊"
        
        color = "#22c55e" if latest_profit_loss >= 0 else "#ef4444"
        st.markdown(f"""
        <div class="ai-card">
            <div class="icon">{icon}</div>
            <div style="margin-top: 0.5rem;">
                <div class="label">Profit / Loss</div>
                <div class="value" style="background: linear-gradient(135deg, {color}, {color}dd); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">₱{latest_profit_loss:,.2f}</div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.5rem;">
                    <span style="font-size: 0.75rem; color: #94a3b8;">Total: ₱{total_profit_loss:,.2f}</span>
                    <span class="badge {status_class}">{status_text}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="ai-card">
            <div class="icon">📅</div>
            <div style="margin-top: 0.5rem;">
                <div class="label">Latest Month</div>
                <div class="value">{latest_month}</div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.5rem;">
                    <span style="font-size: 0.75rem; color: #94a3b8;">{metrics_count} months tracked</span>
                    <span class="badge badge-info">📊 ACTIVE</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    insights = []
    if latest_registrations > 100:
        insights.append(f"🚀 <strong>Strong growth</strong> with {latest_registrations} new users this month")
    elif latest_registrations < 50 and latest_registrations > 0:
        insights.append(f"⚠️ <strong>Low registration volume</strong> ({latest_registrations}) - consider marketing boost")
    
    if latest_ftd > 20:
        insights.append(f" <strong>Excellent conversion</strong> with {latest_ftd} first-time deposits")
    elif latest_ftd < 10 and latest_ftd > 0:
        insights.append(f"⚠️ <strong>Low FTD</strong> ({latest_ftd}) - review conversion funnel")
    
    if latest_profit_loss > 5000:
        insights.append(f"💰 <strong>Strong profitability</strong> of ₱{latest_profit_loss:,.2f}")
    elif latest_profit_loss < 0:
        insights.append(f"📉 <strong>Loss detected</strong> (₱{abs(latest_profit_loss):,.2f}) - review expenses")
    elif latest_profit_loss == 0:
        insights.append("⚖️ <strong>Break-even</strong> position - look for growth opportunities")
    
    if not insights:
        insights.append("📊 <strong>Stable performance</strong> - continue monitoring key metrics")
    
    st.markdown(f"""
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; margin: 1rem 0;">
        {''.join([f'<div class="ai-insight-card"><span style="font-size: 1.2rem; margin-right: 0.75rem;">💡</span><span style="color: #e2e8f0; font-size: 0.95rem; line-height: 1.6;">{insight}</span></div>' for insight in insights])}
    </div>
    """, unsafe_allow_html=True)
    
    if len(metrics_df) > 1:
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            fig_reg = go.Figure()
            
            fig_reg.add_trace(go.Bar(
                x=metrics_df['Month'],
                y=metrics_df['Registrations'],
                name='Registrations',
                marker=dict(
                    color='#8b5cf6',
                    opacity=0.85,
                    line=dict(color='#8b5cf6', width=1)
                ),
                text=metrics_df['Registrations'],
                textposition='outside',
                textfont=dict(color='#c4b5fd', size=11)
            ))
            
            fig_reg.add_trace(go.Scatter(
                x=metrics_df['Month'],
                y=metrics_df['FTD'],
                name='FTD',
                mode='lines+markers',
                line=dict(color='#22c55e', width=3),
                marker=dict(size=10, color='#22c55e', symbol='diamond'),
                text=metrics_df['FTD'],
                textposition='top center',
                textfont=dict(color='#22c55e', size=11)
            ))
            
            fig_reg.update_layout(
                height=350,
                title="<b>Registrations vs FTD</b>",
                paper_bgcolor="rgba(255,255,255,0.02)",
                plot_bgcolor="rgba(255,255,255,0.02)",
                font=dict(color="#e5e7eb", family="Inter"),
                margin=dict(l=40, r=40, t=50, b=40),
                xaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="Month"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="Count"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5, font=dict(color="#e5e7eb", size=11)),
                hovermode="x unified"
            )
            
            st.plotly_chart(fig_reg, use_container_width=True, config={'displayModeBar': False})
        
        with col_chart2:
            colors_profit = ['#22c55e' if x >= 0 else '#ef4444' for x in metrics_df['Profit/Loss']]
            
            fig_profit = go.Figure()
            
            fig_profit.add_trace(go.Bar(
                x=metrics_df['Month'],
                y=metrics_df['Profit/Loss'],
                name='Profit/Loss',
                marker=dict(
                    color=colors_profit,
                    opacity=0.85,
                    line=dict(color=colors_profit, width=1)
                ),
                text=[f"₱{x:,.2f}" for x in metrics_df['Profit/Loss']],
                textposition='outside',
                textfont=dict(color='#e5e7eb', size=10)
            ))
            
            fig_profit.add_trace(go.Scatter(
                x=metrics_df['Month'],
                y=[0] * len(metrics_df),
                mode='lines',
                name='Break-even',
                line=dict(color='#94a3b8', width=2, dash='dash')
            ))
            
            fig_profit.update_layout(
                height=350,
                title="<b>Monthly Profit/Loss Trend</b>",
                paper_bgcolor="rgba(255,255,255,0.02)",
                plot_bgcolor="rgba(255,255,255,0.02)",
                font=dict(color="#e5e7eb", family="Inter"),
                margin=dict(l=40, r=40, t=50, b=40),
                xaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="Month"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="Amount (₱)", tickprefix="₱"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5, font=dict(color="#e5e7eb", size=11)),
                hovermode="x unified"
            )
            
            st.plotly_chart(fig_profit, use_container_width=True, config={'displayModeBar': False})

else:
    st.warning("⚠️ No monthly metrics data available. Please check your Google Sheet connection.")

st.markdown("---")


# =========================
# SEO KPI CARDS
# =========================

st.markdown('<div class="section-title">SEO Performance</div>', unsafe_allow_html=True)

c1, c2, c3, c4, c5, c6 = st.columns(6)

with c1:
    st.markdown(f"""
    <div class="kpi-card" style="--accent-color: #22c55e;">
        <div class="kpi-icon">🎯</div>
        <div class="kpi-label">SEO Score</div>
        <div class="kpi-value">{seo_score}/100</div>
        <div class="kpi-delta">Overall health</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="kpi-card" style="--accent-color: #10b981;">
        <div class="kpi-icon">👆</div>
        <div class="kpi-label">Clicks</div>
        <div class="kpi-value">{total_clicks:,}</div>
        <div class="kpi-delta">Organic search clicks</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="kpi-card" style="--accent-color: #3b82f6;">
        <div class="kpi-icon">👁️</div>
        <div class="kpi-label">Impressions</div>
        <div class="kpi-value">{total_impressions:,}</div>
        <div class="kpi-delta">Search visibility</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="kpi-card" style="--accent-color: #8b5cf6;">
        <div class="kpi-icon">📊</div>
        <div class="kpi-label">CTR</div>
        <div class="kpi-value">{avg_ctr}%</div>
        <div class="kpi-delta">Click-through rate</div>
    </div>
    """, unsafe_allow_html=True)

with c5:
    st.markdown(f"""
    <div class="kpi-card" style="--accent-color: #f59e0b;">
        <div class="kpi-icon">📈</div>
        <div class="kpi-label">Avg Position</div>
        <div class="kpi-value">{avg_position}</div>
        <div class="kpi-delta">Ranking average</div>
    </div>
    """, unsafe_allow_html=True)

with c6:
    st.markdown(f"""
    <div class="kpi-card" style="--accent-color: #06b6d4;">
        <div class="kpi-icon">🌐</div>
        <div class="kpi-label">Sessions</div>
        <div class="kpi-value">{ga4_data['sessions']:,}</div>
        <div class="kpi-delta">GA4 traffic</div>
    </div>
    """, unsafe_allow_html=True)


# =========================
# AHREFS KPI CARDS
# =========================

st.markdown('<div class="section-title">Authority Metrics</div>', unsafe_allow_html=True)

ah1, ah2, ah3, ah4 = st.columns(4)

with ah1:
    st.markdown(f"""
    <div class="kpi-card" style="--accent-color: #f97316;">
        <div class="kpi-icon">🏆</div>
        <div class="kpi-label">Domain Rating</div>
        <div class="kpi-value">{ahrefs_domain_rating}</div>
        <div class="kpi-delta">Ahrefs authority</div>
    </div>
    """, unsafe_allow_html=True)

with ah2:
    st.markdown(f"""
    <div class="kpi-card" style="--accent-color: #ec4899;">
        <div class="kpi-icon">🌍</div>
        <div class="kpi-label">Ahrefs Rank</div>
        <div class="kpi-value">{ahrefs_rank}</div>
        <div class="kpi-delta">Global authority</div>
    </div>
    """, unsafe_allow_html=True)

with ah3:
    st.markdown(f"""
    <div class="kpi-card" style="--accent-color: #14b8a6;">
        <div class="kpi-icon">🔗</div>
        <div class="kpi-label">Referring Domains</div>
        <div class="kpi-value">{ahrefs_refdomains}</div>
        <div class="kpi-delta">Link authority</div>
    </div>
    """, unsafe_allow_html=True)

with ah4:
    st.markdown(f"""
    <div class="kpi-card" style="--accent-color: #6366f1;">
        <div class="kpi-icon">📎</div>
        <div class="kpi-label">Backlinks</div>
        <div class="kpi-value">{ahrefs_backlinks_count}</div>
        <div class="kpi-delta">Total backlink signal</div>
    </div>
    """, unsafe_allow_html=True)


if ahrefs_dr_error:
    st.warning(ahrefs_dr_error)


# =========================
# AI ALERTS
# =========================

st.markdown('<div class="section-title">Intelligent Alerts</div>', unsafe_allow_html=True)

for alert in alerts:
    css_class = "alert-card"
    if alert["level"] == "warning":
        css_class += " alert-warning"
    elif alert["level"] == "danger":
        css_class += " alert-danger"
    elif alert["level"] == "success":
        css_class += " alert-success"

    st.markdown(f"""
    <div class="{css_class}">
        <div class="alert-title">{alert["title"]}</div>
        <div class="alert-body">{alert["body"]}</div>
    </div>
    """, unsafe_allow_html=True)


# =========================
# PERFORMANCE CHART
# =========================

st.markdown('<div class="section-title">Performance Trend</div>', unsafe_allow_html=True)

if not gsc_df.empty:
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=gsc_df["Date"],
        y=gsc_df["Clicks"],
        mode="lines+markers",
        name="Clicks",
        line=dict(width=3, color="#10b981"),
        fill="tozeroy",
        fillcolor="rgba(16, 185, 129, 0.15)",
        marker=dict(size=6, color="#10b981")
    ))

    fig.add_trace(go.Scatter(
        x=gsc_df["Date"],
        y=gsc_df["Impressions"],
        mode="lines+markers",
        name="Impressions",
        line=dict(width=3, color="#3b82f6"),
        yaxis="y2",
        marker=dict(size=6, color="#3b82f6")
    ))

    fig.update_layout(
        height=400,
        paper_bgcolor="rgba(255,255,255,0.03)",
        plot_bgcolor="rgba(255,255,255,0.02)",
        font=dict(color="#e5e7eb", family="Inter"),
        margin=dict(l=40, r=40, t=40, b=40),
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)", title=dict(text="Date", font=dict(color="#94a3b8", size=12))),
        yaxis=dict(title=dict(text="Clicks", font=dict(color="#94a3b8", size=12)), gridcolor="rgba(255,255,255,0.06)"),
        yaxis2=dict(title=dict(text="Impressions", font=dict(color="#94a3b8", size=12)), overlaying="y", side="right", gridcolor="rgba(255,255,255,0.06)"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor="rgba(0,0,0,0.2)", font=dict(color="#e5e7eb", size=12)),
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
else:
    st.warning("No GSC trend data found.")


# =========================
# TOP PAGES
# =========================

st.markdown('<div class="section-title">🏆 Top Performing Pages</div>', unsafe_allow_html=True)

if not pages_df.empty:
    top_pages = pages_df.sort_values("Clicks", ascending=False).head(10)
    
    fig_pages = go.Figure()
    
    fig_pages.add_trace(go.Bar(
        y=top_pages['Page'].apply(lambda x: x.replace('https://', '').replace('scatter.ph/', '').replace('scatter.ph', 'Home').strip('/')[:30]),
        x=top_pages['Clicks'],
        orientation='h',
        marker=dict(
            color=top_pages['Clicks'],
            colorscale='Greens',
            showscale=True,
            colorbar=dict(title="Clicks")
        ),
        text=top_pages['Clicks'],
        textposition='outside',
        textfont=dict(color='#e5e7eb', size=10)
    ))
    
    fig_pages.update_layout(
        height=400,
        title="<b>Pages by Click Volume</b>",
        paper_bgcolor="rgba(255,255,255,0.02)",
        plot_bgcolor="rgba(255,255,255,0.02)",
        font=dict(color="#e5e7eb", family="Inter"),
        margin=dict(l=100, r=40, t=50, b=40),
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="Clicks"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.06)", title=""),
        hovermode="y unified"
    )
    
    st.plotly_chart(fig_pages, use_container_width=True, config={'displayModeBar': False})
    
    st.markdown("### 🔥 Top 5 Pages")
    for idx, row in top_pages.head(5).iterrows():
        page_name = row['Page'].replace('https://', '').replace('scatter.ph/', '').replace('scatter.ph', '🏠 Home').strip('/')
        if not page_name:
            page_name = "🏠 Home"
        
        st.markdown(f"""
        <div class="top-page-card">
            <span class="top-page-rank">#{idx+1}</span>
            <span class="top-page-url">{page_name}</span>
            <span class="top-page-clicks">👆 {row['Clicks']}</span>
            <span class="top-page-position">📍 {row['Position']}</span>
        </div>
        """, unsafe_allow_html=True)
else:
    st.warning("No page data found.")


# =========================
# KEYWORD WINNERS / LOSERS
# =========================

st.markdown('<div class="section-title">Keyword Movement Analysis</div>', unsafe_allow_html=True)

kw1, kw2 = st.columns(2)

with kw1:
    st.markdown("""
    <div style="background: rgba(34, 197, 94, 0.05); border-radius: 12px; padding: 1rem; border: 1px solid rgba(34, 197, 94, 0.1); margin-bottom: 0.5rem;">
        <h4 style="color: #22c55e; margin: 0; font-size: 0.9rem;">📈 Top Gainers</h4>
    </div>
    """, unsafe_allow_html=True)
    
    if not top_gainers_df.empty:
        fig_gainers = go.Figure()
        fig_gainers.add_trace(go.Bar(
            x=top_gainers_df['Keyword'][:7],
            y=top_gainers_df['Position Change'][:7],
            marker_color='#22c55e',
            text=top_gainers_df['Position Change'][:7],
            textposition='outside',
            textfont=dict(color='#22c55e', size=10)
        ))
        fig_gainers.update_layout(
            height=250,
            title="Position Improvements",
            paper_bgcolor="rgba(255,255,255,0.02)",
            plot_bgcolor="rgba(255,255,255,0.02)",
            font=dict(color="#e5e7eb", size=10),
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis=dict(gridcolor="rgba(255,255,255,0.06)", tickangle=45),
            yaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="Position Change")
        )
        st.plotly_chart(fig_gainers, use_container_width=True, config={'displayModeBar': False})
    else:
        st.info("No keyword gainers found.")

with kw2:
    st.markdown("""
    <div style="background: rgba(239, 68, 68, 0.05); border-radius: 12px; padding: 1rem; border: 1px solid rgba(239, 68, 68, 0.1); margin-bottom: 0.5rem;">
        <h4 style="color: #ef4444; margin: 0; font-size: 0.9rem;">📉 Top Losers</h4>
    </div>
    """, unsafe_allow_html=True)
    
    if not top_losers_df.empty:
        fig_losers = go.Figure()
        fig_losers.add_trace(go.Bar(
            x=top_losers_df['Keyword'][:7],
            y=top_losers_df['Position Change'][:7],
            marker_color='#ef4444',
            text=top_losers_df['Position Change'][:7],
            textposition='outside',
            textfont=dict(color='#ef4444', size=10)
        ))
        fig_losers.update_layout(
            height=250,
            title="Position Declines",
            paper_bgcolor="rgba(255,255,255,0.02)",
            plot_bgcolor="rgba(255,255,255,0.02)",
            font=dict(color="#e5e7eb", size=10),
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis=dict(gridcolor="rgba(255,255,255,0.06)", tickangle=45),
            yaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="Position Change")
        )
        st.plotly_chart(fig_losers, use_container_width=True, config={'displayModeBar': False})
    else:
        st.info("No keyword losers found.")


# =========================
# OPPORTUNITY SECTION
# =========================

st.markdown('<div class="section-title">🎯 Opportunities</div>', unsafe_allow_html=True)

op1, op2 = st.columns(2)

with op1:
    st.markdown("""
    <div style="background: rgba(251, 146, 60, 0.05); border-radius: 12px; padding: 1rem; border: 1px solid rgba(251, 146, 60, 0.1); margin-bottom: 0.5rem;">
        <h4 style="color: #fb923c; margin: 0; font-size: 0.9rem;">💡 CTR Opportunities</h4>
    </div>
    """, unsafe_allow_html=True)

    if not queries_df.empty:
        ctr_opportunity_df = queries_df[
            (queries_df["Impressions"] >= 100) &
            (queries_df["CTR"] < 3)
        ].sort_values("Impressions", ascending=False).head(10)

        if not ctr_opportunity_df.empty:
            fig_ctr = go.Figure()
            fig_ctr.add_trace(go.Scatter(
                x=ctr_opportunity_df['Impressions'],
                y=ctr_opportunity_df['CTR'],
                mode='markers+text',
                marker=dict(
                    size=ctr_opportunity_df['Impressions']/10,
                    color=ctr_opportunity_df['CTR'],
                    colorscale='Oranges',
                    showscale=True,
                    colorbar=dict(title="CTR %")
                ),
                text=ctr_opportunity_df['Keyword'].apply(lambda x: x[:20]),
                textposition='top center',
                textfont=dict(color='#e5e7eb', size=9)
            ))
            fig_ctr.update_layout(
                height=300,
                title="CTR Opportunities by Impressions",
                paper_bgcolor="rgba(255,255,255,0.02)",
                plot_bgcolor="rgba(255,255,255,0.02)",
                font=dict(color="#e5e7eb", size=10),
                margin=dict(l=20, r=20, t=40, b=20),
                xaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="Impressions"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="CTR %")
            )
            st.plotly_chart(fig_ctr, use_container_width=True, config={'displayModeBar': False})
        else:
            st.success("✅ No major CTR opportunity found.")
    else:
        st.warning("No query data available.")

with op2:
    st.markdown("""
    <div style="background: rgba(16, 185, 129, 0.05); border-radius: 12px; padding: 1rem; border: 1px solid rgba(16, 185, 129, 0.1); margin-bottom: 0.5rem;">
        <h4 style="color: #10b981; margin: 0; font-size: 0.9rem;">🎯 Low-Hanging Keywords</h4>
    </div>
    """, unsafe_allow_html=True)

    if not queries_df.empty:
        low_hanging_df = queries_df[
            (queries_df["Position"] >= 4) &
            (queries_df["Position"] <= 20) &
            (queries_df["Impressions"] >= 50)
        ].sort_values("Position", ascending=True).head(10)

        if not low_hanging_df.empty:
            fig_low = go.Figure()
            fig_low.add_trace(go.Scatter(
                x=low_hanging_df['Position'],
                y=low_hanging_df['Impressions'],
                mode='markers+text',
                marker=dict(
                    size=low_hanging_df['Impressions']/5,
                    color=low_hanging_df['Position'],
                    colorscale='Tealgrn',
                    showscale=True,
                    colorbar=dict(title="Position")
                ),
                text=low_hanging_df['Keyword'].apply(lambda x: x[:20]),
                textposition='top center',
                textfont=dict(color='#e5e7eb', size=9)
            ))
            fig_low.update_layout(
                height=300,
                title="Low-Hanging Keywords (Position 4-20)",
                paper_bgcolor="rgba(255,255,255,0.02)",
                plot_bgcolor="rgba(255,255,255,0.02)",
                font=dict(color="#e5e7eb", size=10),
                margin=dict(l=20, r=20, t=40, b=20),
                xaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="Current Position", range=[0, 25]),
                yaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="Impressions")
            )
            st.plotly_chart(fig_low, use_container_width=True, config={'displayModeBar': False})
        else:
            st.success("✅ No low-hanging keywords found.")
    else:
        st.warning("No keyword data available.")


# =========================
# AHREFS TABLES
# =========================

st.markdown('<div class="section-title">🔗 Ahrefs Intelligence</div>', unsafe_allow_html=True)

ah_left, ah_right = st.columns(2)

with ah_left:
    st.markdown("""
    <div style="background: rgba(249, 115, 22, 0.05); border-radius: 12px; padding: 0.75rem 1rem; border: 1px solid rgba(249, 115, 22, 0.1); margin-bottom: 0.5rem;">
        <h4 style="color: #f97316; margin: 0; font-size: 0.85rem;">🔑 Top Organic Keywords</h4>
    </div>
    """, unsafe_allow_html=True)
    
    if ahrefs_keywords_error:
        st.warning(ahrefs_keywords_error)
    elif not ahrefs_keywords_df.empty:
        for idx, row in ahrefs_keywords_df.head(10).iterrows():
            keyword = row.get('keyword', 'N/A')
            volume = row.get('volume', 0)
            position = row.get('best_position', 'N/A')
            st.markdown(f"""
            <div class="top-page-card">
                <span class="top-page-rank">#{idx+1}</span>
                <span class="top-page-url">{keyword[:30]}</span>
                <span style="color: #facc15; font-weight: 600; font-size: 0.8rem; min-width: 60px;">📊 {volume}</span>
                <span style="color: #34d399; font-weight: 600; font-size: 0.8rem; min-width: 50px;">📍 {position}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No Ahrefs organic keyword data returned.")

with ah_right:
    st.markdown("""
    <div style="background: rgba(99, 102, 241, 0.05); border-radius: 12px; padding: 0.75rem 1rem; border: 1px solid rgba(99, 102, 241, 0.1); margin-bottom: 0.5rem;">
        <h4 style="color: #6366f1; margin: 0; font-size: 0.85rem;">🔗 Top Backlinks</h4>
    </div>
    """, unsafe_allow_html=True)
    
    if ahrefs_backlinks_error:
        st.warning(ahrefs_backlinks_error)
    elif not ahrefs_backlinks_df.empty:
        for idx, row in ahrefs_backlinks_df.head(10).iterrows():
            url_from = row.get('url_from', 'N/A')
            if isinstance(url_from, str):
                domain = url_from.replace('https://', '').replace('http://', '').split('/')[0][:30]
            else:
                domain = 'N/A'
            st.markdown(f"""
            <div class="top-page-card">
                <span class="top-page-rank">#{idx+1}</span>
                <span class="top-page-url">{domain}</span>
                <span style="color: #34d399; font-weight: 600; font-size: 0.8rem;">🔗</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No Ahrefs backlink data returned.")


# =========================
# DOWNLOAD SECTION
# =========================

st.markdown('<div class="section-title">📥 Data Export</div>', unsafe_allow_html=True)

st.markdown("""
<div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); border-radius: 16px; padding: 1.5rem; margin: 1rem 0;">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
        <div>
            <h4 style="margin: 0; color: #e5e7eb;">Export Reports</h4>
            <p style="color: #94a3b8; margin: 0.25rem 0 0 0; font-size: 0.85rem;">Download your data as beautifully formatted HTML reports</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# GSC Data Downloads
st.markdown("""
<div style="display: flex; align-items: center; gap: 0.75rem; margin: 1.5rem 0 1rem 0;">
    <span style="font-size: 1.2rem;">📊</span>
    <span style="color: #e5e7eb; font-weight: 700; font-size: 1rem;">Google Search Console</span>
</div>
""", unsafe_allow_html=True)

gsc_col1, gsc_col2, gsc_col3 = st.columns(3)

with gsc_col1:
    with st.container():
        st.markdown('<div class="download-container">', unsafe_allow_html=True)
        if not gsc_df.empty:
            href, filename = create_html_download(gsc_df, "Google Search Console - Daily Performance", "gsc_daily")
            st.markdown(f'<a href="{href}" download="{filename}" target="_blank"><button class="download-btn download-btn-gsc">📊 Daily Data</button></a>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="warning-text">No GSC data available</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

with gsc_col2:
    with st.container():
        st.markdown('<div class="download-container">', unsafe_allow_html=True)
        if not queries_df.empty:
            href, filename = create_html_download(queries_df, "Google Search Console - Top Queries", "gsc_queries")
            st.markdown(f'<a href="{href}" download="{filename}" target="_blank"><button class="download-btn download-btn-gsc">🔍 Queries</button></a>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="warning-text">No query data available</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

with gsc_col3:
    with st.container():
        st.markdown('<div class="download-container">', unsafe_allow_html=True)
        if not pages_df.empty:
            href, filename = create_html_download(pages_df, "Google Search Console - Top Pages", "gsc_pages")
            st.markdown(f'<a href="{href}" download="{filename}" target="_blank"><button class="download-btn download-btn-gsc">📄 Pages</button></a>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="warning-text">No page data available</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# Ahrefs Data Downloads
st.markdown("""
<div style="display: flex; align-items: center; gap: 0.75rem; margin: 2rem 0 1rem 0;">
    <span style="font-size: 1.2rem;">🔗</span>
    <span style="color: #e5e7eb; font-weight: 700; font-size: 1rem;">Ahrefs</span>
</div>
""", unsafe_allow_html=True)

ahrefs_col1, ahrefs_col2, ahrefs_col3 = st.columns(3)

with ahrefs_col1:
    with st.container():
        st.markdown('<div class="download-container">', unsafe_allow_html=True)
        if not ahrefs_keywords_df.empty:
            href, filename = create_html_download(ahrefs_keywords_df, "Ahrefs - Organic Keywords", "ahrefs_keywords")
            st.markdown(f'<a href="{href}" download="{filename}" target="_blank"><button class="download-btn download-btn-ahrefs">🔑 Keywords</button></a>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="warning-text">No keyword data available</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

with ahrefs_col2:
    with st.container():
        st.markdown('<div class="download-container">', unsafe_allow_html=True)
        if not ahrefs_backlinks_df.empty:
            href, filename = create_html_download(ahrefs_backlinks_df, "Ahrefs - Backlinks", "ahrefs_backlinks")
            st.markdown(f'<a href="{href}" download="{filename}" target="_blank"><button class="download-btn download-btn-ahrefs">🔗 Backlinks</button></a>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="warning-text">No backlink data available</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

with ahrefs_col3:
    with st.container():
        st.markdown('<div class="download-container">', unsafe_allow_html=True)
        if not ahrefs_refdomains_df.empty:
            href, filename = create_html_download(ahrefs_refdomains_df, "Ahrefs - Referring Domains", "ahrefs_refdomains")
            st.markdown(f'<a href="{href}" download="{filename}" target="_blank"><button class="download-btn download-btn-ahrefs">🌐 Ref Domains</button></a>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="warning-text">No ref domain data available</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# Monthly Metrics Download
st.markdown("""
<div style="display: flex; align-items: center; gap: 0.75rem; margin: 2rem 0 1rem 0;">
    <span style="font-size: 1.2rem;">📈</span>
    <span style="color: #e5e7eb; font-weight: 700; font-size: 1rem;">Monthly Metrics</span>
</div>
""", unsafe_allow_html=True)

metrics_col1, metrics_col2, metrics_col3 = st.columns([1, 2, 1])

with metrics_col2:
    with st.container():
        st.markdown('<div class="download-container">', unsafe_allow_html=True)
        if not metrics_df.empty:
            href, filename = create_html_download(metrics_df, "Monthly Performance Metrics", "monthly_metrics")
            st.markdown(f'<a href="{href}" download="{filename}" target="_blank"><button class="download-btn download-btn-metrics">📊 Download Monthly Metrics</button></a>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="warning-text">No metrics data available</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# Combined Export
st.markdown("""
<div style="display: flex; align-items: center; gap: 0.75rem; margin: 2rem 0 1rem 0;">
    <span style="font-size: 1.2rem;">📦</span>
    <span style="color: #e5e7eb; font-weight: 700; font-size: 1rem;">Complete Export</span>
</div>
""", unsafe_allow_html=True)

all_data_available = not (gsc_df.empty and queries_df.empty and pages_df.empty and 
                        ahrefs_keywords_df.empty and ahrefs_backlinks_df.empty)

if all_data_available:
    combined_html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
            .container {{ max-width: 1400px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
            h1, h2 {{ color: #1a1a2e; }}
            h1 {{ border-bottom: 3px solid #22c55e; padding-bottom: 10px; }}
            .section {{ margin: 30px 0; border: 1px solid #e5e7eb; border-radius: 8px; padding: 20px; }}
            table {{ width: 100%; border-collapse: collapse; font-size: 13px; margin: 10px 0; }}
            th {{ background: #1a1a2e; color: white; padding: 10px; text-align: left; }}
            td {{ padding: 8px 10px; border-bottom: 1px solid #e5e7eb; }}
            .badge {{ display: inline-block; padding: 4px 12px; background: #22c55e; color: white; border-radius: 20px; font-size: 12px; }}
            .header {{ display: flex; justify-content: space-between; align-items: center; }}
            .footer {{ margin-top: 30px; padding: 20px; border-top: 1px solid #e5e7eb; text-align: center; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Complete SEO Data Export</h1>
                <span class="badge">Export Date: {date.today().strftime('%Y-%m-%d')}</span>
            </div>
            <p><strong>Site:</strong> {selected_site}</p>
            <p><strong>Date Range:</strong> {GSC_START_DATE} to {GSC_END_DATE}</p>
    """
    
    if not metrics_df.empty:
        combined_html += f"""
        <div class="section">
            <h2>📊 Monthly Metrics</h2>
            {metrics_df.to_html(index=False, classes='table')}
        </div>
        """
    
    if not gsc_df.empty:
        combined_html += f"""
        <div class="section">
            <h2>📊 GSC Daily Performance</h2>
            {gsc_df.to_html(index=False, classes='table')}
        </div>
        """
    
    if not queries_df.empty:
        combined_html += f"""
        <div class="section">
            <h2>🔍 GSC Top Queries</h2>
            {queries_df.to_html(index=False, classes='table')}
        </div>
        """
    
    if not pages_df.empty:
        combined_html += f"""
        <div class="section">
            <h2>📄 GSC Top Pages</h2>
            {pages_df.to_html(index=False, classes='table')}
        </div>
        """
    
    if not ahrefs_keywords_df.empty:
        combined_html += f"""
        <div class="section">
            <h2>🔑 Ahrefs Organic Keywords</h2>
            {ahrefs_keywords_df.to_html(index=False, classes='table')}
        </div>
        """
    
    if not ahrefs_backlinks_df.empty:
        combined_html += f"""
        <div class="section">
            <h2>🔗 Ahrefs Backlinks</h2>
            {ahrefs_backlinks_df.to_html(index=False, classes='table')}
        </div>
        """
    
    if not ahrefs_refdomains_df.empty:
        combined_html += f"""
        <div class="section">
            <h2>🌐 Ahrefs Referring Domains</h2>
            {ahrefs_refdomains_df.to_html(index=False, classes='table')}
        </div>
        """
    
    combined_html += """
        <div class="footer">
            <p>Generated by SEO Family Dashboard • Data from Google Search Console & Ahrefs</p>
            <p>This report is for internal use only.</p>
        </div>
        </div>
    </body>
    </html>
    """
    
    b64 = base64.b64encode(combined_html.encode()).decode()
    href = f'data:text/html;base64,{b64}'
    filename = f"complete_seo_data_{selected_site}_{date.today().strftime('%Y%m%d')}.html"
    
    col_combined1, col_combined2, col_combined3 = st.columns([1, 2, 1])
    with col_combined2:
        st.markdown(f'''
        <div class="download-container">
            <a href="{href}" download="{filename}" target="_blank">
                <button class="download-btn download-btn-combined" style="width: 100%; padding: 0.8rem; font-size: 1rem;">
                    📥 Download Complete SEO Data (All Tables)
                </button>
            </a>
        </div>
        ''', unsafe_allow_html=True)
else:
    st.info("No data available for export. Please check your API connections.")


# =========================
# WEEKLY SEO REPORT PDF
# =========================

st.markdown('<div class="section-title">📄 Weekly Report</div>', unsafe_allow_html=True)

col_pdf1, col_pdf2, col_pdf3 = st.columns([1, 2, 1])
with col_pdf2:
    pdf_report = generate_pdf_report()
    st.download_button(
        label="📄 Download SEO Report PDF",
        data=pdf_report,
        file_name=f"{selected_site}-weekly-seo-report.pdf",
        mime="application/pdf",
        use_container_width=True
    )


# =========================
# SERP INTELLIGENCE
# =========================

if serp_error:
    st.warning(serp_error)
elif serp_df is not None and not serp_df.empty:
    st.markdown('<div class="section-title">🔍 SERP Intelligence</div>', unsafe_allow_html=True)
    
    serp_left, serp_right = st.columns([2, 1])

    with serp_left:
        st.dataframe(serp_df, use_container_width=True)

    with serp_right:
        domain_counts = serp_df["Domain"].fillna("Unknown").value_counts().reset_index()
        domain_counts.columns = ["Domain", "Count"]

        fig_domain = px.bar(
            domain_counts,
            x="Count",
            y="Domain",
            orientation="h",
            title="Top SERP Domains"
        )

        fig_domain.update_layout(
            height=420,
            paper_bgcolor="rgba(255,255,255,0.03)",
            plot_bgcolor="rgba(255,255,255,0.02)",
            font=dict(color="#e5e7eb", family="Inter"),
            margin=dict(l=20, r=20, t=50, b=20),
            xaxis=dict(gridcolor="rgba(255,255,255,0.06)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.06)")
        )

        st.plotly_chart(fig_domain, use_container_width=True, config={'displayModeBar': False})
else:
    st.warning("No SERP data found.")


# =========================
# SCORECARDS
# =========================

st.markdown('<div class="section-title">Performance Scorecard</div>', unsafe_allow_html=True)

s1, s2, s3, s4 = st.columns(4)

with s1:
    st.markdown(f"""
    <div class="glass-card" style="border-left: 4px solid #8b5cf6;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                <div style="font-size: 0.7rem; color: #94a3b8; text-transform: uppercase; font-weight: 700; letter-spacing: 0.08em;">GSC Visibility</div>
                <div style="font-size: 2rem; font-weight: 800; color: #ffffff; margin: 0.5rem 0;">{total_impressions:,}</div>
            </div>
            <div style="font-size: 1.5rem; opacity: 0.3;">👁️</div>
        </div>
        <div style="display: flex; justify-content: space-between; padding-top: 0.5rem; border-top: 1px solid rgba(255,255,255,0.06);">
            <div><span style="color: #94a3b8; font-size: 0.75rem;">CTR</span> <span style="color: #facc15; font-weight: 600; margin-left: 0.5rem;">{avg_ctr}%</span></div>
            <div><span style="color: #94a3b8; font-size: 0.75rem;">Position</span> <span style="color: #34d399; font-weight: 600; margin-left: 0.5rem;">{avg_position}</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with s2:
    st.markdown(f"""
    <div class="glass-card" style="border-left: 4px solid #3b82f6;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                <div style="font-size: 0.7rem; color: #94a3b8; text-transform: uppercase; font-weight: 700; letter-spacing: 0.08em;">GA4 Traffic</div>
                <div style="font-size: 2rem; font-weight: 800; color: #ffffff; margin: 0.5rem 0;">{ga4_data['sessions']:,}</div>
            </div>
            <div style="font-size: 1.5rem; opacity: 0.3;">🌐</div>
        </div>
        <div style="display: flex; justify-content: space-between; padding-top: 0.5rem; border-top: 1px solid rgba(255,255,255,0.06);">
            <div><span style="color: #94a3b8; font-size: 0.75rem;">Users</span> <span style="color: #facc15; font-weight: 600; margin-left: 0.5rem;">{ga4_data['active_users']:,}</span></div>
            <div><span style="color: #94a3b8; font-size: 0.75rem;">Pageviews</span> <span style="color: #34d399; font-weight: 600; margin-left: 0.5rem;">{ga4_data['pageviews']:,}</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with s3:
    st.markdown(f"""
    <div class="glass-card" style="border-left: 4px solid #f59e0b;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                <div style="font-size: 0.7rem; color: #94a3b8; text-transform: uppercase; font-weight: 700; letter-spacing: 0.08em;">Keyword Demand</div>
                <div style="font-size: 2rem; font-weight: 800; color: #ffffff; margin: 0.5rem 0;">{unique_queries:,}</div>
            </div>
            <div style="font-size: 1.5rem; opacity: 0.3;">🔍</div>
        </div>
        <div style="display: flex; justify-content: space-between; padding-top: 0.5rem; border-top: 1px solid rgba(255,255,255,0.06);">
            <div><span style="color: #94a3b8; font-size: 0.75rem;">Clicks</span> <span style="color: #facc15; font-weight: 600; margin-left: 0.5rem;">{total_clicks:,}</span></div>
            <div><span style="color: #94a3b8; font-size: 0.75rem;">Rank</span> <span style="color: #34d399; font-weight: 600; margin-left: 0.5rem;">{rank_position}</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with s4:
    profit_color = "#22c55e" if latest_profit_loss >= 0 else "#ef4444"
    st.markdown(f"""
    <div class="glass-card" style="border-left: 4px solid #22c55e;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                <div style="font-size: 0.7rem; color: #94a3b8; text-transform: uppercase; font-weight: 700; letter-spacing: 0.08em;">Latest Performance</div>
                <div style="font-size: 2rem; font-weight: 800; color: #ffffff; margin: 0.5rem 0;">{latest_registrations:,}</div>
            </div>
            <div style="font-size: 1.5rem; opacity: 0.3;">📊</div>
        </div>
        <div style="display: flex; justify-content: space-between; padding-top: 0.5rem; border-top: 1px solid rgba(255,255,255,0.06);">
            <div><span style="color: #94a3b8; font-size: 0.75rem;">FTD</span> <span style="color: #facc15; font-weight: 600; margin-left: 0.5rem;">{latest_ftd:,}</span></div>
            <div><span style="color: #94a3b8; font-size: 0.75rem;">P/L</span> <span style="color: {profit_color}; font-weight: 600; margin-left: 0.5rem;">₱{latest_profit_loss:,.2f}</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# =========================
# HIDDEN DATA TABLES
# =========================

with st.expander("📊 View Raw Data Tables (Hidden by Default)", expanded=False):
    st.markdown("### Daily GSC Data")
    if not gsc_df.empty:
        st.dataframe(gsc_df, use_container_width=True)
    else:
        st.warning("No daily GSC data found.")
    
    st.markdown("### Top Queries")
    if not queries_df.empty:
        st.dataframe(queries_df, use_container_width=True)
    else:
        st.warning("No query data found.")
    
    st.markdown("### Top Pages")
    if not pages_df.empty:
        st.dataframe(pages_df, use_container_width=True)
    else:
        st.warning("No page data found.")
