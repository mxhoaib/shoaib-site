---
title: "IFC OpenBIM Workflow for Dubai Municipality BIM Submissions"
date: "2026-10-26T19:10:08.446-07:00"
description: "Export clean IFC for Dubai BIM submissions—units, classification, model checks before Build in Dubai upload."
eyebrow: "Architecture UAE"
keywords: "Architecture UAE, Civil Engineering, Software Guides"
canonical: "https://shoaibsite.blogspot.com/2026/10/blog-post_877.html"
---

<figure style="margin:0 0 1.5em 0;">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" width="100%" style="max-width:100%;height:auto;border-radius:8px;" role="img" aria-label="IFC OpenBIM workflow from Revit Archicad to Dubai submission">
<rect width="1200" height="630" fill="#102030"/>
<rect x="40" y="200" width="220" height="120" rx="10" fill="#2a5080"/><text x="90" y="270" fill="#d0e8ff" font-family="Arial,sans-serif" font-size="18">Revit</text>
<rect x="40" y="360" width="220" height="120" rx="10" fill="#2a6080"/><text x="70" y="430" fill="#d0e8ff" font-family="Arial,sans-serif" font-size="18">Archicad</text>
<path d="M260 260 L360 260 L360 420 L260 420" fill="none" stroke="#70b0e0" stroke-width="3"/>
<rect x="380" y="240" width="280" height="200" rx="12" fill="#1a4058" stroke="#50c8a0" stroke-width="3"/>
<text x="460" y="320" fill="#a0f0d0" font-family="Arial,sans-serif" font-size="22">IFC</text>
<text x="430" y="360" fill="#80d0b0" font-family="Arial,sans-serif" font-size="15">openBIM export</text>
<path d="M660 340 L760 340" stroke="#70b0e0" stroke-width="3" marker-end="url(#a)"/>
<rect x="780" y="180" width="380" height="320" rx="12" fill="#1a3848" stroke="#e0b050" stroke-width="3"/>
<text x="820" y="250" fill="#ffe0a0" font-family="Arial,sans-serif" font-size="20">Model check</text>
<text x="820" y="310" fill="#d0c090" font-family="Arial,sans-serif" font-size="15">Units &#183; Classification</text>
<text x="820" y="360" fill="#d0c090" font-family="Arial,sans-serif" font-size="15">Coordinates &#183; IFC schema</text>
<text x="820" y="420" fill="#d0c090" font-family="Arial,sans-serif" font-size="15">Build in Dubai upload</text>
<text x="40" y="80" fill="#b0d0e8" font-family="Arial,sans-serif" font-size="22">IFC OpenBIM &#183; Dubai BIM submissions</text>
</svg>
<figcaption>Authoring tools export IFC for validation before Dubai Municipality / Build in Dubai submission.</figcaption>
</figure>

**IFC OpenBIM Dubai** workflows are how multi-vendor teams hand models to Dubai Municipality processes without locking everyone into one proprietary format. As the [Dubai BIM mandate 2026](../../blog/dubai-bim-mandate-2026-submission-guide/) approaches, clean IFC export—units, classification, coordinates and schema—becomes a submission skill, not an optional geek interest.

This guide walks Revit and Archicad authors through a practical openBIM path: setup, export, model checking and upload readiness for Build in Dubai, with links to buildingSMART and official product pages only.

<div class="key-takeaways" markdown="1">

**Key takeaways**

- Freeze schema, MVD/view definition and units in the BEP.
- Validate IFC on a checker before every authority upload.
- Shared coordinates first—geometry second.
- Pair IFC drops with drawing packages that match model names.

</div>

## Standards and vendor docs

