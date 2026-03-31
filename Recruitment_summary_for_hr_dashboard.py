@http.route('/hr/dashboard/recruitment_summary', type='json', auth='user', methods=['POST'], csrf=False)
def get_recruitment_summary(self, company_id=None, dept_id=None, **kwargs):
    try:
        env   = request.env
        today = date.today()

 
        IrModel = env['ir.model'].sudo()
        has_recruitment = IrModel.search([('model', '=', 'hr.applicant')], limit=1)
        if not has_recruitment:
            return {'has_recruitment': False}

        #Dates 
        month_start = today.replace(day=1)
        month_end   = (month_start + relativedelta(months=1)) - timedelta(days=1)
        prev_start  = month_start - relativedelta(months=1)
        prev_end    = month_start - timedelta(days=1)

        #Filters 
        base_domain = []
        if company_id and str(company_id) != 'all':
            try:
                base_domain += [('company_id', '=', int(company_id))]
            except (TypeError, ValueError):
                pass
        if dept_id and str(dept_id) != 'all':
            try:
                base_domain += [('department_id', '=', int(dept_id))]
            except (TypeError, ValueError):
                pass

        # ── Applicant query helper 
        def get_applicants(start, end):
            return env['hr.applicant'].sudo().search(
                base_domain + [
                    ('create_date', '>=', datetime.combine(start, datetime.min.time())),
                    ('create_date', '<=', datetime.combine(end,   datetime.max.time())),
                ]
            )

        curr_apps = get_applicants(month_start, month_end)
        prev_apps = get_applicants(prev_start,  prev_end)

        curr_count = len(curr_apps)
        prev_count = len(prev_apps)

        apply_change = None
        if prev_count:
            apply_change = round(((curr_count - prev_count) / prev_count) * 100, 1)

      
        def is_hired(app):
            try:
                return bool(app.stage_id and app.stage_id.hired_stage)
            except Exception:
                return False

        def is_refused(app):
            try:
                return app.refuse_reason or app.active == False
            except Exception:
                return False

        #Current month stats 
        hired_apps   = [a for a in curr_apps if is_hired(a)]
        refused_apps = [a for a in curr_apps if is_refused(a)]
        in_progress  = [a for a in curr_apps
                        if not is_hired(a) and not is_refused(a)]

        hired_count    = len(hired_apps)
        refused_count  = len(refused_apps)
        progress_count = len(in_progress)

        # Conversion rate
        conversion_rate = round((hired_count / curr_count) * 100, 1) if curr_count else 0

        #All-time active pipeline
        all_active = env['hr.applicant'].sudo().search(
            base_domain + [('active', '=', True)]
        )
        pipeline_total = len(all_active)

        #Stage-wise pipeline breakdown
        stage_map = {}
        for app in all_active:
            sname = app.stage_id.name if app.stage_id else 'Unknown'
            if sname not in stage_map:
                stage_map[sname] = {'count': 0, 'hired': 0}
            stage_map[sname]['count'] += 1
            if is_hired(app):
                stage_map[sname]['hired'] += 1

        stage_breakdown = sorted(
            [{'stage': k, 'count': v['count'], 'hired': v['hired']}
             for k, v in stage_map.items()],
            key=lambda x: -x['count']
        )[:8]

        #Department breakdown (current month)
        dept_map = {}
        for app in curr_apps:
            dname = app.department_id.name if app.department_id else 'No Dept'
            if dname not in dept_map:
                dept_map[dname] = {'applied': 0, 'hired': 0}
            dept_map[dname]['applied'] += 1
            if is_hired(app):
                dept_map[dname]['hired'] += 1

        dept_breakdown = sorted(
            [{'dept': k, 'applied': v['applied'], 'hired': v['hired']}
             for k, v in dept_map.items()],
            key=lambda x: -x['applied']
        )[:8]

        #Job Position breakdown (current month)
        job_map = {}
        for app in curr_apps:
            jname = app.job_id.name if app.job_id else 'Unknown'
            job_map[jname] = job_map.get(jname, 0) + 1

        job_breakdown = sorted(
            [{'job': k, 'count': v} for k, v in job_map.items()],
            key=lambda x: -x['count']
        )[:6]

        #source breakdown
        source_map = {}
        for app in curr_apps:
            src = None
            if getattr(app, 'source_id', None):
                src = app.source_id.name
            elif getattr(app, 'ref_user_id', None):
                src = 'Internal Referral'
            src = src or 'Direct'
            source_map[src] = source_map.get(src, 0) + 1

        source_breakdown = sorted(
            [{'source': k, 'count': v} for k, v in source_map.items()],
            key=lambda x: -x['count']
        )[:6]

        #6-month trend
        monthly_trend = []
        for i in range(5, -1, -1):
            m   = today - relativedelta(months=i)
            m_s = m.replace(day=1)
            m_e = (m_s + relativedelta(months=1)) - timedelta(days=1)
            apps = get_applicants(m_s, m_e)
            h    = sum(1 for a in apps if is_hired(a))
            monthly_trend.append({
                'label':   m.strftime('%b %y'),
                'applied': len(apps),
                'hired':   h,
            })

        # Avg days to hire (current month hired) 
        days_list = []
        for app in hired_apps:
            try:
                if app.create_date and app.date_closed:
                    diff = (self._to_date(app.date_closed) -
                            self._to_date(app.create_date)).days
                    if diff >= 0:
                        days_list.append(diff)
            except Exception:
                pass
        avg_days_to_hire = round(sum(days_list) / len(days_list), 1) if days_list else None

        return {
            'has_recruitment':   True,
            'month_label':       today.strftime('%B %Y'),

            # KPIs
            'curr_count':        curr_count,
            'prev_count':        prev_count,
            'apply_change':      apply_change,
            'hired_count':       hired_count,
            'refused_count':     refused_count,
            'progress_count':    progress_count,
            'conversion_rate':   conversion_rate,
            'pipeline_total':    pipeline_total,
            'avg_days_to_hire':  avg_days_to_hire,

            # Breakdowns
            'stage_breakdown':   stage_breakdown,
            'dept_breakdown':    dept_breakdown,
            'job_breakdown':     job_breakdown,
            'source_breakdown':  source_breakdown,
            'monthly_trend':     monthly_trend,
        }

    except Exception as e:
        _logger.error("get_recruitment_summary: %s", e, exc_info=True)
        return {'has_recruitment': False}
