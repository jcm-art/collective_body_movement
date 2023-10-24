# Collective Body Movement Application
# Director: Sarah Silverblatt-Buser (https://www.sarahsilverblatt.com/)
# Author: Justin Martin (jcm-art)

import streamlit as st

from src.pages import CB_PAGE_MAP
from src.state import get_state, provide_state

@provide_state()
def main(state=None):
    current_page = st.sidebar.radio("Go To", list(CB_PAGE_MAP))
    CB_PAGE_MAP[current_page](state=state).write()

if __name__ == "__main__":
    main()