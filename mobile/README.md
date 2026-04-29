# Mobile App

This folder contains the Expo React Native TypeScript client for the lab.

## What It Demonstrates

- A mobile client calling backend API endpoints.
- Environment-based API URL configuration through `EXPO_PUBLIC_API_URL`.
- Loading, success, and error states.
- Typed API responses for health, accounts, and demo payments.
- A simple request ID header that helps connect mobile calls to backend logs.

## Local Commands

From the repository root:

```powershell
cd mobile
npm install
```

Run the backend first in another PowerShell window:

```powershell
cd ..\backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

Then run the mobile app:

```powershell
cd ..\mobile
$env:EXPO_PUBLIC_API_URL="http://127.0.0.1:8000"
npm run web
```

For Android emulator testing, use:

```powershell
$env:EXPO_PUBLIC_API_URL="http://10.0.2.2:8000"
npm run android
```

For a physical phone using Expo Go, use your Windows machine LAN IP instead of `127.0.0.1`.

## iOS Note

On Windows, you can understand and edit the iOS delivery workflow, but native iOS builds require macOS because Apple tooling and code signing depend on Xcode. Expo Go can still help preview JavaScript-only flows.

