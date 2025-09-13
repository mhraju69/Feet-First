# utils/renderers.py
from rest_framework.renderers import BaseRenderer

class ExcelRenderer(BaseRenderer):
    media_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    format = 'xlsx'
    charset = None
    render_style = 'binary'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        # If DRF returns error dict, encode as JSON-style string (avoid frontend break)
        if isinstance(data, dict):
            import json
            return json.dumps(data).encode("utf-8")
        return data