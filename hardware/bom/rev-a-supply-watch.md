# Rev A Supply Watch

Verified against current vendor and manufacturer product pages on `2026-06-29`; power-entry rows (wall adapter and DC jack) re-verified `2026-07-04`.

This file is not the main BOM. It exists so rev-A does not drift onto rare or awkward parts while the schematics are still being captured.

## Preferred Parts To Keep

| Function | Preferred Part | Reason To Keep It | Current Note |
| --- | --- | --- | --- |
| JFET/BiFET input front end | `OPA1644AIDR` | JFET input, audio-grade, aligns with user preference | still the best architectural fit, but current stocking is weaker than the rest of the core BOM |
| main dual audio op amp | `OPA1656IDR` | strong noise/headroom performance and `+/-18V` capability | currently healthy enough to keep as the default audio dual |
| primary send transistor pair | `BD139-16` / `BD140-16` | common through-hole complementary pair, easy to cool and service | keep as preferred rev-A class-AB send pair |
| relay | `G6K-2F-Y-DC5` | compact low-signal audio routing relay | currently easy enough to keep without redesign pressure |
| external power adapter | `WSU240-0750` | regulated `+24 VDC` SMPS, UL 62368-1, keeps mains outside the enclosure | selected `2026-07-04`; DigiKey showed `>1000` in stock at `USD 12.43`; retires the unregulated-sample risk |
| service-endcap DC jack | `PJ-005A` | matches the Triad adapter's `5.5 x 2.1 mm` center-positive plug | same mounting hole and hardware as the prior `PJ-005B` |

## Current Availability Snapshot

Checked on `2026-06-29`.

| Part | Current Source Snapshot | Design Impact |
| --- | --- | --- |
| `OPA1644AIDR` | DigiKey currently lists it at about `USD 4.65` and still shows it as not normally stocked | keep as the preferred JFET quad, but do not let rev-A depend on it being the only workable front-end option |
| `OPA1656IDR` | DigiKey currently shows thousands in stock with a `1 pc` price of about `USD 2.99` | keep as the main dual op amp without extra sourcing concern |
| `OPA1679IDR` | DigiKey currently shows it out of stock and backorderable | keep the topology, but keep an approved quad-op-amp alternate ready |
| `OPA1664AIDR` | DigiKey currently shows several thousand in stock at about `USD 3.68` | strongest practical alternate to `OPA1679IDR` right now |
| `TL074HIDR` | DigiKey currently shows thousands in stock at about `USD 0.40` | emergency commodity fallback only for lower-risk routing/filter functions |
| `G6K-2F-Y-DC5` | Mouser currently shows stock with a unit price about `USD 4.89` | no immediate reason to redesign around a different relay |
| `WSU240-0750` | DigiKey on `2026-07-04` showed `USD 12.43` at qty 1 with over `1,000` in stock | regulated adapter choice removes the unregulated-sample risk from the power entry path |
| `PJ-005A` | DigiKey on `2026-07-04` showed it available at about `USD 3.07` with over `15,000` in stock | matches the Triad `5.5 x 2.1 mm` plug; `PJ-005B` only returns if a future adapter uses a 2.5 mm barrel |
| `NCJ6FI-S` | Mouser currently shows it at about `USD 4.71`, while Neutrik still positions the family primarily as a combined XLR/TRS input-style connector | electrical requirement is preserved, but the output-side mechanical convention still needs final sanity-check |

## Approved Alternates

| Preferred Part | First Alternate | When To Use It | Notes |
| --- | --- | --- | --- |
| `OPA1644AIDR` | `2x OPA1642AIDR` | use if the preferred JFET quad is the sourcing bottleneck | preserves the same JFET family and `+/-18V` tolerance at the cost of one extra package |
| `OPA1679IDR` | `OPA1664AIDR` | use if `OPA1679IDR` lead time becomes the blocker | good fit for routing, crossfade, and filter duties; confirm gain-bandwidth and current budget during capture |
| `OPA1679IDR` | `TL074HIDR` | use only if a very common commodity quad is needed for the first bench spin | acceptable only on the lower-risk routing/filter blocks after noise and headroom review |
| `NCJ6FI-S` | `NCJ6FA-H` | use if the exact combo jack mechanical variant changes | recheck panel cutout and XLR orientation before metalwork freeze |
| `WSU240-0750` | `L6R20-240` | use if the Triad adapter goes out of stock | same regulated `+24 V` nominal at 20 W; confirm `5.5 x 2.1 mm` center-positive plug at order time |

## Source Links Used For This Snapshot

- `OPA1644AIDR`
  - [DigiKey listing](https://www.digikey.com/en/products/detail/texas-instruments/OPA1644AIDR/2353575)
  - [TI OPA1644 family datasheet](https://www.ti.com/lit/gpn/OPA1644)
- `OPA1656IDR`
  - [DigiKey listing](https://www.digikey.com/en/products/detail/texas-instruments/OPA1656IDR/10715414)
  - [TI part page](https://www.ti.com/product/OPA1656/part-details/OPA1656IDR)
- `OPA1679IDR`
  - [DigiKey listing](https://www.digikey.com/en/products/detail/texas-instruments/OPA1679IDR/7034963)
  - [TI product page](https://www.ti.com/product/OPA1679)
- `OPA1664AIDR`
  - [DigiKey listing](https://www.digikey.com/en/products/detail/texas-instruments/OPA1664AIDR/3674882)
  - [TI part page](https://www.ti.com/product/OPA1664/part-details/OPA1664AIDR)
- `OPA1642AIDR`
  - [DigiKey listing](https://www.digikey.com/en/products/detail/texas-instruments/OPA1642AIDR/2261898)
  - [TI part page](https://www.ti.com/product/OPA1642/part-details/OPA1642AIDR)
- `TL074HIDR`
  - [DigiKey listing](https://www.digikey.com/en/products/detail/texas-instruments/TL074HIDR/13563033)
- `G6K-2F-Y-DC5`
  - [DigiKey listing](https://www.digikey.com/en/products/detail/omron-electronics-inc-emc-div/G6K-2F-Y-DC5/307648)
  - [Mouser listing](https://www.mouser.com/ProductDetail/Omron-Electronics/G6K-2F-Y-DC5?qs=SXIVkn%252Bm38kNKs%252BIzeJTSg%3D%3D&srsltid=AfmBOorKdqF-Mys3PTqHyL0_3t81mo0i4_ngCWICcV0bzXBieiEKnqAl)
- `WSU240-0750`
  - [DigiKey listing](https://www.digikey.com/en/products/detail/triad-magnetics/WSU240-0750/3094933)
  - [Triad WSU240-0750 datasheet](https://catalog.triadmagnetics.com/Asset/WSU240-0750.pdf)
- `PJ-005A`
  - [DigiKey listing](https://www.digikey.com/en/products/detail/same-sky-formerly-cui-devices/PJ-005A/165838)
- `NCJ6FI-S`
  - [Neutrik product page](https://www.neutrik.com/en/product/ncj6fi-s)
  - [Neutrik datasheet](https://www.neutrik.com/en/product/ncj6fi-s.pdf)

## Parts To Keep Out Of The SMD Quote

- the four spring tanks
- their tank harnesses and RCA cable assemblies
- enclosure and panel metalwork
- the user-supplied enclosure tube

## Current Procurement Direction

- let the PCB assembler source and place the common SMD parts
- keep the active BOM centered on TI audio op amps, Omron relays, and common JST families
- treat spring tanks and large mechanical hardware as separate procurement items
