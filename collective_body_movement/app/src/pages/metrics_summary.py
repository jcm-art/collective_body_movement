# Collective Body Movement Application
# Director: Sarah Silverblatt-Buser (https://www.sarahsilverblatt.com/)
# Author: Justin Martin (jcm-art)

import streamlit as st

from ..utils import StreamlitPage

class MetricsSummaryPage(StreamlitPage):

    def __init__(self, state):
        self.state = state

    def write(self):
        st.title("Collective Body Metrics Summary")

        st.header("[Under Construction]")
        # Example of how to use state - https://github.com/ash2shukla/streamlit-heroku/blob/master/app/src/pages/page1.py