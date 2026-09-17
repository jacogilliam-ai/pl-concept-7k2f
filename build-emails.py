#!/usr/bin/env python3
"""Payload demo-request lifecycle. One shell, five emails, per-email layout.
Previews render with sample recipient and sender data, not merge tokens.
Run: python3 build-emails.py
"""
import os, re

C = dict(navy="#1d4f66", deep="#143b4d", mint="#76f4b2", teal="#4fc3bd", blue="#11c0ee",
         btnink="#0b2f3a", ink="#1a2227", ink2="#4b5559", ink3="#78868c",
         paper="#e9f3f7", card="#ffffff", rule="#e4eef2", panel="#f4fafc",
         pale="#c7ebf7", tealink="#0b7791")

# a real gradient bar, stepped across table cells, because email has no CSS gradients
GRAD = ["#76f4b2","#6beeb9","#60e8bf","#54e2c6","#49ddcd","#3ed7d3","#33d1da","#27cbe1","#1cc6e7","#11c0ee"]

SAMPLE = dict(first="Dana", company="Northwind Title", slot="Thursday 18 September, 10:30am ET",
              use_case="Sending payouts, commissions and disbursements",
              call="Thursday 18 September, 10:30am ET",
              eng="Alex Navarro", eng_initials="AN", eng_role="Solutions Engineering, Payload",
              est_date="18 September")

MONO = "'SF Mono','SFMono-Regular',Menlo,Consolas,'Liberation Mono','Courier New',monospace"

def grad_rule():
    cells = "".join('<td height="3" bgcolor="%s" style="font-size:0;line-height:0;">&nbsp;</td>' % c for c in GRAD)
    return ('      <table role="presentation" width="100%%" cellpadding="0" cellspacing="0" border="0">'
            '<tr>%s</tr></table>\n' % cells)

def wordmark(size=21, on_dark=True):
    lead = C["pale"] if on_dark else C["navy"]
    return ('<span style="font-family:Arial,Helvetica,sans-serif;font-size:%dpx;font-weight:bold;'
            'color:%s;letter-spacing:-0.3px;white-space:nowrap;">'
            '<span style="color:%s;font-weight:normal;">{</span>payload'
            '<span style="color:%s;font-weight:normal;">}</span></span>' % (size, lead, C["mint"], C["mint"]))

def route(t):
    """Mono breadcrumb in the header. Ties the email to the page it came from."""
    return ('<span style="font-family:%s;font-size:11px;color:%s;letter-spacing:0.3px;">'
            '%s</span>' % (MONO, C["mint"], t))

def statusline(t):
    """A log line, not a marketing kicker. Scannable in one glance."""
    return ('      <p style="margin:0 0 18px;font-family:%s;font-size:11px;line-height:1.5;'
            'letter-spacing:0.2px;color:%s;">%s</p>\n' % (MONO, C["tealink"], t))

def p(t, size=16, color=None, bottom=14, lh=1.62):
    return ('      <p style="margin:0 0 %dpx;font-family:Arial,Helvetica,sans-serif;font-size:%dpx;'
            'line-height:%s;color:%s;">%s</p>\n' % (bottom, size, lh, color or C["ink2"], t))

def h1(t):
    return ('      <h1 style="margin:0 0 16px;font-family:Arial,Helvetica,sans-serif;font-size:27px;'
            'line-height:1.2;font-weight:bold;color:%s;letter-spacing:-0.6px;">%s</h1>\n' % (C["ink"], t))

def button(label, href, bottom=30):
    return ("""      <table role="presentation" class="btn" cellpadding="0" cellspacing="0" border="0" style="margin:26px 0 %dpx;">
        <tr><td bgcolor="%s" style="border-radius:4px;">
          <a href="%s" style="display:inline-block;padding:15px 30px;font-family:Arial,Helvetica,sans-serif;font-size:16px;font-weight:bold;color:%s;text-decoration:none;border-radius:4px;">%s</a>
        </td></tr>
      </table>\n""" % (bottom, C["mint"], href, C["btnink"], label))

def textlink(label, href):
    return ('<a href="%s" style="color:%s;font-weight:bold;text-decoration:none;border-bottom:1px solid %s;">%s</a>'
            % (href, C["tealink"], C["teal"], label))

