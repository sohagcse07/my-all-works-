

from odoo import models, fields, api


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    in_location_map = fields.Html(
        string="Check In Location",
        compute='_compute_location_map',
        sanitize=False,
        store=False,
    )
    out_location_map = fields.Html(
        string="Check Out Location",
        compute='_compute_location_map',
        sanitize=False,
        store=False,
    )

    def _make_location_html(self, location_str):
        if not location_str:
            return False

        parts = location_str.split(' | ', 1)
        coords = parts[0].strip()
        address = parts[1].strip() if len(parts) > 1 else coords

        try:
            lat, lon = coords.split(',')
            float(lat.strip()), float(lon.strip())  
            map_url = f"https://www.google.com/maps?q={lat.strip()},{lon.strip()}"
            label = address[:60] + ('...' if len(address) > 60 else '')
            return (
                f'<a href="{map_url}" target="_blank" title="{address}">'
                f'<i class="fa fa-map-marker text-danger"/> {label}'
                f'</a>'
            )
        except Exception:
            return location_str

    @api.depends('in_location', 'out_location')
    def _compute_location_map(self):
        for rec in self:
            rec.in_location_map = self._make_location_html(rec.in_location)
            rec.out_location_map = self._make_location_html(rec.out_location)
