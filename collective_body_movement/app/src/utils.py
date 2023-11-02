# Collective Body Movement Application
# Director: Sarah Silverblatt-Buser (https://www.sarahsilverblatt.com/)
# Author: Justin Martin (jcm-art)

import time

import streamlit as st
from abc import ABC, abstractmethod

class StreamlitPage(ABC):
    @abstractmethod
    def write(self):
        pass

class AppProfiler:

    def __init__(self, profile_app=True) -> None:
        self.profile_app = profile_app
        self.start_time = time.time()
        self.time_dict = {}

    def start_timer(self):
        if self.profile_app:
            self.start_time = time.time()

    def end_timer(self, label: str):
        if self.profile_app:
            time_result = time.time() - self.start_time
            self.time_dict[label] = time_result
            print(f"{label} took {time_result} seconds")

    def write_timing(self):
        if self.profile_app:
            with open("timing.json", "w") as outfile: 
                json.dump(self.time_dict, outfile)

    def print_timing(self):
        if self.profile_app:
            print(self.time_dict)