def datacard(rows, label=None, accent=False):
    """Key and value, mono keys, on a tinted surface. A second mint rule per email was
    the tic that made these read as a template."""
    out = ('      <table role="presentation" width="100%%" cellpadding="0" cellspacing="0" border="0" '
           'style="margin:6px 0 30px;"><tr>'
           '<td bgcolor="%s" style="padding:22px 24px;border-radius:4px;">\n' % C["panel"])
    if label:
        out += ('        <p style="margin:0 0 16px;font-family:%s;font-size:11px;letter-spacing:0.3px;color:%s;">'
                '<span style="color:%s;">{</span> %s <span style="color:%s;">}</span></p>\n'
                % (MONO, C["ink3"], C["teal"], label, C["teal"]))
    for i, (k, v) in enumerate(rows):
        mb = 0 if i == len(rows) - 1 else 15
        out += ('        <p style="margin:0 0 %dpx;font-family:Arial,Helvetica,sans-serif;font-size:15px;'
                'line-height:1.5;color:%s;"><span style="font-family:%s;font-size:11px;color:%s;'
                'letter-spacing:0.3px;display:block;margin-bottom:4px;">%s</span>%s</p>\n'
                % (mb, C["ink"], MONO, C["ink3"], k, v))
    out += '      </td></tr></table>\n'
    return out

def quote(text, who, role):
    """Same sans as the rest. A serif here would be somebody else's brand."""
    return ("""      <table role="presentation" width="100%%" cellpadding="0" cellspacing="0" border="0" style="margin:6px 0 30px;">
        <tr><td width="2" bgcolor="%s" style="font-size:0;line-height:0;">&nbsp;</td>
        <td style="padding:2px 0 2px 20px;">
          <p style="margin:0 0 10px;font-family:Arial,Helvetica,sans-serif;font-size:17px;line-height:1.5;color:%s;letter-spacing:-0.2px;">%s</p>
          <p style="margin:0;font-family:%s;font-size:11px;line-height:1.6;color:%s;letter-spacing:0.2px;">%s <span style="color:%s;">&middot;</span> %s</p>
        </td></tr>
      </table>\n""" % (C["mint"], C["ink"], text, MONO, C["ink3"], who, C["teal"], role))

def readylist(items):
    out = ('      <table role="presentation" width="100%%" cellpadding="0" cellspacing="0" border="0" '
           'style="margin:6px 0 30px;">\n')
    for t in items:
        out += ('        <tr><td width="22" valign="top" style="padding:2px 0 12px;font-family:%s;font-size:13px;line-height:1;color:%s;">&rsaquo;</td>'
                '<td valign="top" style="padding:0 0 12px;font-family:Arial,Helvetica,sans-serif;font-size:15px;'
                'line-height:1.5;color:%s;">%s</td></tr>\n' % (MONO, C["teal"], C["ink2"], t))
    out += '      </table>\n'
    return out

def steps(items):
    out = '      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:6px 0 30px;table-layout:fixed;">\n'
    for i, (head, sub) in enumerate(items, 1):
        out += ('        <tr><td width="36" valign="top" style="padding:4px 0 18px;font-family:%s;'
                'font-size:12px;line-height:1;color:%s;letter-spacing:0.3px;">%02d</td>\n' % (MONO, C["teal"], i))
        out += ('          <td valign="top" style="padding:0 0 18px;font-family:Arial,Helvetica,sans-serif;font-size:15px;'
                'line-height:1.55;color:%s;"><strong style="color:%s;">%s</strong> %s</td></tr>\n'
                % (C["ink2"], C["ink"], head, sub))
    out += '      </table>\n'
    return out

def sectionrule(label=None):
    """A named boundary. Gives the eye a rest point and a map of what is left."""
    if not label:
        return ('      <table role="presentation" width="100%%" cellpadding="0" cellspacing="0" border="0" style="margin:4px 0 26px;">'
                '<tr><td height="1" bgcolor="%s" style="font-size:0;line-height:0;">&nbsp;</td></tr></table>\n' % C["rule"])
    return ("""      <table role="presentation" width="100%%" cellpadding="0" cellspacing="0" border="0" style="margin:8px 0 22px;table-layout:auto;">
        <tr>
          <td style="font-family:%s;font-size:11px;letter-spacing:0.4px;color:%s;padding-right:14px;">
            <span style="color:%s;">{</span> %s <span style="color:%s;">}</span></td>
          <td style="border-bottom:1px solid %s;font-size:0;line-height:0;">&nbsp;</td>
        </tr>
      </table>\n""" % (MONO, C["ink3"], C["teal"], label, C["teal"], C["rule"]))

def signature(line=None):
    return ("""      <table role="presentation" width="100%%" cellpadding="0" cellspacing="0" border="0" style="margin:6px 0 0;">
        <tr><td style="border-top:1px solid %s;padding-top:22px;">
          <p style="margin:0;font-family:Arial,Helvetica,sans-serif;font-size:15px;font-weight:bold;color:%s;line-height:1.4;">
            <span style="color:%s;font-weight:normal;">{</span> %s <span style="color:%s;font-weight:normal;">}</span></p>
          <p style="margin:4px 0 0;font-family:%s;font-size:11px;color:%s;letter-spacing:0.3px;">%s</p>
          %s
        </td></tr>
      </table>\n""" % (C["rule"], C["ink"], C["teal"], SAMPLE["eng"], C["teal"],
                       MONO, C["ink3"], "solutions engineering, payload",
                       ('<p style="margin:18px 0 0;font-family:Arial,Helvetica,sans-serif;font-size:14px;'
                        'line-height:1.6;color:%s;">%s</p>' % (C["ink2"], line)) if line else ""))


