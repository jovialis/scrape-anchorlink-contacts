# Scrape Anchorlink Contacts
A rudimentary script to scrape all principal contacts for all Organizations off of AnchorLink.
### Setup
1. Create a `.env` file in the project root. Create two keys: `COOKIE` and `XSRF-TOKEN`.
2. Log into [Anchorlink](https://anchorlink.vanderbilt.edu/) in a web browser.
3. Open developer tools and look at any random REST call to the anchorlink.vanderbilt.edu domain. Copy the values from the `Cookie` and `X-XSRF-Token` headers.
4. Paste in the values to the `.env` file in the respective key names.
5. Run it and voila :)