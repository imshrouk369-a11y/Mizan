# Mizan Budget for Android

A values-based budget app. You split your income across the things you value (Security, Family, Growth and so on), log each payment against a value, and see the month as a ring chart with your balance.

Everything works offline. Your data stays on your phone. There is no account and no server.

## Get the APK (about 10 minutes, no coding)

The APK is built for free by GitHub, so you do not need Android Studio.

1. Sign in at github.com (free account) and create a new **private** repository, for example `mizan-budget`.
2. In the new repository choose **Add file → Upload files**.
3. Unzip this folder on your computer, select everything inside it (including the hidden `.github` folder), and drag it into the upload page. Press **Commit changes**.
   - If your computer hides the `.github` folder, turn on "show hidden files" first. The build will not start without it.
4. Open the **Actions** tab. A run called **Build Android APK** starts by itself and takes about 5 to 8 minutes. If it does not start, open it from the left list and press **Run workflow**.
5. When the run shows a green tick, open it and download **mizan-budget-apk** from the Artifacts section at the bottom. Unzip it to get `mizan-budget.apk`.

## Install on your phone

1. Send `mizan-budget.apk` to your phone (Drive, WhatsApp to yourself, a cable, anything).
2. Open it. Android will ask you to allow installs from that app (Files, Chrome, WhatsApp). Allow it once.
3. Tap **Install**, then open **Mizan** from your app drawer.

The APK is signed with a debug key. That is fine for your own phone. It is not suitable for the Play Store.

## iPhone, or any phone without the APK

The `docs` folder is also a complete website that installs like an app and works offline.

1. In your repository open **Settings → Pages**. Under **Build and deployment** choose **Deploy from a branch**, pick branch **main** and folder **/docs**, then Save. (On a free GitHub account Pages needs a public repository. The repository only contains the app, not your data.)
2. After a minute or two the page shows your link, usually `https://YOURNAME.github.io/REPOSITORY/`.
3. iPhone: open the link in **Safari**, tap **Share**, then **Add to Home Screen**. Android: open it in Chrome, tap the menu, then **Install app**.

The website copy keeps its data in that phone's browser storage, separate from the APK. Use **Back up data** to move data between them.

## Your data

- Saved on the phone after every change.
- Keep it safe with **side menu → Settings → Back up data**. It opens the Android share sheet so you can save the file to Drive or send it to yourself. **Restore from backup** loads that file again, for example on a new phone.
- Uninstalling the app or clearing its storage deletes the data, so back up first.
- **side menu → Settings → Export CSV** shares the month as a spreadsheet file.

## Using Android Studio instead

Needs Node 22 and Android Studio.

```
npm install
npm run android:prepare
npx cap open android
```

Then in Android Studio choose **Build → Build APK(s)**.

## Changing the app

The whole app is `docs/index.html`. After editing it, run `npx cap sync android` (Android Studio route) or just upload the changed file to GitHub (cloud route) and download the new APK. If you change app files, also raise the number in `docs/sw.js` (`mizan-v4` to `mizan-v5`) so installed copies update.

To change the icon or splash screen, replace the PNG files in `assets/` and build again.

## Selling Pro (prices, checkout links, license codes)

Prices are $20 for 1 year, $39 for 3 years and $100 for lifetime.

1. Open `docs/index.html` and find `var CONFIG = {`. Put your checkout page for each plan in `checkout`, and your WhatsApp or email link in `supportUrl`. You can also add a tutorial video link in `tutorialUrl`. If you change a price, also change the "About $x a month" lines in the `S2` block.
2. A customer pays on your checkout page and messages you.
3. You create a license code with the private license tool (a separate download, never upload it to GitHub): `node make-license.js y1`, `y3` or `life`. Send the code to the customer.
4. They paste it in **Menu -> Buying Options -> license code** and Pro turns on. It works offline and is checked on the phone against a public key inside the app.

Codes can be used on one phone each time they are entered, and a backup file never changes a plan. A code is not locked to one phone, so share only with the buyer.

If you later publish on Google Play or the App Store, they require their own in-app purchase for digital unlocks, so license codes are for the website, the APK you send yourself, and direct sales.

## Pro features in the app

Free: all 3 budget styles, unlimited payments, 10 categories with 3 sub-categories each, backup and restore.

Pro: unlimited categories and sub-categories, recurring bills (added automatically on their due day), reminders (daily, bill due day, monthly summary), monthly report with charts, CSV export, and the Android home-screen widget.

Reminders and the widget work only in the Android app. On iPhone the website version has everything else. A real iPhone widget needs Xcode on a Mac.

## Calculator in the amount box

Anywhere you type an amount (expense, income, recurring bill) you can write a sum, such as `120+45x2`, `(10+5)*3` or `200+10%`, and the answer shows under the box. The keys under the box insert + - x / ( ) %.

## Widgets on Android

Long-press an empty part of the home screen, tap Widgets, choose Mizan and drag out the small or the large one (Pro).

- Small: how much of this month's income is spent, a progress bar, and **Spend** and **Income** buttons.
- Large: the same, plus three category tiles that show this month's spending. Tap a tile to add an expense straight into that category. Choose the three categories in **Menu -> Home-screen widget**.

Neither widget shows your balance. They follow the phone's light or dark mode.
