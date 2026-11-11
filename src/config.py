"""Editable site text for CMD Resource Hub Arizona (everything user-facing that is not a listing).

Change INTRO here and rebuild with `python3 build55.py`; it is used in the orange box, nothing else needs touching.
"""
NAME = 'CMD Resource Hub Arizona'      # used in <title>/meta/JSON-LD only; the visible header is the CMD logo + H1_TEXT
H1_TEXT = 'RESOURCE HUB ARIZONA'
VERSION = '5.5'                        # internal only (HTML comment); never shown to visitors
STAMP = '2026-11-11'                   # date links/contacts were last re-checked (also invalidates cached AI model lists)

# Approved by Corey on Nov 11, 2026 (single constant: edit here only).
INTRO = ("Free and sponsored resources for Arizona residents, covering food, health care, housing, jobs, legal help, "
         "education, and business funding. Each listing links to the official program and its contact details, "
         "so you can reach the right help quickly.")

TITLE = NAME + ' | Arizona Assistance Programs'                 # <= 60 chars
DESC = ('Free help in Arizona: rent and housing assistance, food banks, emergency shelter, legal aid, AHCCCS, SNAP, '
        'job training and more. Official links and contacts.')    # <= 160 chars

# Footer: exactly these two lines and nothing else.
FOOTER = ('All of this information, including links and contact information, was accurate and checked working as of November 2026.',
          'All information came from the official organization web pages or an authoritative .gov listing.')

# Tabs in display order: key, tab label (ALL CAPS, no "Free"), section heading (h2), blue subheader (h3, ALL CAPS), one-line intro.
TABS = [
    ('health', 'HEALTH & FOOD', 'HEALTH & FOOD', 'FOOD BANKS, HEALTHCARE, AND SNAP',
     'Food banks and free food pantries in Phoenix and Tempe, SNAP and WIC, AHCCCS coverage through Health-e-Arizona Plus, free and sliding-fee clinics, dental help, and the 988 mental health line.'),
    ('legal', 'LEGAL & LAW', 'LEGAL & LAW', 'LEGAL AID AND LEGAL HELP',
     'Free legal help in Phoenix and across Arizona: legal aid offices, court self-help, tenant rights, consumer complaints and crime victim services.'),
    ('school', 'CERTS & SCHOOL', 'FREE CERTS & SCHOOL', 'CLASSES, CERTIFICATES, AND FINANCIAL AID',
     'Free online courses and certificates, plus FAFSA, Pell Grant and Arizona adult education (GED) information.'),
    ('biz', 'BUSINESS & FUNDING', 'BUSINESS & FUNDING', 'SMALL BUSINESS FUNDING AND CREDIT HELP',
     'SBA loans, SCORE mentoring, Arizona Commerce Authority resources, grants, business licenses and free credit counseling.'),
    ('cheap', 'SUPER CHEAP', 'SUPER CHEAP', 'PLANS, TOOLS, AND SERVICES',
     'Low-cost phone plans, software, hosting, transit and tuition, each with a price read from the official page.'),
    ('allfree', 'ALL SERVICES', 'ALL FREE SERVICES', 'LIBRARIES, TAXES, TOOLS, AND COMMUNITY PROGRAMS',
     'Free libraries, apps, open-source software and community programs that can lower your everyday costs.'),
    ('housing', 'HOUSING & SHELTER', 'HOUSING & SHELTER', 'EMERGENCY SHELTER IN PHOENIX, RENT HELP, AND HOUSING ASSISTANCE',
     'Emergency shelters and homeless shelters in Phoenix and Tempe, help with rent and utilities, Arizona rental assistance, Section 8 and low-income public housing, home repair and heat relief.'),
    ('jobs', 'JOB PLACEMENT & HELP', 'JOB PLACEMENT & HELP', 'JOB HELP, ARIZONA UNEMPLOYMENT BENEFITS, AND FREE JOB TRAINING',
     'ARIZONA@WORK centers, AZ Job Connection, unemployment insurance, free job training, veteran employment help and resume support.'),
    ('state', 'STATE & OTHER ASSISTANCE', 'STATE & OTHER ASSISTANCE', 'ARIZONA ASSISTANCE PROGRAMS: CASH ASSISTANCE, UTILITY BILL HELP, AND CHILD CARE',
     'Arizona DES cash assistance and child care assistance, utility bill assistance, Arizona veterans benefits, free tax help, and social services from Tempe, Phoenix and Maricopa County.'),
]

# Real FAQ: every answer restates facts from the matching official pages/listings above (phones/addresses are copied from those pages).
FAQ = [
    ('How do I apply for SNAP food benefits in Arizona?',
     'Arizona DES says to apply for nutrition, cash or medical assistance through Health-e-Arizona Plus (healthearizonaplus.gov) or call 1-855-432-7587. The SNAP listing is in the Health & Food tab.'),
    ('Where can I get free or low-cost health coverage in Arizona?',
     'AHCCCS is Arizona\u2019s Medicaid agency and covers eligible people based on income; you apply through Health-e-Arizona Plus. The AHCCCS main line is (602) 417-4000.'),
    ('Where can I find emergency shelter in Phoenix?',
     'The Key Campus Welcome Center at 204 S 12th Ave, Phoenix is open 24 hours a day, 7 days a week and gives shelter referrals; its phone is (602) 229-5155. CASS also lists 24/7 emergency shelter in Phoenix at 602-256-6945. See the Housing & Shelter tab for more.'),
    ('How can I get free legal help in Arizona?',
     'AZLawHelp.org lists legal aid, articles and forms (866-637-5341), and Community Legal Services provides civil legal help for low-income residents ((602) 258-3434). Free legal aid is income-based. See the Legal & Law tab.'),
    ('How do I apply for unemployment benefits in Arizona?',
     'Use the Arizona DES Unemployment Insurance Benefits page to apply and file weekly claims. If you cannot find an answer there, DES says to call the UI Benefits Call Center at 1-877-600-2722.'),
    ('What if I am not sure which program to use?',
     '211 Arizona is a free statewide referral line for bills, food and housing help: (800) 377-3536 or (602) 263-0979 (211arizona.org/contact). The USAGov Benefit Finder in the State & Other Assistance tab also helps you see which government benefits you may qualify for.'),
]
