# Optional Project Support

YT Cuts is free to use and open source under the MIT License. All core features remain available without payment. Contributions are voluntary and do not unlock features, remove limits, create an account, provide support obligations, or change download behavior.

## Lemon Squeezy setup

1. Create a Lemon Squeezy product and checkout that is appropriate for voluntary project support. Use a one-time contribution configuration; do not create a subscription or imply that support is required.
2. Copy the HTTPS hosted checkout URL from Lemon Squeezy. The application accepts only URLs on `lemonsqueezy.com` that use the `/checkout/` path.
3. Configure the local process before starting YT Cuts:

   ```powershell
   $env:YT_CUTS_SUPPORT_URL = "https://YOUR-STORE.lemonsqueezy.com/checkout/buy/YOUR-VARIANT"
   .\.venv\Scripts\python.exe run.py
   ```

4. For a packaged executable, set the same environment variable in the process or launcher that starts the executable. Do not commit it to source control if the URL contains private or campaign-specific information.

The application uses a normal external link. It does not embed Lemon Squeezy scripts, collect payment details, call the Lemon Squeezy API, receive webhooks, store contribution records, or expose API keys. Lemon Squeezy handles checkout, payment processing, receipts, taxes, and its own customer data according to its current requirements and policies.

Verify the checkout text, pricing, currency, receipt settings, refund language, tax treatment, and any applicable seller disclosures in the Lemon Squeezy dashboard before publishing the link. Review the provider's current documentation and obtain professional legal and tax advice for the jurisdictions in which contributions are accepted.
