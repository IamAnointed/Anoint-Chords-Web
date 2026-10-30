# Anoint Chords website (Firebase Hosting)

Uses existing Firebase project `chord-charts-bd4c3`, Firestore collection `songs`.

## Before deploying
1. In Firebase Console > Authentication > Users, create/find your admin email account and copy its UID. Do not share the password.
2. Replace `REPLACE_WITH_ADMIN_FIREBASE_UID` in `public/index.html` AND `firestore.rules` with the exact UID.
3. In Firebase Console > Firestore Database > Rules, merge the `songs` rule from `firestore.rules` into existing rules (do not overwrite unrelated collections), then Publish. Viewer read is public; writes are admin-only.
4. In Firebase Console > Authentication > Settings > Authorized domains, ensure your hosting domain is allowed.

## Deploy from computer
1. Install Node.js LTS, then `npm install -g firebase-tools`.
2. Open terminal in this folder and run `firebase login`.
3. Run `firebase use chord-charts-bd4c3`.
4. Run `firebase deploy --only hosting`.
5. Open https://chord-charts-bd4c3.web.app (if Hosting is provisioned).

## GitHub
Commit these files to a GitHub repository for source control. GitHub does NOT host this deployment; Firebase Hosting does. Do not upload the Android `app/` folder into this web root.

## Notes
The PWA service worker caches only the website shell. Offline Firestore songs require additional persistence configuration/testing. This package does not import Drive Excel files. Existing Firebase config is embedded in index.html; Firebase web config is not a password. Admin permissions depend on Firestore rules, not UI alone.