def headdetail(label, when, meta):
    """Lives inside the navy header, so the email opens with one block that answers
    every logistics question instead of three that each answer part of it."""
    return ("""    <tr><td bgcolor="%s" style="padding:4px 32px 26px;" class="pad">
      <p style="margin:0 0 9px;font-family:%s;font-size:11px;letter-spacing:0.4px;color:%s;">
        <span style="color:%s;">{</span> %s <span style="color:%s;">}</span></p>
      <p class="hd" style="margin:0 0 8px;font-family:Arial,Helvetica,sans-serif;font-size:27px;line-height:1.15;font-weight:bold;color:#ffffff;letter-spacing:-0.8px;">%s</p>
      <p style="margin:0;font-family:%s;font-size:12px;letter-spacing:0.3px;color:%s;">%s</p>
    </td></tr>\n""" % (C["navy"], MONO, C["pale"], C["mint"], label, C["mint"], when, MONO, C["pale"], meta))

def herocard(day, when, meta):
    """The meeting, as a branded band. Table and bgcolor only, so it survives images being blocked."""
    cells = "".join('<td height="3" bgcolor="%s" style="font-size:0;line-height:0;">&nbsp;</td>' % c for c in GRAD)
    return ("""      <table role="presentation" width="100%%" cellpadding="0" cellspacing="0" border="0" style="margin:6px 0 30px;">
        <tr><td bgcolor="%s" style="padding:26px 28px 24px;border-radius:5px 5px 0 0;">
          <p style="margin:0 0 10px;font-family:%s;font-size:11px;letter-spacing:0.4px;color:%s;">
            <span style="color:%s;">{</span> %s <span style="color:%s;">}</span></p>
          <p style="margin:0 0 8px;font-family:Arial,Helvetica,sans-serif;font-size:28px;line-height:1.15;font-weight:bold;color:#ffffff;letter-spacing:-0.8px;">%s</p>
          <p style="margin:0;font-family:%s;font-size:12px;letter-spacing:0.3px;color:%s;">%s</p>
        </td></tr>
        <tr><td style="font-size:0;line-height:0;"><table role="presentation" width="100%%" cellpadding="0" cellspacing="0" border="0"><tr>%s</tr></table></td></tr>
      </table>\n""" % (C["navy"], MONO, C["pale"], C["mint"], day, C["mint"], when, MONO, C["pale"], meta, cells))

LOGOS = [("anywhere","Anywhere"),("remax","RE/MAX"),("kw","Keller Williams"),
         ("exp","eXp Realty"),("fidelity","Fidelity National Title")]

def logostrip(label=None):
    cells = "".join(
      '<td align="center" valign="middle" style="padding:0 10px;">'
      '<img src="img/logo-%s.png" alt="%s" height="20" style="height:20px;width:auto;display:block;border:0;" /></td>'
      % (slug, alt) for slug, alt in LOGOS)
    return ("""      <table role="presentation" width="100%%" cellpadding="0" cellspacing="0" border="0" style="margin:10px 0 30px;">
        <tr><td style="padding:2px 0 4px;">
          <table role="presentation" align="center" cellpadding="0" cellspacing="0" border="0"><tr>%s</tr></table>
        </td></tr>
      </table>\n""" % cells)

def resources(label, items):
    """Fed by VERTICALS. Same template, different reading, no extra form fields."""
    out = '      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:6px 0 30px;">\n'
    if label:
        out += ('        <tr><td colspan="3" style="padding:0 0 14px;font-family:%s;font-size:11px;letter-spacing:0.4px;color:%s;">'
                '<span style="color:%s;">{</span> %s <span style="color:%s;">}</span></td></tr>\n'
                % (MONO, C["ink3"], C["teal"], label, C["teal"]))
    out += '        <tr>\n'
    for i, (slug, title, blurb, href) in enumerate(items):
        if i: out += '          <td width="4%">&nbsp;</td>\n'
        out += ('          <td width="48%%" valign="top">\n'
                '            <a href="%s" style="text-decoration:none;" aria-label="Read: %s">'
                '<img src="img/card-%s.png" alt="%s" width="252" style="width:100%%;max-width:252px;height:auto;display:block;border:0;border-radius:4px;" /></a>\n'
                '            <p style="margin:12px 0 4px;font-family:Arial,Helvetica,sans-serif;font-size:15px;font-weight:bold;line-height:1.35;color:%s;">%s</p>\n'
                '            <p style="margin:0;font-family:Arial,Helvetica,sans-serif;font-size:13px;line-height:1.5;color:%s;">%s</p>\n'
                '          </td>\n' % (href, title, slug, title, C["ink"], title, C["ink3"], blurb))
    out += '        </tr>\n      </table>\n'
    return out

