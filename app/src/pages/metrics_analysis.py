# Collective Body Movement Application
# Director: Sarah Silverblatt-Buser (https://www.sarahsilverblatt.com/)
# Author: Justin Martin (jcm-art)

import streamlit as st

from ..utils import StreamlitPage

class MetricsAnalysisPage(StreamlitPage):

    def __init__(self, state):
        self.state = state

    def write(self):
        st.title("Collective Body Movement Analysis")

        # Example of how to use state - https://github.com/ash2shukla/streamlit-heroku/blob/master/app/src/pages/page1.py