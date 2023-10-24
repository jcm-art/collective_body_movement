# Collective Body Movement Application
# Director: Sarah Silverblatt-Buser (https://www.sarahsilverblatt.com/)
# Author: Justin Martin (jcm-art)

from typing import Dict, Type

from .user_metrics import MetricsAnalysisPage
from . metrics_summary import MetricsSummaryPage
from ..utils import StreamlitPage


CB_PAGE_MAP: Dict[str, Type[StreamlitPage]] = {
    "User Metrics": MetricsAnalysisPage,
    "Metrics Summary": MetricsSummaryPage,
}

__all__ = ["CB_PAGE_MAP"]