# Optional Project Support

YT Cuts is free to use and open source under the MIT License. All core features remain available without payment. Contributions are voluntary and do not unlock features, remove limits, create an account, provide support obligations, or change download behavior.

## Test mode

Set `BUYMEACOFFEE_MODE=demo` to use the local integration test. Clicking **Support the Project** then opens a clearly labeled test page where a contribution can be simulated. It does not contact Buy Me a Coffee, collect money, or record a contribution.

## Live Buy Me a Coffee setup

1. Create or activate your Buy Me a Coffee creator page and complete its payout and account requirements.
2. Copy your public page URL in the form `https://buymeacoffee.com/YOUR-USERNAME`.
3. Configure live mode before starting YT Cuts. The current project default points to `https://buymeacoffee.com/dreamlogicapps`:

   ```powershell
   $env:BUYMEACOFFEE_MODE = "live"
   $env:BUYMEACOFFEE_URL = "https://buymeacoffee.com/YOUR-USERNAME"
   .\.venv\Scripts\python.exe run.py
   ```

   The same placeholder values are available in `.env.example`. The application intentionally does not load `.env` files automatically, so export the values in the process that launches YT Cuts.

4. For a packaged executable, set the same environment variable in the process or launcher that starts the executable. Do not commit it to source control if the URL contains private or campaign-specific information.

The application uses a normal external link. It does not embed payment scripts, collect payment details, call the Buy Me a Coffee API, receive webhooks, store supporter records, or expose payment credentials. Buy Me a Coffee handles the checkout, payment processing, receipts, and payout workflow according to its current requirements and policies.

Complete Buy Me a Coffee's creator, payout, and tax requirements before publishing the link. Review its current terms and obtain professional legal and tax advice for the jurisdictions in which contributions are accepted.
