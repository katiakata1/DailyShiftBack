// how to run: deno run index.ts | jq

// Constants
const MAX_EMPLOYEES = 100;
const PHONE_PREFIX = "+1-555-";
const ROLES = [
  "Cashier",
  "Retail Associate",
  "Food Service Worker",
  "Delivery Driver",
  "Receptionist",
  "Cleaner",
  "Warehouse Worker",
  "Telemarketer",
  "Housekeeper",
  "Customer Service Representative",
];
const GOAL_NAMES = [
  "Emergency Fund",
  "Education",
  "Vacation",
  "Home Down Payment",
  "Retirement",
  "Medical Expenses",
  "Debt Repayment",
  "New Car",
  "Wedding Fund",
  "Family Support",
  "Investment",
  "Gadget Purchase",
  "Pet Care",
  "Self-Development",
  "Career Advancement",
  "Relocation",
  "Charity Donation",
  "Business Startup",
  "Travel",
  "Vehicle Maintenance",
];
const FIRST_NAMES = [
  "John",
  "Jane",
  "Alex",
  "Samantha",
  "Chris",
  "Pat",
  "Taylor",
  "Jordan",
  "Morgan",
  "Skyler",
];
const LAST_NAMES = [
  "Doe",
  "Smith",
  "Johnson",
  "Lee",
  "Evans",
  "Brown",
  "Miller",
  "Wilson",
  "Moore",
  "Taylor",
];

// Helper functions
const getRandomInt = (max: number, min = 0) =>
  Math.floor(Math.random() * (max - min) + min);
const getRandomFloat = (max: number, min = 0) =>
  parseFloat((Math.random() * (max - min) + min).toFixed(2));

// Generate employee details
const generateEmployee = () => ({
  uuid: Math.random().toString(36).substring(2),
  fullName: `${FIRST_NAMES[getRandomInt(FIRST_NAMES.length)]} ${LAST_NAMES[getRandomInt(LAST_NAMES.length)]}`,
  phoneNumber: `${PHONE_PREFIX}${getRandomInt(900000, 100000)}`,
  role: ROLES[getRandomInt(ROLES.length)],
});

// Generate savings goals
const generateSavingsGoal = () => ({
  goalName: GOAL_NAMES[getRandomInt(GOAL_NAMES.length)],
  targetAmountDollars: getRandomInt(10000, 1000),
  currentAmountDollars: getRandomInt(getRandomInt(10000, 1000)),
});

const generateSavingsGoals = () =>
  Array.from({ length: getRandomInt(5, 1) }, generateSavingsGoal);

// Generate full employee data with goals and financials
const generateEmployeesData = () => ({
  employee: generateEmployee(),
  savingsGoals: generateSavingsGoals(),
  dailyPayAvailableBalance: getRandomFloat(200, 50),
  advancesWithinPast30Days: getRandomInt(6),
  daysSinceLastAdvance: getRandomInt(30),
  averageAdvanceAmount: getRandomFloat(200, 100),
  opportunityAcceptanceRatio: getRandomFloat(0.3, 0.5),
  hoursWorkedWithinPastWeek: getRandomInt(20, 10),
  currentLocationInMilesAway: getRandomInt(30, 1),
});

// Generate an array of employees
const generateEmployees = (num: number) =>
  Array.from({ length: num }, generateEmployeesData);

// Generate and output the employees JSON
const employees = { eligibleEmployees: generateEmployees(MAX_EMPLOYEES) };

console.log(JSON.stringify(employees, null, 2));
