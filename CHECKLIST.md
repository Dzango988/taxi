# Functional Regression Checklist — taxieconom.ru

This checklist documents the manual coverage used as a basis for the automated UI suite.

Legend: **P0** — smoke/critical, **P1** — core regression, **P2** — extended regression.

| ID | Priority | Area | Check | Expected result | Automated |
|---|---|---|---|---|---|
| HOME-01 | P0 | Home | Open `/` | Page responds successfully, title and main heading are visible | Yes |
| HOME-02 | P0 | Navigation | Check Advertising, Contacts, Add service links | Links are visible and point to expected URLs | Yes |
| HOME-03 | P0 | Cities | Open Moscow from popular cities | `/moscow/` opens and city heading is displayed | Yes |
| HOME-04 | P1 | City search | Search for Penza | Relevant `/penza/` result appears | Yes |
| CITY-01 | P0 | City page | Open Moscow | City heading, services and phone links are present | Yes |
| CITY-02 | P1 | City page | Open Saint Petersburg and Sochi | Shared template works for different city data | Yes |
| CITY-03 | P0 | Service card | Open first service from city page | Service detail page opens with matching heading | Yes |
| SERVICE-01 | P1 | Breadcrumbs | Check Home and city breadcrumb links | Breadcrumb URLs are correct | Yes |
| SERVICE-02 | P1 | Phone | Check phone link on service page | At least one visible `tel:` link is available | Yes |
| FAV-01 | P1 | Favourites | Open empty favourites | Page opens and empty favourites state is available | Yes |
| AUTH-01 | P0 | Login | Open `/account/` | Login and password fields are visible | Yes |
| AUTH-02 | P0 | Login | Sign in with valid test credentials | User receives access to protected page | Yes |
| AUTH-03 | P1 | Login | Submit wrong password | Authorization fails and safe error is shown | Yes |
| AUTH-04 | P1 | Login | Submit unknown user | Authorization fails and safe error is shown | Yes |
| AUTH-05 | P1 | Login | Submit empty credentials | User stays unauthorized | Yes |
| AUTH-06 | P1 | Access control | Open `/account/add/` without session | User is redirected to login | Yes |
| REG-01 | P1 | Registration | Open registration form | Required registration controls exist | Yes |
| REC-01 | P1 | Recovery | Open password recovery | Recovery input and submit control are available | Yes |
| CONTACT-01 | P0 | Contacts | Open contacts page | Heading and form are visible | Yes |
| CONTACT-02 | P1 | Contacts | Check required fields | Name, email and message use native required validation | Yes |
| ADS-01 | P1 | Advertising | Open advertising page | Advertising form is available | Yes |
| ADS-02 | P1 | Advertising | Check required fields | Email, taxi name and phone are required | Yes |
| NEWS-01 | P0 | News | Open news page | Heading and at least one article link are present | Yes |
| FOOT-01 | P1 | Footer | Check legal/navigation links | Offer, privacy, about and news links point correctly | Yes |
| COMMON-01 | P2 | Responsive | Check 360×800, 768×1024, 1440×900 | Key controls remain usable without layout breakage | No |
| COMMON-02 | P2 | Accessibility | Keyboard navigation and visible focus | Interactive controls are keyboard reachable | No |
| COMMON-03 | P2 | Cross-browser | Run P0/P1 in Chromium, Firefox, WebKit | Critical scenarios behave consistently | Supported |

## Execution strategy

- Pull request / quick check: `pytest -m "smoke and not auth" --browser chromium -v`
- Full local regression: `pytest -m regression --browser chromium -v`
- Authorization suite: `pytest -m auth --browser chromium -v` with credentials passed through environment variables.
- Destructive production actions (real form submission, SMS registration, password reset, account data changes) are intentionally excluded.