SHELL = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<meta name="x-apple-disable-message-reformatting" />
<meta name="color-scheme" content="light" />
<meta name="supported-color-schemes" content="light" />
<meta name="robots" content="noindex, nofollow" />
<title>__SUBJECT__</title>
<style type="text/css">
  body,table,td,a{-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%}
  table,td{mso-table-lspace:0pt;mso-table-rspace:0pt}
  img{-ms-interpolation-mode:bicubic;border:0;outline:none;text-decoration:none}
  body{margin:0!important;padding:0!important;width:100%!important}
  @media screen and (max-width:620px){
    .wrap{width:100%!important}
    .pad{padding-left:24px!important;padding-right:24px!important}
    .btn a{display:block!important;text-align:center!important}
    h1{font-size:24px!important;line-height:1.24!important}
    .hd{font-size:22px!important;line-height:1.2!important}
  }
</style>
</head>
<body style="margin:0;padding:0;background:__PAPER__;">
<div style="display:none;font-size:1px;color:__PAPER__;line-height:1px;max-height:0;max-width:0;opacity:0;overflow:hidden;">__PREHEADER__&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;</div>

<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:__PAPER__;">
<tr><td align="center" style="padding:32px 12px;">
  <table role="presentation" class="wrap" width="600" cellpadding="0" cellspacing="0" border="0" style="width:600px;max-width:600px;">

    <tr><td bgcolor="__NAVY__" style="padding:20px 32px;border-radius:5px 5px 0 0;" class="pad">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="table-layout:fixed;"><tr>
        <td align="left" width="45%">__WORDMARK__</td>
        <td align="right" width="55%">__TAG__</td>
      </tr></table>
    </td></tr>
__HEADDETAIL__

    <tr><td style="font-size:0;line-height:0;">
__GRAD__
    </td></tr>

    <tr><td bgcolor="__CARD__" style="padding:34px 32px 32px;border-radius:0 0 5px 5px;" class="pad">
__BODY__
    </td></tr>

    <tr><td style="padding:24px 32px 0;" class="pad">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
        <td align="left" valign="top">__WORDMARK_SM__</td>
        <td align="right" valign="top" style="font-family:__MONO__;font-size:11px;line-height:1.8;color:__INK3__;letter-spacing:0.2px;">
          payload, llc &middot; cincinnati, oh<br />
          __FOOTLINK__
        </td>
      </tr></table>
      <p style="margin:16px 0 0;font-family:__MONO__;font-size:11px;line-height:1.7;color:__INK3__;letter-spacing:0.2px;">sent because you requested a demo at payload.com/demo</p>
    </td></tr>

  </table>
