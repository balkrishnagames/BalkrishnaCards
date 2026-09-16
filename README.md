# Balkrishna Cards website

Deploy this folder to **https://balkrishnagames.in** (HTTPS is required — the app's relay URL and the WhatsApp
invite App Link both assume it).

## Pages

| File | Purpose |
|---|---|
| `index.html` | Home / marketing |
| `rules.html` | How to play every game, in twelve languages (generated from the app's own translations) |
| `terms.html` | Terms & Conditions (required by Play) |
| `privacy.html` | Privacy Policy (required by Play) |
| `delete-account.html` | Data deletion instructions (required by Play for apps with accounts/server data) |
| `support.html` | FAQ and contact |
| `join.html` | Target of the WhatsApp invite link: `https://balkrishnagames.in/join?room=CODE` |
| `.well-known/assetlinks.json` | Digital Asset Links — needed for the `/join` App Link |

Regenerate everything (rules are pulled from the app so the two can never disagree):

```bash
python3 website/build_site.py
```

## Hosting

Any static host works (GitHub Pages, Netlify, Cloudflare Pages, or nginx on your own VPS).
Two things must be true:

1. **HTTPS**, with a valid certificate.
2. The relay runs on the same domain under `/relay`, because the app's default server URL is
   `https://balkrishnagames.in/relay`. With nginx:

```nginx
location /relay/ {
    proxy_pass http://127.0.0.1:8787/;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_read_timeout 40s;      # the relay long-polls for up to 25s
}
location /.well-known/ { root /var/www/balkrishnagames; }
location / { root /var/www/balkrishnagames; try_files $uri $uri/ =404; }
```

Start the relay with `node server/server.js` (see `docs/20_BUILD_AND_RUN.md`).

## App Links (so an invite opens the app)

1. Put your Play App Signing SHA-256 fingerprint into `.well-known/assetlinks.json`
   (Play Console → Release → Setup → App signing).
2. Add the intent filter to the Android manifest
   (see `docs/20_BUILD_AND_RUN.md`, section "WhatsApp invites").
3. Verify with `https://https://balkrishnagames.in/.well-known/assetlinks.json` and Google's
   [Statement List Generator](https://developers.google.com/digital-asset-links/tools/generator).

Until App Links are verified, the invite link still works: it opens `join.html`, which shows the
room code and offers the Play Store listing.
