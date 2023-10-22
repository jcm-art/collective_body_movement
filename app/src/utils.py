# Collective Body Movement Application
# Director: Sarah Silverblatt-Buser (https://www.sarahsilverblatt.com/)
# Author: Justin Martin (jcm-art)

import streamlit as st
from abc import ABC, abstractmethod

class StreamlitPage(ABC):
    @abstractmethod
    def write(self):
        pass