OpenBIM home: [buildingSMART](https://www.buildingsmart.org/) and the [IFC technical standards pages](https://technical.buildingsmart.org/standards/ifc/). Authoring: [Autodesk Revit](https://www.autodesk.com/products/revit/overview), [Graphisoft Archicad](https://www.graphisoft.com/archicad/). Authority: [Dubai Municipality](https://www.dm.gov.ae/).

## Pre-export checklist

| Item | Target | If wrong |
| --- | --- | --- |
| Length unit | mm (typical UAE) | Model appears 1000× too small/large |
| Coordinate system | Shared site origin per BEP | Clash tests misalign |
| IFC schema | As specified for submission | Portal rejects file |
| Classification | Agreed system mapped to elements | Quantities/spaces fail checks |
| Element naming | Matches sheet/model index | Reviewers cannot trace issues |

## Revit and Archicad notes

Small-firm Revit habits: [Revit BIM workflow](https://shoaibsite.blogspot.com/2026/10/revit-bim-workflow-for-small-design.html). Tool choice: [Archicad vs Revit](https://shoaibsite.blogspot.com/2026/10/archicad-vs-revit-which-bim-tool-fits.html). Site context from Civil 3D: [Civil 3D basics](https://shoaibsite.blogspot.com/2026/10/civil-3d-basics-for-site-and.html). After export, federate for clashes with [Navisworks clash detection](../../blog/navisworks-clash-detection-uae-coordination/).

1. Map project parameters to IFC properties required by the BEP.
2. Export only the submission view/set—not the entire worksharing jungle.
3. Open IFC in a viewer/checker; confirm storeys and spaces.
4. Fix authoring model; re-export (do not “patch” IFC by hand for authority files).
5. Upload per Build in Dubai instructions—drawing tips in [Build in Dubai drawing package tips](../../blog/build-in-dubai-drawing-package-tips/).

Shop-drawing alignment still matters: [shop drawing approval Dubai](https://shoaibsite.blogspot.com/2026/10/shop-drawing-approval-process-dubai.html).

## Common IFC rejection causes

- Mixed units between architecture and MEP exports.
- Duplicate site origins after a late coordinate “fix”.
- Empty IfcSpace / wrong storey assignment.
- Huge files from exporting linked CAD underlays as solids.

## Minimum BEP clauses for IFC

- Authoring software + version for each discipline.
- IFC schema and Model View Definition (or export setup name).
- Shared coordinate origin, rotation and units.
- Storey naming identical across disciplines.
- Classification system and required property sets.
- Checker tool and pass/fail gates before upload.

## Federation test before the real submission

One week before the portal date, run a “dress rehearsal”:

1. Export architecture, structure and MEP IFCs with the agreed settings.
2. Federate in Navisworks (or the project checker).
3. Confirm storeys stack and grids align within tolerance.
4. Fix authors’ models—not the federated file.
5. Re-export and archive the passing set with a checksum or CDE revision ID.

## Property set essentials

Even a light UAE submission benefits from consistent properties:

- Fire rating on walls/doors where claimed.
- Material name matching the finish schedule.
- Manufacturer fields only when specified—do not invent.
- Space names identical to the architectural room schedule.

Map once in the template; audit with schedules before export.

## Document controller tips

- Filename includes project, discipline, schema, revision, date.
- Reject uploads that lack a checker report PDF.
- Keep a register of which IFC produced which drawing issue.
- On portal failure, archive the error message with the file hash.

## OpenBIM benefits for mixed UAE teams

Main contractors rarely share one authoring tool across every subconsultant. IFC lets architecture in Revit, structure in another platform, and MEP from a specialist still meet in a federated check. That is the point of buildingSMART standards—not ideology.

When a client insists on native files only, still keep IFC as the coordination exchange format unless the BEP forbids it. Native files remain the authoring truth; IFC is the bridge.

For early massing that is not yet BIM-ready, remember Forma exports are concept aids—rebuild cleanly before authority IFC drops.

## Version pinning

Pin Revit/Archicad build numbers in the BEP for the submission window. Mid-project upgrades that change IFC exporters are a classic source of last-week portal failures. If an upgrade is mandatory, re-run the dress rehearsal before the authority date.

## Training drill for the team

Pick a completed small project, export IFC with the new BEP settings, federate, and score errors. Fix the template until the drill passes. Doing that drill on a live portal deadline is how teams learn the hard way.

## Summary

Clean **IFC OpenBIM Dubai** submissions come from boring consistency: pinned software versions, agreed schema, shared coordinates, validated property sets, and a dress rehearsal before the portal date. Pair models with matching drawing packages and clash close-out so Build in Dubai reviewers—and any AI-assisted checks—see one coherent project story.

## FAQ

### What is IFC OpenBIM for Dubai projects?

IFC is the openBIM schema used to exchange building models between different software. Dubai BIM submissions increasingly expect clean IFC (or specified model formats) that pass unit, classification and geometry checks.

### Which IFC version should I export?

Use the version stated in the project BEP or DM submission guide for your permit date. Confirm schema (e.g. IFC2x3 vs IFC4) before batch export.

### Can Archicad and Revit both deliver IFC for the same project?

Yes—openBIM is designed for that—but only if coordinates, classification and MVD/view settings are agreed in the BEP and validated on a federated check.

Need drawings that stay aligned to your IFC deliverables? [d3ddd.com](https://d3ddd.com/) · [info@d3ddd.com](mailto:info@d3ddd.com).

Originally published on [ShoaibSite](https://shoaibsite.blogspot.com/2026/10/blog-post_877.html).