</td></tr>
</table>
</body>
</html>
"""

MANAGE = '<a href="#" style="color:%s;font-family:%s;text-decoration:underline;">manage what we send</a>' % (C["ink3"], MONO)
OPTOUT = ('<a href="#" style="color:%s;font-family:%s;text-decoration:underline;">stop these emails</a> &middot; '
          '<a href="#" style="color:%s;font-family:%s;text-decoration:underline;">preferences</a>'
          % (C["ink3"], MONO, C["ink3"], MONO))
S = SAMPLE


# ---- Two signals decide everything below. The use case comes from step one of the form,
#      before any typing. The vertical is inferred from the work email domain, so nothing
#      extra is asked of the person. ----
DEFAULT_VERT = "realestate"
# Mirrors payload.com/solutions exactly, so the form speaks their language and every
# link lands on a page that already exists.
VERTICALS = {
  "realestate": dict(
    first_q=("Which side of the close you start on.", "Earnest money, commission disbursements and vendor payables each carry different rules. Whichever you build first sets the licensing."),
    label="Real estate",
    detail="Brokerage, title, mortgage, property management",
    line="Real estate teams almost always describe the same week to me: earnest money in one system, "
         "commission splits in another, vendor payables on paper. We can put all three on one ledger.",
    reading=[("emd","Earnest money, automated","How eXp Realty moved deposits onto one rail.",
              "https://payload.com/articles/exp-realty--payload-a-unified-digital-payments-experience-for-real-estate"),
             ("protect","Good funds, guaranteed","What Payload Protect does about irrevocability.",
              "https://payload.com/articles/payload-protect")]),
  "legal": dict(
    first_q=("Whether trust funds ever touch your balance.", "IOLTA decides the rail before anything else does, and it decides it differently in every state you operate in."),
    label="Legal payments",
    detail="IOLTA, invoicing, co-counsel disbursements",
    line="With legal, the first question is always trust accounting. IOLTA rules decide the rail before "
         "anything else does, so that is where we will start.",
    reading=[("legal","Trust accounting that reconciles","IOLTA, invoicing and co-counsel payments.",
              "https://payload.com/legal-payments"),
             ("protect","Good funds, guaranteed","What Payload Protect does about irrevocability.",
              "https://payload.com/articles/payload-protect")]),
  "insurance": dict(
    first_q=("Whether premiums and claims share one ledger.", "Most carriers run them apart and find the reconciliation cost afterwards, usually at the first audit."),
    label="Insurance",
    detail="Premiums, commissions, claims disbursements",
    line="Insurance flows tend to be premiums in and claims out on completely separate systems, with "
         "commission splits sitting awkwardly between them. One integration covers all three.",
    reading=[("insurance","Premiums and claims, one rail","How insurance providers use Payload.",
              "https://payload.com/insurance-providers"),
             ("fifththird","A bank backed these rails","Why Fifth Third invested in August 2026.",
              "https://payload.com/articles/payload-fifth-third-investment")]),
  "proservices": dict(
    first_q=("Collecting or disbursing first.", "Invoicing and payouts are separate builds. Doing both in release one roughly doubles it, and one of them is usually urgent."),
    label="Professional services",
    detail="CPA, consulting, engineering firms",
    line="For firms billing time, the win is usually collections speed rather than cost. Invoices that "
         "settle on their own beat invoices that are cheaper to send.",
    reading=[("proservices","Invoices that settle themselves","Payments for CPA, consulting and engineering firms.",
              "https://payload.com/professional-services"),
             ("sandbox","Build it before we talk","Checkout and payouts quickstarts, open now.",
              "https://docs.payload.com/v2")]),
  "saas": dict(
    first_q=("Who holds the funds.", "You, us, or a bank. That one choice sets the licensing, the reconciliation and roughly half the build."),
    label="Software platform",
    detail="Embedding payments in your own product",
    line="Platform teams ask the same two things first: who holds the funds, and what reconciliation "
         "looks like at month end. We will start there rather than at the API surface.",
    reading=[("sandbox","Build it before we talk","Checkout and payouts quickstarts, open now.",
              "https://docs.payload.com/v2"),
             ("fifththird","A bank backed these rails","Why Fifth Third invested in August 2026.",
              "https://payload.com/articles/payload-fifth-third-investment")]),
}

EMAILS = []

# 01 ---- the confirmation. Densest of the five, because this is the one people keep.
EMAILS.append(dict(
    slug="01-request-received", tag=route("demo &rarr; booked"),
    head=headdetail("thursday", "18 September, 10:30am ET",
                    "30 minutes with Alex Navarro"),
    subject="Confirmed: Thursday 10:30 with Payload",
    preheader="Nothing to do until Thursday. One thing that would help if you have it.",
    body=(h1("You are booked, %s." % S["first"])
        + p("The invite is on its way with the video link. I am the engineer joining, and I already "
            "have your note about %s." % S["use_case"].lower())
        + p("<strong style=\"color:%s;\">Nothing else is needed from you.</strong> If you want the thirty "
            "minutes to go further, reply with your API reference or a flow diagram and I will map your "
            "objects onto ours before we meet." % C["ink"])
        + button("Add to calendar", "#")
        + signature("Reply here and it reaches me, not a shared inbox. Need to move it? Say so and I will resend times.")),
    footlink=MANAGE,
    text=f"""You are booked, {S['first']}.

THURSDAY 18 SEPTEMBER, 10:30AM ET
30 minutes with Alex Navarro

The invite is on its way with the video link. I am the engineer joining, and I
already have your note about {S['use_case'].lower()}.

Nothing else is needed from you. If you want the thirty minutes to go further,
reply with your API reference or a flow diagram and I will map your objects onto
ours before we meet.

Add to calendar: [link]

{S['eng']}
{S['eng_role']}

Reply here and it reaches me, not a shared inbox. Need to move it? Say so and I
will resend times.

Payload, LLC, Cincinnati, Ohio
"""))

# 02 ---- the nudge. Deliberately the shortest email in the set.
EMAILS.append(dict(
    slug="02-nothing-booked", tag=route("demo &rarr; no slot"),
    subject="Still want the thirty minutes?",
    preheader="One email. Then I leave you alone, genuinely.",
    body=(h1("You got as far as my calendar.")
        + p("Then closed it, which is fair. Here is the one thing worth knowing before you decide: most "
            "people leave this call with a written integration estimate, and that is hard to get any "
            "other way.")
        + button("Pick a time", "#")
        + p("Not ready for a call? Reply to this email with the question you actually have and I will "
            "answer it in writing. It is a slower way to the same answer, but it is a real option.", size=15)
        + p("This is the only reminder I send. There is no sequence behind it.", size=15)
        + signature()),
    footlink=OPTOUT,
    text=f"""You got as far as my calendar.

