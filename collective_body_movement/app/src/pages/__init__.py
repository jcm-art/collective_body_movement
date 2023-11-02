# Collective Body Movement Application
# Director: Sarah Silverblatt-Buser (https://www.sarahsilverblatt.com/)
# Author: Justin Martin (jcm-art)

from typing import Dict, Type

from . metrics_summary import MetricsSummaryPage
from .user_movement import MovementExplorerPage
from ..utils import StreamlitPage


CB_PAGE_MAP: Dict[str, Type[StreamlitPage]] = {
    "Metrics Summary": MetricsSummaryPage,
    "User Movement Exploration": MovementExplorerPage,
}

__all__ = ["CB_PAGE_MAP"]