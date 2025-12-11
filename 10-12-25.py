
class PortalEmployeeProfileController(http.Controller):

    @http.route(['/my/profile'], type='http', auth='user', website=True)
    def portal_employee_profile(self, **kwargs):
        user = request.env.user

        # Fetch employee record
        employee = (
            request.env['hr.employee']
            .sudo()
            .search([('user_id', '=', user.id)], limit=1)
        )

        if not employee:
            return request.redirect('/')
        

        _logger.info("Birthday: %s", employee.birthday)
        _logger.info("Place of Birth: %s", employee.place_of_birth)
        _logger.info("Identification No: %s", employee.identification_id)
        _logger.info("Passport No: %s", employee.passport_id) 
        _logger.info("Disabled: %s", employee.disabled)
     
       
       

        # Render template with full employee context
        return request.render("portal_login.portal_employee_profile", {
            'employee': employee,
          
        })

    @http.route(['/my/profile/update'], type='http', auth='user', methods=['POST'], website=True ,  csrf=True)
    def portal_employee_profile_update(self, **kwargs):
        user = request.env.user

        employee = (
            request.env['hr.employee']
            .sudo()
            .search([('user_id', '=', user.id)], limit=1)
        )
        
        
        if employee:

            vals = {
                'mobile_phone': kwargs.get('mobile_phone'),
                'work_email': kwargs.get('work_email'),
                'private_email': kwargs.get('private_email'),
                'private_phone': kwargs.get('private_phone'),
                'emergency_contact': kwargs.get('emergency_contact'),
                'emergency_phone': kwargs.get('emergency_phone'),
                'marital': kwargs.get('marital'),
                'children': int(kwargs.get('children')) if kwargs.get('children') else 0,
                'certificate': kwargs.get('certificate'),
                'study_field': kwargs.get('study_field'),
                'passport_id': kwargs.get('passport_id'),

                # Address
                'private_street': kwargs.get('private_street'),
                'private_street2': kwargs.get('private_street2'),
                'private_city': kwargs.get('private_city'),
                'private_zip': kwargs.get('private_zip'),
                'private_state_id': kwargs.get('private_state_id'),
                'private_country_id': kwargs.get('private_country_id'),
            }
            
            file = request.httprequest.files.get('profile_image')
            if file:
                image_data = file.read()
                if image_data:
                    vals['image_1920'] = base64.b64encode(image_data)

            employee.sudo().write(vals)
            
        return request.redirect('/my/profile')
    
    
    
    
    
    
    
    
    
    
    <odoo>
    <template id="portal_employee_profile" name="Portal Employee Profile">
        <t t-call="portal.portal_layout">

            <div class="container py-4">


                <!-- PAGE TITLE -->
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h3 class="fw-bold">My Profile</h3>
                </div>

                <!-- CARD -->
                <div class="card shadow-sm border-0">
                    <div class="card-body">

                        <form action="/my/profile/update" method="POST" enctype="multipart/form-data">
                            <input type="hidden" name="csrf_token" t-att-value="request.csrf_token()"/>
                            <!-- EMPLOYEE HEADER SECTION -->
                            <div class="text-center mb-4">

                                <t t-if="employee.image_1920">
                                    <img t-att-src="'data:image/png;base64,%s' % employee.image_1920.decode()" class="rounded-circle shadow" style="width:130px;height:130px;object-fit:cover;" />
                                </t>
                                <t t-else="">
                                    <div class="rounded-circle bg-secondary text-white d-flex justify-content-center align-items-center shadow" style="width:130px;height:130px;font-size:40px;">
                                        <i class="fa fa-user"></i>
                                    </div>
                                </t>

                                <h4 class="fw-bold mt-3" t-esc="employee.name" />
                                <p class="text-muted" t-esc="employee.job_title" />
                                <div class="mt-3">
                                    <input type="file" name="profile_image" class="form-control" accept="image/*"/>
                                </div>
                            </div>

                            <hr/>

                            <!-- READ-ONLY WORK INFO -->
                            <h5 class="fw-semibold mb-3">Work Information</h5>

                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label fw-semibold">Work Email</label>
                                    <p class="form-control-plaintext border rounded p-2 bg-light">
                                        <t t-esc="employee.work_email or 'N/A'"/>
                                    </p>
                                </div>

                                <div class="col-md-6 mb-3">
                                    <label class="form-label fw-semibold">Department</label>
                                    <p class="form-control-plaintext border rounded p-2 bg-light">
                                        <t t-esc="employee.department_id.name or 'N/A'"/>
                                    </p>
                                </div>
                            </div>

                            <hr/>

                            <!-- PERSONAL CONTACT SECTION -->
                            <h5 class="fw-semibold mb-3">Contact Information</h5>

                            <div class="row">

                                <div class="col-md-6 mb-3">
                                    <label class="form-label fw-semibold">Mobile Phone</label>
                                    <input class="form-control" name="mobile_phone" t-att-value="employee.mobile_phone"/>
                                </div>

                                <div class="col-md-6 mb-3">
                                    <label class="form-label fw-semibold">Private Phone</label>
                                    <input class="form-control" name="private_phone" t-att-value="employee.private_phone"/>
                                </div>

                                <div class="col-md-6 mb-3">
                                    <label class="form-label fw-semibold">Private Email</label>
                                    <input class="form-control" name="private_email" t-att-value="employee.private_email"/>
                                </div>

                            </div>

                            <hr/>

                            <!-- ADDRESS SECTION -->
                            <h5 class="fw-semibold mb-3">Address</h5>

                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label fw-semibold">Street</label>
                                    <input class="form-control" name="private_street" t-att-value="employee.private_street"/>
                                </div>

                                <div class="col-md-6 mb-3">
                                    <label class="form-label fw-semibold">Street 2</label>
                                    <input class="form-control" name="private_street2" t-att-value="employee.private_street2"/>
                                </div>

                                <div class="col-md-4 mb-3">
                                    <label class="form-label fw-semibold">City</label>
                                    <input class="form-control" name="private_city" t-att-value="employee.private_city"/>
                                </div>

                                <div class="col-md-4 mb-3">
                                    <label class="form-label fw-semibold">State</label>
                                    <input class="form-control" name="private_state_id" t-att-value="employee.private_state_id.id if employee.private_state_id else ''"/>
                                </div>

                                <div class="col-md-2 mb-3">
                                    <label class="form-label fw-semibold">ZIP</label>
                                    <input class="form-control" name="private_zip" t-att-value="employee.private_zip"/>
                                </div>

                                <div class="col-md-2 mb-3">
                                    <label class="form-label fw-semibold">Country</label>
                                    <input class="form-control" name="private_country_id" t-att-value="employee.private_country_id.id if employee.private_country_id else ''"/>
                                </div>
                            </div>

                            <hr/>

                            <!-- PERSONAL INFO -->
                            <h5 class="fw-semibold mb-3">Personal Details</h5>

                            <div class="row">

                                <div class="col-md-4 mb-3">
                                    <label class="form-label fw-semibold">Marital Status</label>
                                    <select class="form-select" name="marital">
                                        <option value="single" t-att-selected="employee.marital=='single'">Single</option>
                                        <option value="married" t-att-selected="employee.marital=='married'">Married</option>
                                        <option value="divorced" t-att-selected="employee.marital=='divorced'">Divorced</option>
                                        <option value="widower" t-att-selected="employee.marital=='widower'">Widower</option>
                                    </select>
                                </div>

                                <div class="col-md-4 mb-3">
                                    <label class="form-label fw-semibold">Children</label>
                                    <input type="number" name="children" class="form-control" t-att-value="employee.children"/>
                                </div>

                                <!-- Birthday (Read-only) -->
                                <div class="col-md-6 mb-3">
                                    <label class="form-label fw-semibold">Birthday</label>
                                    <p class="form-control-plaintext border rounded p-2 bg-light">
                                        <t t-esc="employee.birthday or 'N/A'"/>
                                    </p>
                                </div>
                                <!-- Place of Birth (Read-only) -->
                                <div class="col-md-6 mb-3">
                                    <label class="form-label fw-semibold">Place of Birth</label>
                                    <p class="form-control-plaintext border rounded p-2 bg-light">
                                        <t t-esc="employee.place_of_birth or 'N/A'"/>
                                    </p>
                                </div>
                                <!-- Identification No (Read-only) -->
                                <div class="col-md-6 mb-3">
                                    <label class="form-label fw-semibold">Identification No</label>
                                    <p class="form-control-plaintext border rounded p-2 bg-light">
                                        <t t-esc="employee.identification_id or 'N/A'"/>
                                    </p>
                                </div>
                                <!-- Passport No (Editable) -->
                                <div class="col-md-6 mb-3">
                                    <label class="form-label fw-semibold">Passport No</label>
                                    <input type="text" class="form-control" name="passport_id" t-att-value="employee.passport_id"/>
                                </div>
                            </div>
                            <!-- EDUCATION -->
                            <h5 class="fw-semibold mb-3">Educational Background</h5>

                            <div class="row">

                                <div class="col-md-6 mb-3">
                                    <label class="form-label fw-semibold">Certificate Level</label>
                                    <input class="form-control" name="certificate" t-att-value="employee.certificate"/>
                                </div>

                                <div class="col-md-6 mb-3">
                                    <label class="form-label fw-semibold">Field of Study</label>
                                    <input class="form-control" name="study_field" t-att-value="employee.study_field"/>
                                </div>

                            </div>

                            <hr/>

                            <!-- EMERGENCY -->
                            <h5 class="fw-semibold mb-3">Emergency Contact</h5>

                            <div class="row">

                                <div class="col-md-6 mb-3">
                                    <label class="form-label fw-semibold">Contact Name</label>
                                    <input class="form-control" name="emergency_contact" t-att-value="employee.emergency_contact"/>
                                </div>

                                <div class="col-md-6 mb-3">
                                    <label class="form-label fw-semibold">Contact Phone</label>
                                    <input class="form-control" name="emergency_phone" t-att-value="employee.emergency_phone"/>
                                </div>

                            </div>

                            <div class="text-end mt-4">
                                <button class="btn btn-primary px-4" type="submit">Update Profile</button>
                            </div>

                        </form>
                    </div>
                </div>

            </div>

        </t>
    </template>
</odoo>





