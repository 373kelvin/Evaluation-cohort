# Artifact Inventory — mern-employee-shift-manager-master

**Summary:** 30 artifacts (config: 2, function: 26, model: 2)

## Configs

| Name | Source | Detail |
|------|--------|--------|
| `package.json` | `backend/package.json` | configuration file |
| `package.json` | `frontend/package.json` | configuration file |

## Functions

| Name | Source | Detail |
|------|--------|--------|
| `connectDB` | `backend/config/db.js:3` | JavaScript function |
| `registerUser` | `backend/controllers/authController.js:13` | JavaScript function |
| `loginUser` | `backend/controllers/authController.js:50` | JavaScript function |
| `generateToken` | `backend/controllers/authController.js:7` | JavaScript function |
| `getUserProfile` | `backend/controllers/authController.js:79` | JavaScript function |
| `updateShift` | `backend/controllers/shiftController.js:101` | JavaScript function |
| `deleteShift` | `backend/controllers/shiftController.js:128` | JavaScript function |
| `deleteShiftsByMonth` | `backend/controllers/shiftController.js:142` | JavaScript function |
| `isValidISODate` | `backend/controllers/shiftController.js:178` | JavaScript function |
| `getShiftById` | `backend/controllers/shiftController.js:53` | JavaScript function |
| `getShifts` | `backend/controllers/shiftController.js:6` | JavaScript function |
| `createShift` | `backend/controllers/shiftController.js:77` | JavaScript function |
| `deleteUserById` | `backend/controllers/userController.js:117` | JavaScript function |
| `getUserById` | `backend/controllers/userController.js:26` | JavaScript function |
| `updateUserById` | `backend/controllers/userController.js:42` | JavaScript function |
| `getUsers` | `backend/controllers/userController.js:6` | JavaScript function |
| `updateUserPassword` | `backend/controllers/userController.js:78` | JavaScript function |
| `adminOnly` | `backend/middlewares/authMiddleware.js:28` | JavaScript function |
| `protect` | `backend/middlewares/authMiddleware.js:6` | JavaScript function |
| `errorHandler` | `backend/middlewares/errorHandler.js:3` | JavaScript function |
| `queryHandler` | `backend/middlewares/queryHandler.js:3` | JavaScript function |
| `formatToLocalTime` | `frontend/src/utils/formatToLocalTime.js:1` | JavaScript function |
| `getNextMonth` | `frontend/src/utils/helper.js:14` | JavaScript function |
| `genareteWeeklySummary` | `frontend/src/utils/helper.js:20` | JavaScript function |
| `validateEmail` | `frontend/src/utils/helper.js:3` | JavaScript function |
| `getPreviousMonth` | `frontend/src/utils/helper.js:8` | JavaScript function |

## Models

| Name | Source | Detail |
|------|--------|--------|
| `Shift.Model.js` | `backend/models/Shift.Model.js` | data model / schema |
| `User.Model.js` | `backend/models/User.Model.js` | data model / schema |
