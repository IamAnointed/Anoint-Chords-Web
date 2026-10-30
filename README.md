# Anoint Chords Web v2 — Admin Approval

Existing Firebase project: `chord-charts-bd4c3`.

## Setup
1. Enable **Authentication → Sign-in method → Email/Password** in Firebase Console.
2. Confirm the two supplied UIDs exist in Authentication → Users.
3. **Back up existing Firestore rules** before replacing them. Merge rules for any unrelated collections.
4. Paste `firestore.rules` into Firestore Database → Rules → Publish (or deploy with CLI).
5. From this folder, run `npm install -g firebase-tools`, `firebase login`, then `firebase deploy --only hosting --project chord-charts-bd4c3`.
6. Open the Hosting URL and sign in as Super Admin. The dashboard lists pending requests.

## New Admin workflow
A new person signs up with email/password, then selects **Request Admin Access**. The request is stored in `adminRequests/{uid}` with status `pending`. The Super Admin approves or rejects it. Only approved accounts can edit songs. All visitors can view and transpose songs.

## Security
Permissions are enforced in Firestore rules, not merely by hiding buttons. The Super Admin UID and initial Admin UID are identifiers, not passwords. Never commit service-account credentials. Existing users' Firebase passwords are not included.

## Limitations
This release does not import the Drive Excel collection automatically. Test against your existing `songs` collection. Hosting and Firestore rules are separate deployment steps. Offline song availability depends on browser caching and Firestore configuration.
