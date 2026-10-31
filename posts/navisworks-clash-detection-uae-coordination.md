---
title: "Navisworks Manage Clash Detection: UAE Coordination Workflow"
date: "2026-10-26T18:59:25.379-07:00"
description: "Run Navisworks Manage clash tests for UAE projects—federate models, set tolerances, report and close clashes."
eyebrow: "Civil Engineering"
keywords: "Civil Engineering, Software Guides, Architecture UAE"
canonical: "https://shoaibsite.blogspot.com/2026/10/navisworks-clash-detection-uae-coordination.html"
---

<figure style="margin:0 0 1.5em 0;">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" width="100%" style="max-width:100%;height:auto;border-radius:8px;" role="img" aria-label="Navisworks clash detection boxes over federated BIM model">
<rect width="1200" height="630" fill="#102018"/>
<rect x="80" y="120" width="400" height="360" fill="#2a4a3a" opacity="0.9"/>
<rect x="220" y="80" width="360" height="300" fill="#3a5a7a" opacity="0.85"/>
<rect x="400" y="200" width="320" height="280" fill="#5a4a2a" opacity="0.8"/>
<rect x="300" y="250" width="120" height="90" fill="none" stroke="#ff6b4a" stroke-width="6"/>
<rect x="480" y="180" width="100" height="80" fill="none" stroke="#ffd24a" stroke-width="6"/>
<text x="80" y="50" fill="#b8e0c8" font-family="Arial,sans-serif" font-size="22">Navisworks Manage &#183; Clash Detective</text>
<text x="320" y="310" fill="#ffb0a0" font-family="Arial,sans-serif" font-size="16">Hard</text>
<text x="500" y="170" fill="#ffe08a" font-family="Arial,sans-serif" font-size="16">Soft</text>
<rect x="800" y="80" width="360" height="470" rx="8" fill="#1a3028" stroke="#4a8a6a" stroke-width="2"/>
<text x="830" y="130" fill="#c8f0d8" font-family="Arial,sans-serif" font-size="18">Clash matrix</text>
<text x="830" y="180" fill="#a0d0b8" font-family="Arial,sans-serif" font-size="15">Arch &#215; Struct &#8212; 12</text>
<text x="830" y="220" fill="#a0d0b8" font-family="Arial,sans-serif" font-size="15">MEP &#215; Struct &#8212; 47</text>
<text x="830" y="260" fill="#a0d0b8" font-family="Arial,sans-serif" font-size="15">MEP &#215; Arch &#8212; 23</text>
<text x="830" y="320" fill="#ffb090" font-family="Arial,sans-serif" font-size="15">Tolerance: 25 mm</text>
<text x="830" y="380" fill="#90c8b0" font-family="Arial,sans-serif" font-size="15">Status: Open / Reviewed</text>
<text x="830" y="440" fill="#90c8b0" font-family="Arial,sans-serif" font-size="15">Report &#8594; BIM 360 / Docs</text>
</svg>
<figcaption>Federated models with hard and soft clash boxes&#8212;core of a UAE Navisworks coordination workflow.</figcaption>
</figure>

**Navisworks clash detection** is how many UAE main contractors and BIM leads catch duct-vs-beam and pipe-vs-ceiling conflicts before fit-out starts. Navisworks Manage federates architectural, structural and MEP models, runs Clash Detective, and produces reports the design team can close against a shared issue list.

This tutorial walks through a practical UAE coordination workflow: append models, set hard vs soft tests, assign owners, and push status through Autodesk Docs or BIM collaboration without drowning the team in duplicate clashes.

<div class="key-takeaways" markdown="1">

**Key takeaways**

- Agree hard/soft tolerances in the BEP before the first run.
- Clash by discipline pairs, not one giant ‘everything vs everything’ test.
- Group duplicates; assign one owner and a due date per clash group.
- Link reports to shop-drawing and permit milestones.

</div>

## Tools and official references

