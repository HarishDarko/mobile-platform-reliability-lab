# Mobile DevOps Overview

This document summarizes mobile build and release concepts relevant to the lab.

## Why Mobile DevOps Is Different

Backend services can often be deployed, rolled back, and patched quickly on server-side infrastructure. Mobile apps have extra constraints:

- App Store and Play Store distribution.
- iOS and Android signing.
- Device compatibility.
- Installed app versions in the wild.
- Slower rollback.
- Platform-specific build tools.
- Coordination with backend API versions.

## iOS Build And Release

Native iOS builds require macOS and Xcode.

Important concepts:

- Xcode
- macOS CI runner
- signing certificate
- provisioning profile
- bundle identifier
- entitlements
- TestFlight
- App Store Connect

Common failure areas:

- expired certificate
- wrong provisioning profile
- bundle ID mismatch
- entitlement mismatch
- Xcode version mismatch
- CocoaPods/dependency issue
- TestFlight upload issue

## Android Build And Release

Android builds generally run well on Linux CI runners.

Important concepts:

- Gradle
- Android SDK/build tools
- Java version
- keystore
- key alias/passwords
- application ID
- build variants/flavors
- Google Play Console tracks

Common failure areas:

- Gradle dependency issue
- wrong Java version
- missing SDK/build tools
- keystore/signing problem
- application ID mismatch
- Play upload issue

## CI/CD Checks

Useful mobile CI checks:

- TypeScript validation
- linting
- unit tests
- Android build validation
- iOS build validation on macOS
- signing validation
- environment config validation
- artifact upload
- staged release

## How This Lab Connects

This lab does not claim to implement a full native mobile release pipeline. It demonstrates the platform-adjacent workflow:

- Expo React Native TypeScript app
- environment-based API URL
- GitHub Actions TypeScript validation
- backend API reliability
- Dockerized backend
- Kubernetes manifests
- Cloud Run/GKE deployment path
- certificate expiry automation
- observability/runbook documentation

## Explanation

> Mobile DevOps includes normal CI/CD practices, but it also has platform-specific concerns like signing, provisioning profiles, app store distribution, installed app versions, and slower rollback. A mobile platform engineer needs to understand both the app build pipeline and the backend/API reliability path that the app depends on.
