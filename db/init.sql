--テーブル作成
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


--インデックス作成
CREATE INDEX idx_teams_team_code ON teams (team_code);

CREATE INDEX idx_users_team_id ON users (team_id);
CREATE INDEX idx_users_employee_code ON users (employee_code);

CREATE INDEX idx_schedules_target_date ON schedules (target_date);
CREATE INDEX idx_schedules_user_id ON schedules (user_id);
CREATE INDEX idx_schedules_user_date ON schedules (user_id, target_date);

CREATE INDEX idx_monthly_summary_year_month ON monthly_schedule_summary (year_month);


--サンプルデータの登録
INSERT INTO teams (id, team_code, name, created_at, updated_at)
VALUES
    ('1', 'TEAM_A', 'チームA', '2026-04-01 09:00:00', '2026-04-01 09:00:00'),
    ('2', 'TEAM_B', 'チームB', '2025-04-01 09:00:00', '2025-04-01 09:00:00'),
    ('3', 'TEAM_C', 'チームC', '2025-04-01 09:00:00', '2025-04-01 09:00:00');


INSERT INTO users (id, employee_code, name, team_id, created_at)
VALUES
    ('001','E0001', '山田太郎', '1', '2024-01-05 09:15:22+09'),
    ('002','E0002', '伊藤一馬', '1', '2024-02-12 10:30:45+09'),
    ('003','E0003', '渡辺圭子', '2', '2024-03-25 14:05:12+09'),
    ('004','E0004', '山田太郎', '1', '2024-04-01 08:55:30+09'),
    ('005','E0005', '高橋健太', '2', '2024-05-18 11:20:00+09'),
    ('006','E0006', '田中直樹', '2', '2024-07-10 16:45:18+09'),
    ('007','E0007', '渡辺美紀', '3', '2024-09-02 09:02:55+09'),
    ('008','E0008', '伊藤裕子', '1', '2024-11-15 13:12:40+09'),
    ('009','E0009', '中村亮介', '3', '2025-01-06 10:05:00+09'),
    ('010','E0010', '小林直人', '2', '2025-02-20 15:30:12+09'),
    ('011','E0011', '加藤恵子', '1', '2025-04-01 09:10:05+09'),
    ('012','E0012', '吉田拓也', '3', '2025-06-12 11:40:22+09'),
    ('013','E0013', '山田花子', '2', '2025-08-05 14:55:33+09'),
    ('014','E0014', '佐々木純', '1', '2025-10-22 17:05:48+09'),
    ('015','E0015', '山口真一', '3', '2025-12-01 10:20:15+09');


INSERT INTO work_status_types (id, status_code, status_name)
VALUES
    ('01', 'OFFICE', '出社'),
    ('02', 'REMOTE', 'リモート'),
    ('03', 'PAID_LEAVE', '休暇'),
    ('04', 'AM_LEAVE', '午前休暇'),
    ('05', 'PM_LEAVE', '午後休暇'),
    ('06', 'ABSENCE', '欠勤');


INSERT INTO schedules (id, user_id, target_date, status_type_id, start_time, end_time, comment,created_at, updated_at)
VALUES
    ('1', '001', '2026-05-20', '04', '09:30:00', '12:00:00', '通院のため', '2026-04-16 12:00:00', '2026-04-16 12:00:00');


INSERT INTO schedules (id, user_id, target_date, status_type_id, start_time, end_time, comment, created_at, updated_at)
VALUES
    ('2', '002', '2026-05-20', '02', '09:00:00', '18:00:00', '自宅作業', '2026-04-16 12:05:00', '2026-04-16 12:05:00'),
    ('3', '003', '2026-05-21', '03', NULL, NULL, '私用のため', '2026-04-16 12:10:00', '2026-04-16 12:10:00'),
    ('4', '005', '2026-05-20', '05', '09:00:00', '13:00:00', '役所手続き', '2026-04-16 12:15:00', '2026-04-16 12:15:00'),
    ('5', '005', '2026-04-16', '06', NULL, NULL, '体調不良', '2026-04-16 08:30:00', '2026-04-16 08:30:00');


INSERT INTO monthly_schedule_summary (id, user_id, year_month, office_days, remote_days, paid_leave_days, am_leave_count, pm_leave_count, absence_days, updated_at)
VALUES
    ('1', '001', '2026-04','11','3', '0', '0', '0', '1', '2026-04-16 14:00:00+09'),
    ('2', '002', '2026-04', '2', '10', '0', '0', '0', '0', '2026-04-16 14:05:00+09'),
    ('3', '003', '2026-04', '8', '2', '2', '0', '0', '0', '2026-04-16 14:10:00+09'),
    ('4', '004', '2026-04', '11', '1', '0', '0', '0', '0', '2026-04-16 14:15:00+09'),
    ('5', '005', '2026-04', '5', '6', '0', '0', '1', '0', '2026-04-16 14:20:00+09');