Then closed it, which is fair. Here is the one thing worth knowing before you
decide: most people leave this call with a written integration estimate, and
that is hard to get any other way.

Pick a time: [scheduling link]

Not ready for a call? Reply to this email with the question you actually have
and I will answer it in writing. It is a slower way to the same answer, but it
is a real option.

This is the only reminder I send. There is no sequence behind it.

{S['eng']}
{S['eng_role']}

Payload, LLC, Cincinnati, Ohio
Stop these emails: [unsubscribe]
"""))

# 03 ---- the reminder. Compact, agenda-forward.
EMAILS.append(dict(
    slug="03-day-before", tag=route("demo &rarr; tomorrow"),
    head=headdetail("tomorrow", "18 September, 10:30am ET",
                    "30 minutes with Alex Navarro"),
    subject="Tomorrow at 10:30: what we will cover",
    preheader="Three parts, thirty minutes. Reply tonight if you have a flow diagram.",
    body=(h1("Here is the shape of tomorrow.")
        + steps([("Minutes 0 to 5.", "Your flows on screen. Inbound, outbound, multi party, whatever you actually run."),
                 ("Minutes 5 to 25.", "I build the closest thing to your model in the sandbox, live. It stays yours afterwards."),
                 ("Minutes 25 to 30.", "What it takes to go live, and what I still need from you.")])
        + p("<strong style=\"color:%s;\">Useful to have open:</strong> a flow diagram or API reference, rough monthly "
            "volume, and whoever owns reconciliation today. None of it is required, and replying with any of it "
            "tonight means I read it before we meet." % C["ink"])
        + p('Wrong time after all? <a href="#" style="color:%s;font-weight:bold;text-decoration:none;border-bottom:1px solid %s;">Reschedule in one click.</a>'
            % (C["tealink"], C["teal"]), size=15)
        + "__VERTLINE__"
        + sectionrule("optional reading")
        + "__RESOURCES__"
        + quote("Payload has built something rare in the payments space: a platform that is both technically "
                "sophisticated and deeply aligned with real business needs.",
                "Bridgit Chayt", "Head of Commercial Payments and Treasury Management, Fifth Third")
        + signature("Bring your engineer. The questions worth asking tomorrow are the ones an SDR could not answer.")),
    footlink=MANAGE,
    text=f"""Here is the shape of tomorrow.

TOMORROW 18 SEPTEMBER, 10:30AM ET
30 minutes with Alex Navarro

01 Minutes 0 to 5. Your flows on screen. Inbound, outbound, multi party.
02 Minutes 5 to 25. I build the closest thing to your model in the sandbox,
   live. It stays yours afterwards.
03 Minutes 25 to 30. What it takes to go live, and what I still need from you.

Useful to have open: a flow diagram or API reference, rough monthly volume, and
whoever owns reconciliation today. None of it is required, and replying with any
of it tonight means I read it before we meet.

Wrong time after all? Reschedule in one click: [link]

__VERTLINE__

OPTIONAL READING
__RESOURCES__

"Payload has built something rare in the payments space: a platform that is both
technically sophisticated and deeply aligned with real business needs."
Bridgit Chayt, Head of Commercial Payments, Fifth Third

{S['eng']}
{S['eng_role']}

Bring your engineer.

Payload, LLC, Cincinnati, Ohio
"""))

# 04 ---- the estimate. The most structured, because it is a document.
EST_ROWS = [
    ("Scope", "Embedded payouts for agent commissions, ACH and RTP, with your platform as the ledger of record."),
    ("Integration estimate", "Three to four weeks. Two weeks of build, one week in sandbox, one week phased to production."),
    ("Pricing model at your volume", "Interchange plus, with payout pricing flat per transaction. Full schedule in the document."),
    ("Still open", "Whether commission splits settle same day or next day. That changes the rail, not the build."),
]
EMAILS.append(dict(
    slug="04-written-estimate", tag=route("demo &rarr; estimate"),
    subject="Your integration estimate",
    preheader="Scope, timeline and pricing model. One document, from the person on the call.",
    body=(h1("What it takes to go live.")
        + p("This is the document the demo page promised. It comes from me, the person who was on the call, not from a "
            "proposal team who was not.")
        + sectionrule("the estimate")
        + datacard(EST_ROWS)
        + button("Open the full document", "#")
        + sectionrule()
        + p("Your sandbox is still live with the objects we built together. Nothing expires, and nobody takes it back "
            "if you go quiet for a month.")
        + p("If a number in there is wrong, tell me which one. It is an estimate written by a person, so it is "
            "correctable by replying to one.")
        + signature()),
    footlink=MANAGE,
    text=f"""What it takes to go live.

Here is the summary. The full document behind the link has the line by line
pricing schedule, the API objects we mapped, and the two week build plan. It
comes from me, the person who was on the call, not a proposal team who was not.

