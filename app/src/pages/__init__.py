# Collective Body Movement Application
# Director: Sarah Silverblatt-Buser (https://www.sarahsilverblatt.com/)
# Author: Justin Martin (jcm-art)

from typing import Dict, Type

from .metrics_analysis import MetricsAnalysisPage
from ..utils import StreamlitPage


CB_PAGE_MAP: Dict[str, Type[StreamlitPage]] = {
    "Metrics Analysis": MetricsAnalysisPage,
}

__all__ = ["CB_PAGE_MAP"]