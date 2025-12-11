
class PortalAttendance(http.Controller):

    @http.route('/portal/attendance/check_in', auth='user')
    def portal_check_in(self):
        employee = request.env.user.employee_id
         # Permission check
         
        if not employee or not employee.allow_manual_attendance:
            request.session['portal_status'] = ("danger", "You are not allowed to mark attendance.")
            return request.redirect('/my')

        # Auto check in
        request.env['hr.attendance'].sudo().create({
            'employee_id': employee.id,
            'check_in': fields.Datetime.now(),
        })
        request.session['portal_status'] = ("success", "You have successfully Checked In.")
        return request.redirect('/my')

    @http.route('/portal/attendance/check_out', auth='user')
    def portal_check_out(self):
        employee = request.env.user.employee_id
        
        
        if not employee or not employee.allow_manual_attendance:
            request.session['portal_status'] = ("danger", "You are not allowed to mark attendance.")
            return request.redirect('/my')

        # Last open attendance record
        attendance = request.env['hr.attendance'].sudo().search([
            ('employee_id', '=', employee.id),
            ('check_out', '=', False)
        ], limit=1, order='check_in desc')

        if attendance:
            attendance.sudo().write({
                'check_out': fields.Datetime.now()
            })
            request.session['portal_status'] = ("success", "You have successfully Checked Out.")
        else:
            request.session['portal_status'] = ("danger", "No active check-in found!")


        return request.redirect('/my')










<div class="col-md-4 text-end">
                            <t t-if="user.employee_id.allow_manual_attendance">
                                <button class="btn btn-success" id="btn_check_in">Check In</button>
                                <button class="btn btn-danger" id="btn_check_out">Check Out</button>
                            </t>
                            <t t-if="not user.employee_id.allow_manual_attendance">
                                <small class="text-muted">Manual Attendance Disabled</small>
                            </t>

                                <t t-if="request.session.get('portal_status')">
                                    <div t-attf-class="alert alert-{{ request.session['portal_status'][0] }} mt-2">
                                        <t t-esc="request.session['portal_status'][1]"/>
                                    </div>
                                    <t t-set="x" t-value="request.session.pop('portal_status')"/>
                                </t>
                              <script>
                                document.getElementById("btn_check_in").onclick = function () {
                                    window.location.href = "/portal/attendance/check_in";
                                };
                                document.getElementById("btn_check_out").onclick = function () {
                                    window.location.href = "/portal/attendance/check_out";
                                };
                            </script>
                        </div>