NORTHWIND TITLE, INTEGRATION ESTIMATE
Scope: Embedded payouts for agent commissions, ACH and RTP, with your platform
as the ledger of record.
Integration estimate: Three to four weeks. Two weeks of build, one week in
sandbox, one week phased to production.
Pricing model at your volume: Interchange plus, with payout pricing flat per
transaction. Full schedule in the document.
Still open: Whether commission splits settle same day or next day. That changes
the rail, not the build.

Open the full document: [link]

Your sandbox is still live with the objects we built together. Nothing expires.

If a number in there is wrong, tell me which one.

{S['eng']}
{S['eng_role']}

Payload, LLC, Cincinnati, Ohio
"""))

# 05 ---- the close. Almost plain text on purpose: it has to read like a person typed it.
EMAILS.append(dict(
    slug="05-closing-the-file", tag=route("demo &rarr; closing"),
    subject="Closing this out, unless you say otherwise",
    preheader="Three honest options, and one of them is no.",
    body=(h1("It has been two weeks.")
        + p("I sent your estimate on %s and have not heard back. In my experience that means the timing moved, not "
            "that the product was wrong. Either way you should not have to keep deleting emails about it." % S["est_date"])
        + steps([("Pick it back up.", "Reply and we start where we stopped. Your sandbox is untouched."),
                 ("Park it.", "Name a quarter and I will note it and go quiet until then."),
                 ("You went another way.", "Say so and I close the file. No exit sequence, no win back campaign.")])
        + button("Pick it back up", "mailto:contact@payload.com?subject=Picking%20the%20Payload%20integration%20back%20up")
        + p("That button opens a reply to me with the subject filled in. Or do nothing and option three "
            "happens by default, because this is the last email in this thread. The sandbox stays open "
            "either way, since it costs us nothing and it is the part you might still want.", size=15)
        + signature("Thanks for the thirty minutes either way. Genuinely useful to hear how you are building.")),
    footlink=OPTOUT,
    text=f"""It has been two weeks.

I sent your estimate on {S['est_date']} and have not heard back. In my
experience that means the timing moved, not that the product was wrong.

01 Pick it back up. Reply and we start where we stopped. Your sandbox is
   untouched.
02 Park it. Name a quarter and I will note it and go quiet until then.
03 You went another way. Say so and I close the file. No exit sequence, no win
   back campaign.

Pick it back up: reply to this email, or write to contact@payload.com.

Or do nothing and option three happens by default, because this is the last
email in this thread. The sandbox stays open either way.

{S['eng']}
{S['eng_role']}

Thanks for the thirty minutes either way.

Payload, LLC, Cincinnati, Ohio
Stop these emails: [unsubscribe]
"""))

# 06 ---- the no show. Within the hour, because a same day rebook is the only one that lands.
EMAILS.append(dict(
    slug="06-no-show", tag=route("demo &rarr; missed"),
    subject="Missed you at 10:30",
    preheader="No harm done. Here is the calendar again, and I kept your notes.",
    body=(h1("Something came up, %s." % S["first"])
        + p("That happens more often than not in a week like yours, and it costs you nothing with me. "
            "Your sandbox is still open and I still have your notes about %s." % S["use_case"].lower())
        + button("Grab another time", "#")
        + p("<strong style=\"color:%s;\">If the answer is actually no,</strong> reply with one word and I will "
            "close the file. No follow up, no sequence. I would rather know than guess." % C["ink"])
        + p("If I do not hear anything in three days I will assume the timing moved and stop emailing you.", size=15)
        + signature()),
    footlink=OPTOUT,
    text=f"""Something came up, {S['first']}.

That happens more often than not in a week like yours, and it costs you nothing
with me. Your sandbox is still open and I still have your notes about
{S['use_case'].lower()}.

Grab another time: [scheduling link]

If the answer is actually no, reply with one word and I will close the file. No
follow up, no sequence. I would rather know than guess.

If I do not hear anything in three days I will assume the timing moved and stop
emailing you.

{S['eng']}
{S['eng_role']}

Payload, LLC, Cincinnati, Ohio
Stop these emails: [unsubscribe]
"""))

# 07 ---- the review route. No calendar was shown, so this has to be worth more than the
#         meeting it withheld, and it has to keep the promise the page made anyway.
EMAILS.append(dict(
    slug="07-not-yet", tag=route("demo &rarr; review"),
    subject="No call yet, and what I would decide first",
    preheader="The two questions that come before a demo, and your sandbox either way.",
    body=(h1("You are earlier than a demo, %s." % S["first"])
        + p("Pre-launch and still deciding is the one case where thirty minutes with an engineer "
            "produces a conversation and no decisions, because the answers depend on things you have "
            "not picked yet. Two of them, specifically.")
        + sectionrule("what comes first")
        + "__DECISION__"
        + p("Answer those two and a demo is worth booking. Reply with where you land and I will put the "
            "thirty minutes in myself, no form.")
        + sectionrule("in the meantime")
        + p("The page said sandbox credentials the same day whether or not you move forward, so they are "
            "on their way to this address. %s and %s both have quickstarts. Building the smallest version "
            "of your flow tends to answer question two faster than thinking about it does."
            % (textlink("checkout", "https://docs.payload.com/v2/pay/checkout"),
               textlink("payouts", "https://docs.payload.com/v2/pay/sending-payouts")))
        + sectionrule("worth reading while you decide")
        + "__RESOURCES__"
        + signature("This is the only email you get from me until you reply.")),
    footlink=OPTOUT,
    text=f"""You are earlier than a demo, {S['first']}.

