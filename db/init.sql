CREATE TABLE teams (
    id bigserial not null PRIMARY KEY,
    team_code varchar(50) not null,
    name VARCHAR(100) not null,
    created_at timestamptz not null,
    updated_at timestamptz not null,
    UNIQUE(team_code)
);

CREATE TABLE users (
    id bigserial not null PRIMARY KEY,
    employee_code varchar(50) not null,
    name VARCHAR(100) not null,
    team_id bigint not null, 
    created_at timestamptz not null,
    UNIQUE(employee_code),
    foreign key (team_id) references teams(id)
);

CREATE TABLE work_status_types (
    id bigserial not null PRIMARY KEY,
    status_code varchar(50) not null UNIQUE,
    status_name VARCHAR(100) not null
);

CREATE TABLE schedules (
    id bigserial not null PRIMARY KEY,
    user_id bigint not null,
    target_date DATE not null,
    status_type_id bigint not null,
    start_time TIME,
    end_time TIME,
    comment TEXT, 
    created_at timestamptz not null,
    updated_at timestamptz not null,
    foreign key (user_id) references users(id),
    foreign key (status_type_id) references work_status_types(id)
);

CREATE TABLE monthly_schedule_summary (
    id bigserial not null PRIMARY KEY,
    user_id bigint not null,
    year_month char(7) not null,
    office_days integer not null,
    remote_days integer not null,
    paid_leave_days integer not null,
    am_leave_count integer not null,
    pm_leave_count integer not null,
    absence_days integer not null,
    updated_at timestamptz not null,
    foreign key (user_id) references users(id),
    unique(user_id, year_month)
);

CREATE INDEX idx_teams_team_code ON teams (team_code);

CREATE INDEX idx_users_team_id ON users (team_id);
CREATE INDEX idx_users_employee_code ON users (employee_code);

CREATE INDEX idx_schedules_target_date ON schedules (target_date);
CREATE INDEX idx_schedules_user_id ON schedules (user_id);
CREATE INDEX idx_schedules_user_date ON schedules (user_id, target_date);

CREATE INDEX idx_monthly_summary_year_month ON monthly_schedule_summary (year_month);