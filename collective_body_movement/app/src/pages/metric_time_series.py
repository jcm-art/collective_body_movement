# Collective Body Movement Application
# Director: Sarah Silverblatt-Buser (https://www.sarahsilverblatt.com/)
# Author: Justin Martin (jcm-art)

import json
import platform
import time
from typing import Dict

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from ..utils import StreamlitPage, AppProfiler
from ..data_management.movement_data import MovementDataManager
from ..data_management.movement_frame import UserMetricFrame


class MetricSeriesPage(StreamlitPage):

    def __init__(self, state):
        print("Initializing MetricsSeriesPage")
        self.state = state
        


    def write(self):
        st.title("Collective Body Metric Time Series")
        