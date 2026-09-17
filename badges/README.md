# Compliance badge slot

Drop the real marks here, then the chips in `demo.html` become images with a one line swap.

## What to save

| File | Where to get it |
|---|---|
| `pci.png` | payload.com footer, Certifications section |
| `soc2.png` | payload.com footer, Certifications section |
| `fifththird.png` | Fifth Third brand guidelines, or the Aug 2026 announcement page |

Save at 2x the display height (52px tall for a 26px chip), transparent PNG or SVG.

## The swap

In `demo.html`, find `<ul class="chips">` and replace each inline `<svg>` plus its label:

```html
<li><img src="badges/pci.png" alt="PCI DSS Level 1" height="26"></li>
```

The `.chips img{height:26px;width:auto}` rule is already in the stylesheet, so nothing
else changes. Keep the `alt` text, it is the accessible name once the label is gone.

## Why these are not drawn

A certification mark is a credential artifact controlled by the assessor and the AICPA,
and a partner logo belongs to the partner. Reusing the marks Payload already publishes is
fine, on the same basis as the customer logos already on the page. Drawing a lookalike is
not. That is the only line here.