Pre-launch and still deciding is the one case where thirty minutes with an
engineer produces a conversation and no decisions, because the answers depend on
things you have not picked yet. Two of them, specifically.

WHAT COMES FIRST
__DECISION__

Answer those two and a demo is worth booking. Reply with where you land and I
will put the thirty minutes in myself, no form.

IN THE MEANTIME
The page said sandbox credentials the same day whether or not you move forward,
so they are on their way to this address.
Checkout: https://docs.payload.com/v2/pay/checkout
Payouts: https://docs.payload.com/v2/pay/sending-payouts

WORTH READING WHILE YOU DECIDE
__RESOURCES__

{S['eng']}
{S['eng_role']}

This is the only email you get from me until you reply.

Payload, LLC, Cincinnati, Ohio
Stop these emails: [unsubscribe]
"""))

os.makedirs("emails", exist_ok=True)
DASH = re.compile(r"[–—]")
def render(e, vert):
    doc = SHELL
    doc = doc.replace("__GRAD__", grad_rule())
    doc = doc.replace("__WORDMARK_SM__", wordmark(16, on_dark=False))
    doc = doc.replace("__WORDMARK__", wordmark(21, on_dark=True))
    doc = doc.replace("__HEADDETAIL__", e.get("head", ""))
    for t, k in [("__SUBJECT__","subject"),("__PREHEADER__","preheader"),("__TAG__","tag"),
                 ("__BODY__","body"),("__FOOTLINK__","footlink")]:
        doc = doc.replace(t, e[k])
    for t, k in [("__PAPER__","paper"),("__NAVY__","navy"),("__MINT__","mint"),("__CARD__","card"),("__INK3__","ink3")]:
        doc = doc.replace(t, C[k])
    doc = doc.replace("__MONO__", MONO)
    v = VERTICALS[vert]
    doc = doc.replace("__RESOURCES__", resources("", v["reading"]))
    doc = doc.replace("__VERTLINE__", p(v["line"]))
    doc = doc.replace("__DECISION__", steps([v["first_q"],
        ("How many parties split a payment.", "One party is a different build to three, and it is the question every timeline estimate depends on.")]))
    assert "__" not in doc, "unreplaced token in " + e["slug"]
    assert not DASH.search(doc), "dash in " + e["slug"]
    return doc

def render_text(e, vert):
    v = VERTICALS[vert]
    reading = "\n".join("- %s: %s\n  %s" % (t, blurb, href) for _, t, blurb, href in v["reading"])
    dec = ("01 %s %s\n02 How many parties split a payment. One party is a different build\n"
           "   to three, and it is the question every timeline estimate depends on."
           % (v["first_q"][0], v["first_q"][1]))
    txt = (e["text"].replace("__RESOURCES__", reading).replace("__VERTLINE__", v["line"])
                    .replace("__DECISION__", dec))
    assert "__" not in txt and not DASH.search(txt), "bad text in " + e["slug"]
    return txt

import shutil
shutil.rmtree("emails/variants", ignore_errors=True)   # stale variants outlive a restructure
os.makedirs("emails/variants", exist_ok=True)
rows = []
for e in EMAILS:
    base = render(e, DEFAULT_VERT)
    open("emails/%s.html" % e["slug"], "w").write(base)
    open("emails/%s.txt" % e["slug"], "w").write(render_text(e, DEFAULT_VERT))
    variants = 0
    for vert in VERTICALS:
        if vert == DEFAULT_VERT: continue
        alt = render(e, vert)
        if alt == base: continue          # nothing routes in this one, do not ship a copy
        # variants sit a directory deeper, so image paths climb one level
        open("emails/variants/%s--%s.html" % (e["slug"], vert), "w").write(
            alt.replace('src="img/', 'src="../img/'))
        open("emails/variants/%s--%s.txt" % (e["slug"], vert), "w").write(render_text(e, vert))
        variants += 1
    rows.append((e["slug"], e["subject"], len(base), variants))

print("%-24s %-46s %7s %9s" % ("FILE","SUBJECT","BYTES","VARIANTS"))
for r in rows: print("%-24s %-46s %7d %9d" % r)