Product overview: [Autodesk Navisworks](https://www.autodesk.com/products/navisworks/overview). Command-level help: [Navisworks 2026 help](https://help.autodesk.com/view/NAV/2026/ENU/). For cloud markup and model exchange use [Autodesk BIM 360 / Docs family pages](https://www.autodesk.com/bim-360). Authority context for Dubai permits sits on [Dubai Municipality](https://www.dm.gov.ae/).

## Hard vs soft vs duplicate clashes

| Type | Meaning | Typical UAE example |
| --- | --- | --- |
| Hard | Geometry intersects | Chilled-water pipe through beam |
| Soft | Clearance / buffer violated | Cable tray inside maintenance zone above ceiling |
| Duplicate | Same element appears twice | Two copies of a duct after a bad append |

## Federation workflow (step by step)

1. Collect current IFC or native NWC/NWD exports from each discipline—aligned to shared coordinates.
2. Append into a coordination NWF; never explode consultant geometry into CAD for clash.
3. Create search sets: Architecture walls/ceilings, Structure beams/slabs, MEP by system.
4. Run Clash Detective for Arch×Struct, MEP×Struct, MEP×Arch with agreed tolerances.
5. Group results by grid zone; assign status Open → Reviewed → Resolved → Approved.
6. Export HTML/XML report; link clash IDs to the issue tracker in Docs.
7. Re-run only changed search sets after each model drop—not the entire history blindly.

Site and civil context often comes from Civil 3D—see [Civil 3D basics for site work](https://shoaibsite.blogspot.com/2026/10/civil-3d-basics-for-site-and.html). Building models usually come from Revit or Archicad: [Revit BIM workflow for small design firms](https://shoaibsite.blogspot.com/2026/10/revit-bim-workflow-for-small-design.html) and [Archicad vs Revit](https://shoaibsite.blogspot.com/2026/10/archicad-vs-revit-which-bim-tool-fits.html).

## Sample clash matrix (cite-worthy)

| Test | Tolerance | Owner | Gate |
| --- | --- | --- | --- |
| MEP wet × Structure | 0–15 mm hard | MEP coordinator | Before ceiling shop drawings |
| Duct × Ceiling zone | Soft 100–150 mm | Fit-out architect | Before RCP approval |
| Façade bracket × Slab edge | Hard 0 mm | Façade engineer | Before stone cladding SD |
| Fire services × Escape path | Per code soft | Fire consultant | Before authority package |

Close coordination loops against the same milestones you use for [shop drawing approval in Dubai](https://shoaibsite.blogspot.com/2026/10/shop-drawing-approval-process-dubai.html) and [Dubai fit-out approval drawings](https://shoaibsite.blogspot.com/2026/10/dubai-fit-out-approval-drawings.html). For IFC-first Dubai submissions, pair this with our [IFC OpenBIM workflow for Dubai BIM submissions](../../blog/ifc-openbim-workflow-dubai-bim-submissions/).

## Issue writing that gets clashes closed

A clash ID alone does not move a duct. Each issue should carry:

- Grid location and level.
- Disciplines involved and proposed owner.
- Screenshot from the federated model.
- Suggested resolution (reroute, resize, open structure request).
- Due date tied to the next model drop.

Ban vague titles like “Clash 1284.” Prefer “L12 Grid C-4 CHW vs beam B12 — MEP to offset 150 mm south.”

## Cadence for UAE main-contractor meetings

| Meeting | Input | Output |
| --- | --- | --- |
| Weekly coordination | Fresh NWC/IFC drops | Updated clash groups + owners |
| Bi-weekly design | Open hard clashes only | Signed decisions in minutes |
| Pre-ceiling close | Soft clearance report | RCP shop-drawing release gate |
| Pre-stone install | Façade/slab edge clashes | Cladding SD release gate |

Publish the clash dashboard PDF to the CDE the same day—do not leave status only inside one planner’s NWF.

## Search set library (starter)

- ARCH\_Walls · ARCH\_Ceilings · ARCH\_Doors
- STR\_Beams · STR\_Columns · STR\_Slabs
- MEP\_Duct\_Supply · MEP\_Duct\_Return · MEP\_Pipe\_CHW · MEP\_Pipe\_Domestic · MEP\_CableTray
- FF\_Joinery · FF\_Stone (when modelled)

Save search sets in the coordination NWF template so every new tower does not reinvent filters. Review membership whenever a discipline changes element naming.

For shop-drawing packages that follow clash close-out, keep the same grid references on RCP and ceiling SD sheets so installers can find the resolved route without opening Navisworks.

## Export and archive rules

At each coordination milestone, publish an NWD snapshot plus the HTML clash report to the CDE. Lock write access on that revision. When disputes arise months later about who owned a duct clash, the archived report is the evidence—not a rebuilt NWF on someone’s laptop.

Also archive the search-set definitions and tolerance values used for that run. Changing tolerance from 15 mm to 50 mm silently between weeks makes trend charts meaningless.

## FAQ

### What is Navisworks clash detection?

Navisworks clash detection compares geometry from federated models to find hard intersections, soft clearance violations and duplicate elements so the team can resolve them before site installation.

### What tolerance should UAE projects use?

There is no single number. Agree tolerances per discipline in the BEP—often tighter for wet services and looser for soft clearance zones. Document them before the first Clash Detective run.

### Do I need Navisworks Manage or Freedom?

Clash Detective and full coordination tools require Navisworks Manage (or the appropriate Autodesk collection). Freedom is for viewing published NWD/NWC files, not for running clash tests.

Need coordinated shop drawings after clash close-out? Contact [D3DDD](https://d3ddd.com/) at [info@d3ddd.com](mailto:info@d3ddd.com).

Originally published on [ShoaibSite](https://shoaibsite.blogspot.com/2026/10/navisworks-clash-detection-uae-coordination.html).
