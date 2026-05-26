from . import health, teams, users, work_status_types, schedules, reports

def register_routes(app):
    app.register_blueprint(health.bp)
    app.register_blueprint(work_status_types.bp)
    app.register_blueprint(schedules.bp)
    app.register_blueprint(teams.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(reports.bp)