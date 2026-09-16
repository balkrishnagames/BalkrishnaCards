# Balkrishna Cards website

This folder is served as GitHub Pages from the BalkrishnaCards repo, at **https://balkrishnagames.github.io/BalkrishnaCards**.

## Pages

| File | Purpose |
|---|---|
| `index.html` | Home / marketing |
| `rules.html` | How to play every game, in twelve languages (generated from the app's own translations) |
| `terms.html` | Terms & Conditions (required by Play) |
| `privacy.html` | Privacy Policy (required by Play) |
| `delete-account.html` | Data deletion instructions (required by Play for apps with accounts/server data) |
| `support.html` | FAQ and contact |
| `join.html` | Target of the WhatsApp invite link: `https://balkrishnagames.github.io/BalkrishnaCards/join?room=CODE` |
| `.well-known/assetlinks.json` | Digital Asset Links — needed for the `/join` App Link |

Regenerate everything (rules are pulled from the app so the two can never disagree):

```bash
python3 website/build_site.py
```

The rule text on `rules.html` is read straight out of `unity/Assets/Scripts/App/L.cs`
(`BuildRules()`), one tab per game. Two things to know before touching that reader:

* the reader accepts dotted keys, and `rules.tp.bonus` is **folded into Teen Patti** rather than
  opened as a tab of its own — the app appends it the same way in `L.RulesFor()`, and the bonus
  sits in its own key only because it is a rule the leader can switch on or off;
* a new rule line belongs in the app first. Add it to the game's own block in `L.cs` and it appears
  on the site, in the app's help screen and on the rules page of a real table in one move.

After a rebuild, `python3 tools/audit/audit_site.py` checks all seven pages: every language present,
no empty strings, and every block of inline JavaScript actually parses.

## Hosting

GitHub Pages here — but as a *project* site (`https://balkrishnagames.github.io/BalkrishnaCards`, not a custom domain or a
`balkrishnagames.github.io` root repo), it is static-only. Two consequences:

1. **The relay cannot live here.** GitHub Pages cannot run `node server/server.js`. The relay
   needs its own host (a small VPS, Render, Railway, Fly.io, etc.) with its own HTTPS URL, and the
   app's default server URL (`Assets/Scripts/App/Save.cs`, `Assets/Scripts/Net/RelayTransport.cs`)
   must point at wherever that ends up.
2. **App Links can never auto-verify.** Android requires `/.well-known/assetlinks.json` at the
   true root of the intent-filter's host. A GitHub Pages project site can only serve files under
   `/BalkrishnaCards/`, never at the bare root of `balkrishnagames.github.io` — only a repo
   literally named `balkrishnagames.github.io` (or a custom domain with a `CNAME` file) could do
   that. The manifest's `/join` intent-filter is left with `autoVerify="false"` for this reason.

## App Links (so an invite opens the app)

Auto-verified App Links are not possible on the current GitHub Pages project site (see above), so
the invite flow relies entirely on `join.html`'s own redirect: tapping
`https://balkrishnagames.github.io/BalkrishnaCards/join?room=CODE` opens this page in a browser, which immediately tries
`balkrishnacards://join?room=CODE` (an intent-filter that needs no verification) and falls back to
the Play Store button if the app is not installed. If a custom domain is ever added, revisit
`android:autoVerify` on the HTTPS intent-filter in `AndroidManifest.xml` and put the real Play App
Signing SHA-256 fingerprint into `.well-known/assetlinks.json`.
