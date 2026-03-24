export const teams = [
  { id: 1, teamCode: "TEAM_A", name: "第1チーム" },
  { id: 2, teamCode: "TEAM_B", name: "第2チーム" },
];

export const users = [
  { id: 10, employeeCode: "E0001", name: "山田 太郎", teamId: 1 },
  { id: 11, employeeCode: "E0002", name: "佐藤 花子", teamId: 1 },
  { id: 20, employeeCode: "E0101", name: "鈴木 次郎", teamId: 2 },
];

export const workStatusTypes = [
  { id: 1, statusCode: "OFFICE", statusName: "出社" },
  { id: 2, statusCode: "REMOTE", statusName: "在宅" },
  { id: 3, statusCode: "PAID_LEAVE", statusName: "休暇" },
  { id: 4, statusCode: "AM_LEAVE", statusName: "午前休" },
  { id: 5, statusCode: "PM_LEAVE", statusName: "午後休" },
  { id: 6, statusCode: "ABSENCE", statusName: "欠勤" },
];

export const schedules = [
  {
    id: 100,
    userId: 10,
    targetDate: "2026-03-11",
    statusTypeId: 1,
    startTime: "09:00:00",
    endTime: "18:00:00",
    comment: "客先訪問あり",
  },
  {
    id: 101,
    userId: 11,
    targetDate: "2026-03-11",
    statusTypeId: 2,
    startTime: null,
    endTime: null,
    comment: "",
  },
  {
    id: 102,
    userId: 20,
    targetDate: "2026-03-12",
    statusTypeId: 3,
    startTime: null,
    endTime: null,
    comment: "有休",
  },
];

export function teamById(teamId) {
  return teams.find((t) => t.id === Number(teamId)) ?? null;
}

export function userById(userId) {
  return users.find((u) => u.id === Number(userId)) ?? null;
}

export function statusById(statusTypeId) {
  return workStatusTypes.find((s) => s.id === Number(statusTypeId)) ?? null;
}

export function formatTimeShort(value) {
  if (!value) return "";
  return String(value).slice(0, 5);
}

