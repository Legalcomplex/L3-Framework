# S3 World Benchmark — Sweep Report

Generated 2026-06-20 16:03Z by `run_world_sweep.py` + `make_sweep_report.py`.

## Run setup

- **Model:** `grok-4-1-fast-non-reasoning` via `xai` (flash tier, thinking disabled, temperature 0, 1 round per item)
- **Packs:** 227/227 passed (pass = zero unresolved API errors and 100% of items parsed or documented blocked; accuracy is NOT a pass criterion)
- **Items:** 2716 run, 2716 parsed, 0 blocked
- **Sampling:** full packs (all items)
- **Tokens:** 536,107 in / 82,961 out across 2,716 calls
- **Estimated cost:** $0.09 (at $0.1/M input, $0.4/M output)
- **Wall time:** 624s

Prompt construction and True/False parsing mirror `run_s3_claude.py` exactly (same placeholder fill, same first-`\b(true|false)\b` extraction), so numbers are comparable to prior S3 runs.

## Aggregate results

- **Aggregate accuracy: 51.9%** (1411/2716) — chance is 50%.
- **TRUE items:** 5.8% correct (1358 items)
- **FALSE items:** 98.1% correct (1358 items)
- **Model said "True"** on 3.9% of all judged items.

**Asymmetry: the model over-denies.** It rejects fabricated citations more readily than it confirms real ones (FALSE-recall 98.1% vs TRUE-recall 5.8%). This is skepticism without knowledge: it doubts everything, including real documents, rather than knowing which citations exist.

## Accuracy by mutation class (FALSE items)

| Mutation | n | Accuracy (caught) |
|---|---|---|
| wrong-source | 718 | 100.0% |
| id-mutation | 234 | 97.9% |
| date-shift | 406 | 94.8% |

## Accuracy by statement shape

| Shape | n | Accuracy |
|---|---|---|
| S1-published-via | 1536 | 49.4% |
| S2-decision | 798 | 51.5% |
| S3-identifier | 382 | 63.1% |

## Per-jurisdiction accuracy (best → worst)

| # | Flag | CC | Jurisdiction | Items | Accuracy | Pass |
|---|---|---|---|---|---|---|
| 1 | 🇦🇼 | AW | Aruba | 12 | 75% | PASS |
| 2 | 🇧🇴 | BO | Bolivia | 12 | 75% | PASS |
| 3 | 🇮🇳 | IN | India | 12 | 75% | PASS |
| 4 | 🇳🇴 | NO | Norway | 12 | 75% | PASS |
| 5 | 🇹🇻 | TV | Tuvalu | 12 | 75% | PASS |
| 6 | 🇨🇫 | CF | Central African Republic | 12 | 67% | PASS |
| 7 | 🇨🇷 | CR | Costa Rica | 12 | 67% | PASS |
| 8 | 🇨🇾 | CY | Cyprus | 12 | 67% | PASS |
| 9 | 🇪🇬 | EG | Egypt | 12 | 67% | PASS |
| 10 | 🇪🇸 | ES | Spain | 12 | 67% | PASS |
| 11 | 🇬🇦 | GA | Gabon | 12 | 67% | PASS |
| 12 | 🇭🇰 | HK | Hong Kong | 12 | 67% | PASS |
| 13 | 🇱🇻 | LV | Latvia | 12 | 67% | PASS |
| 14 | 🇵🇱 | PL | Poland | 12 | 67% | PASS |
| 15 | 🇸🇮 | SI | Slovenia | 12 | 67% | PASS |
| 16 | 🇧🇧 | BB | Barbados | 12 | 58% | PASS |
| 17 | 🇧🇪 | BE | Belgium | 12 | 58% | PASS |
| 18 | 🇧🇫 | BF | Burkina Faso | 12 | 58% | PASS |
| 19 | 🇧🇮 | BI | Burundi | 12 | 58% | PASS |
| 20 | 🇨🇩 | CD | Democratic Republic of the Congo | 12 | 58% | PASS |
| 21 | 🇨🇬 | CG | Republic of the Congo | 12 | 58% | PASS |
| 22 | 🇨🇰 | CK | Cook Islands | 12 | 58% | PASS |
| 23 | 🇨🇿 | CZ | Czechia | 12 | 58% | PASS |
| 24 | 🇩🇴 | DO | Dominican Republic | 12 | 58% | PASS |
| 25 | 🇩🇿 | DZ | Algeria | 12 | 58% | PASS |
| 26 | 🇪🇺 | EU | European Union | 12 | 58% | PASS |
| 27 | 🇰🇮 | KI | Kiribati | 12 | 58% | PASS |
| 28 | 🇱🇰 | LK | Sri Lanka | 12 | 58% | PASS |
| 29 | 🇲🇩 | MD | Moldova | 12 | 58% | PASS |
| 30 | 🇲🇬 | MG | Madagascar | 12 | 58% | PASS |
| 31 | 🇳🇦 | NA | Namibia | 12 | 58% | PASS |
| 32 | 🇳🇪 | NE | Niger | 12 | 58% | PASS |
| 33 | 🇳🇬 | NG | Nigeria | 12 | 58% | PASS |
| 34 | 🇳🇮 | NI | Nicaragua | 12 | 58% | PASS |
| 35 | 🇵🇪 | PE | Peru | 12 | 58% | PASS |
| 36 | 🇵🇾 | PY | Paraguay | 12 | 58% | PASS |
| 37 | 🇸🇬 | SG | Singapore | 12 | 58% | PASS |
| 38 | 🇹🇩 | TD | Chad | 12 | 58% | PASS |
| 39 | 🇹🇬 | TG | Togo | 12 | 58% | PASS |
| 40 | 🇹🇼 | TW | Taiwan | 12 | 58% | PASS |
| 41 | 🇺🇸 | US | United States | 12 | 58% | PASS |
| 42 | 🇺🇾 | UY | Uruguay | 12 | 58% | PASS |
| 43 | 🇽🇰 | XK | Kosovo | 12 | 58% | PASS |
| 44 | 🇿🇦 | ZA | South Africa | 12 | 58% | PASS |
| 45 | 🇦🇩 | AD | Andorra | 12 | 50% | PASS |
| 46 | 🇦🇪 | AE | United Arab Emirates | 12 | 50% | PASS |
| 47 | 🇦🇬 | AG | Antigua and Barbuda | 12 | 50% | PASS |
| 48 | 🇦🇮 | AI | Anguilla | 12 | 50% | PASS |
| 49 | 🇦🇱 | AL | Albania | 12 | 50% | PASS |
| 50 | 🇦🇲 | AM | Armenia | 12 | 50% | PASS |
| 51 | 🇦🇴 | AO | Angola | 12 | 50% | PASS |
| 52 | 🇦🇸 | AS | American Samoa | 6 | 50% | PASS |
| 53 | 🇦🇹 | AT | Austria | 12 | 50% | PASS |
| 54 | 🇦🇺 | AU | Australia | 12 | 50% | PASS |
| 55 | 🇦🇽 | AX | Åland Islands | 12 | 50% | PASS |
| 56 | 🇦🇿 | AZ | Azerbaijan | 12 | 50% | PASS |
| 57 | 🇧🇩 | BD | Bangladesh | 12 | 50% | PASS |
| 58 | 🇧🇬 | BG | Bulgaria | 12 | 50% | PASS |
| 59 | 🇧🇭 | BH | Bahrain | 12 | 50% | PASS |
| 60 | 🇧🇱 | BL | Saint Barthélemy | 12 | 50% | PASS |
| 61 | 🇧🇲 | BM | Bermuda | 12 | 50% | PASS |
| 62 | 🇧🇳 | BN | Brunei | 12 | 50% | PASS |
| 63 | 🇧🇶 | BQ | Caribbean Netherlands | 12 | 50% | PASS |
| 64 | 🇧🇷 | BR | Brazil | 12 | 50% | PASS |
| 65 | 🇧🇸 | BS | Bahamas | 12 | 50% | PASS |
| 66 | 🇧🇹 | BT | Bhutan | 12 | 50% | PASS |
| 67 | 🇧🇼 | BW | Botswana | 12 | 50% | PASS |
| 68 | 🇧🇿 | BZ | Belize | 12 | 50% | PASS |
| 69 | 🇨🇦 | CA | Canada | 12 | 50% | PASS |
| 70 | 🇨🇭 | CH | Switzerland | 12 | 50% | PASS |
| 71 | 🇨🇮 | CI | Côte d'Ivoire | 12 | 50% | PASS |
| 72 | 🇨🇱 | CL | Chile | 12 | 50% | PASS |
| 73 | 🇨🇲 | CM | Cameroon | 12 | 50% | PASS |
| 74 | 🇨🇳 | CN | China | 12 | 50% | PASS |
| 75 | 🇨🇴 | CO | Colombia | 12 | 50% | PASS |
| 76 | 🏰 | COE | Council of Europe | 12 | 50% | PASS |
| 77 | 🇨🇺 | CU | Cuba | 12 | 50% | PASS |
| 78 | 🇨🇻 | CV | Cape Verde | 12 | 50% | PASS |
| 79 | 🇨🇼 | CW | Curaçao | 12 | 50% | PASS |
| 80 | 🇩🇪 | DE | Germany | 12 | 50% | PASS |
| 81 | 🇩🇯 | DJ | Djibouti | 12 | 50% | PASS |
| 82 | 🇩🇰 | DK | Denmark | 12 | 50% | PASS |
| 83 | 🇩🇲 | DM | Dominica | 12 | 50% | PASS |
| 84 | 🇪🇨 | EC | Ecuador | 12 | 50% | PASS |
| 85 | 🇪🇪 | EE | Estonia | 12 | 50% | PASS |
| 86 | 🇪🇷 | ER | Eritrea | 12 | 50% | PASS |
| 87 | 🇪🇹 | ET | Ethiopia | 12 | 50% | PASS |
| 88 | 🇫🇮 | FI | Finland | 12 | 50% | PASS |
| 89 | 🇫🇯 | FJ | Fiji | 12 | 50% | PASS |
| 90 | 🇫🇰 | FK | Falkland Islands | 12 | 50% | PASS |
| 91 | 🇫🇲 | FM | Micronesia | 10 | 50% | PASS |
| 92 | 🇫🇴 | FO | Faroe Islands | 12 | 50% | PASS |
| 93 | 🇬🇩 | GD | Grenada | 12 | 50% | PASS |
| 94 | 🇬🇪 | GE | Georgia | 12 | 50% | PASS |
| 95 | 🇬🇬 | GG | Guernsey | 12 | 50% | PASS |
| 96 | 🇬🇭 | GH | Ghana | 12 | 50% | PASS |
| 97 | 🇬🇮 | GI | Gibraltar | 12 | 50% | PASS |
| 98 | 🇬🇱 | GL | Greenland | 12 | 50% | PASS |
| 99 | 🇬🇲 | GM | Gambia | 12 | 50% | PASS |
| 100 | 🇬🇳 | GN | Guinea | 12 | 50% | PASS |
| 101 | 🇬🇶 | GQ | Equatorial Guinea | 12 | 50% | PASS |
| 102 | 🇬🇷 | GR | Greece | 12 | 50% | PASS |
| 103 | 🇬🇹 | GT | Guatemala | 12 | 50% | PASS |
| 104 | 🇬🇺 | GU | Guam | 12 | 50% | PASS |
| 105 | 🇬🇼 | GW | Guinea-Bissau | 12 | 50% | PASS |
| 106 | 🇬🇾 | GY | Guyana | 12 | 50% | PASS |
| 107 | 🇭🇳 | HN | Honduras | 12 | 50% | PASS |
| 108 | 🇭🇷 | HR | Croatia | 12 | 50% | PASS |
| 109 | 🇭🇹 | HT | Haiti | 12 | 50% | PASS |
| 110 | 🇭🇺 | HU | Hungary | 12 | 50% | PASS |
| 111 | 🇮🇩 | ID | Indonesia | 12 | 50% | PASS |
| 112 | 🇮🇪 | IE | Ireland | 12 | 50% | PASS |
| 113 | 🇮🇱 | IL | Israel | 12 | 50% | PASS |
| 114 | 🇮🇲 | IM | Isle of Man | 12 | 50% | PASS |
| 115 |  | INTL | International | 12 | 50% | PASS |
| 116 | 🇮🇶 | IQ | Iraq | 12 | 50% | PASS |
| 117 | 🇮🇷 | IR | Iran | 12 | 50% | PASS |
| 118 | 🇮🇸 | IS | Iceland | 12 | 50% | PASS |
| 119 | 🇮🇹 | IT | Italy | 12 | 50% | PASS |
| 120 | 🇯🇪 | JE | Jersey | 12 | 50% | PASS |
| 121 | 🇯🇲 | JM | Jamaica | 12 | 50% | PASS |
| 122 | 🇯🇴 | JO | Jordan | 12 | 50% | PASS |
| 123 | 🇰🇪 | KE | Kenya | 12 | 50% | PASS |
| 124 | 🇰🇬 | KG | Kyrgyzstan | 12 | 50% | PASS |
| 125 | 🇰🇭 | KH | Cambodia | 12 | 50% | PASS |
| 126 | 🇰🇲 | KM | Comoros | 12 | 50% | PASS |
| 127 | 🇰🇳 | KN | Saint Kitts and Nevis | 12 | 50% | PASS |
| 128 | 🇰🇷 | KR | South Korea | 12 | 50% | PASS |
| 129 | 🇰🇾 | KY | Cayman Islands | 12 | 50% | PASS |
| 130 | 🇰🇿 | KZ | Kazakhstan | 12 | 50% | PASS |
| 131 | 🇱🇦 | LA | Laos | 12 | 50% | PASS |
| 132 | 🇱🇧 | LB | Lebanon | 12 | 50% | PASS |
| 133 | 🇱🇨 | LC | Saint Lucia | 12 | 50% | PASS |
| 134 | 🇱🇷 | LR | Liberia | 12 | 50% | PASS |
| 135 | 🇱🇸 | LS | Lesotho | 12 | 50% | PASS |
| 136 | 🇱🇹 | LT | Lithuania | 12 | 50% | PASS |
| 137 | 🇱🇺 | LU | Luxembourg | 12 | 50% | PASS |
| 138 | 🇱🇾 | LY | Libya | 12 | 50% | PASS |
| 139 | 🇲🇦 | MA | Morocco | 12 | 50% | PASS |
| 140 | 🇲🇨 | MC | Monaco | 12 | 50% | PASS |
| 141 | 🇲🇪 | ME | Montenegro | 12 | 50% | PASS |
| 142 | 🇲🇫 | MF | Saint Martin | 12 | 50% | PASS |
| 143 | 🇲🇭 | MH | Marshall Islands | 12 | 50% | PASS |
| 144 | 🇲🇰 | MK | North Macedonia | 12 | 50% | PASS |
| 145 | 🇲🇱 | ML | Mali | 12 | 50% | PASS |
| 146 | 🇲🇲 | MM | Myanmar | 12 | 50% | PASS |
| 147 | 🇲🇳 | MN | Mongolia | 12 | 50% | PASS |
| 148 | 🇲🇴 | MO | Macao | 12 | 50% | PASS |
| 149 | 🇲🇷 | MR | Mauritania | 12 | 50% | PASS |
| 150 | 🇲🇸 | MS | Montserrat | 12 | 50% | PASS |
| 151 | 🇲🇹 | MT | Malta | 12 | 50% | PASS |
| 152 | 🇲🇻 | MV | Maldives | 12 | 50% | PASS |
| 153 | 🇲🇼 | MW | Malawi | 12 | 50% | PASS |
| 154 | 🇲🇿 | MZ | Mozambique | 12 | 50% | PASS |
| 155 | 🇳🇱 | NL | Netherlands | 12 | 50% | PASS |
| 156 | 🇳🇷 | NR | Nauru | 12 | 50% | PASS |
| 157 | 🇳🇺 | NU | Niue | 12 | 50% | PASS |
| 158 | 🇳🇿 | NZ | New Zealand | 12 | 50% | PASS |
| 159 | 🇴🇲 | OM | Oman | 12 | 50% | PASS |
| 160 | 🇵🇦 | PA | Panama | 12 | 50% | PASS |
| 161 | 🇵🇫 | PF | French Polynesia | 12 | 50% | PASS |
| 162 | 🇵🇬 | PG | Papua New Guinea | 12 | 50% | PASS |
| 163 | 🇵🇭 | PH | Philippines | 12 | 50% | PASS |
| 164 | 🇵🇰 | PK | Pakistan | 12 | 50% | PASS |
| 165 | 🇵🇲 | PM | Saint Pierre and Miquelon | 12 | 50% | PASS |
| 166 | 🇵🇳 | PN | Pitcairn Islands | 12 | 50% | PASS |
| 167 | 🇵🇷 | PR | Puerto Rico | 12 | 50% | PASS |
| 168 | 🇵🇸 | PS | Palestine | 12 | 50% | PASS |
| 169 | 🇵🇹 | PT | Portugal | 12 | 50% | PASS |
| 170 | 🇵🇼 | PW | Palau | 12 | 50% | PASS |
| 171 | 🇶🇦 | QA | Qatar | 12 | 50% | PASS |
| 172 | 🇷🇴 | RO | Romania | 12 | 50% | PASS |
| 173 | 🇷🇸 | RS | Serbia | 12 | 50% | PASS |
| 174 | 🇷🇺 | RU | Russia | 12 | 50% | PASS |
| 175 | 🇷🇼 | RW | Rwanda | 12 | 50% | PASS |
| 176 | 🇸🇦 | SA | Saudi Arabia | 12 | 50% | PASS |
| 177 | 🇸🇧 | SB | Solomon Islands | 12 | 50% | PASS |
| 178 | 🇸🇨 | SC | Seychelles | 12 | 50% | PASS |
| 179 | 🇸🇩 | SD | Sudan | 12 | 50% | PASS |
| 180 | 🇸🇪 | SE | Sweden | 12 | 50% | PASS |
| 181 | 🇸🇭 | SH | Saint Helena | 12 | 50% | PASS |
| 182 | 🇸🇰 | SK | Slovakia | 12 | 50% | PASS |
| 183 | 🇸🇱 | SL | Sierra Leone | 12 | 50% | PASS |
| 184 | 🇸🇲 | SM | San Marino | 12 | 50% | PASS |
| 185 | 🇸🇳 | SN | Senegal | 12 | 50% | PASS |
| 186 | 🇸🇴 | SO | Somalia | 12 | 50% | PASS |
| 187 | 🇸🇷 | SR | Suriname | 12 | 50% | PASS |
| 188 | 🇸🇸 | SS | South Sudan | 12 | 50% | PASS |
| 189 | 🇸🇻 | SV | El Salvador | 12 | 50% | PASS |
| 190 | 🇸🇽 | SX | Sint Maarten | 12 | 50% | PASS |
| 191 | 🇸🇾 | SY | Syria | 12 | 50% | PASS |
| 192 | 🇸🇿 | SZ | Eswatini | 12 | 50% | PASS |
| 193 | 🇹🇨 | TC | Turks and Caicos Islands | 12 | 50% | PASS |
| 194 | 🇹🇭 | TH | Thailand | 12 | 50% | PASS |
| 195 | 🇹🇯 | TJ | Tajikistan | 12 | 50% | PASS |
| 196 | 🇹🇱 | TL | Timor-Leste | 12 | 50% | PASS |
| 197 | 🇹🇲 | TM | Turkmenistan | 12 | 50% | PASS |
| 198 | 🇹🇳 | TN | Tunisia | 12 | 50% | PASS |
| 199 | 🇹🇴 | TO | Tonga | 12 | 50% | PASS |
| 200 | 🇹🇷 | TR | Turkey | 12 | 50% | PASS |
| 201 | 🇹🇹 | TT | Trinidad and Tobago | 12 | 50% | PASS |
| 202 | 🇹🇿 | TZ | Tanzania | 12 | 50% | PASS |
| 203 | 🇺🇬 | UG | Uganda | 12 | 50% | PASS |
| 204 | 🇬🇧 | UK | United Kingdom | 12 | 50% | PASS |
| 205 | 🇺🇳 | UN | United Nations | 12 | 50% | PASS |
| 206 | 🇺🇿 | UZ | Uzbekistan | 12 | 50% | PASS |
| 207 | 🇻🇦 | VA | Vatican City | 12 | 50% | PASS |
| 208 | 🇻🇨 | VC | Saint Vincent and the Grenadines | 12 | 50% | PASS |
| 209 | 🇻🇬 | VG | British Virgin Islands | 12 | 50% | PASS |
| 210 | 🇻🇮 | VI | U.S. Virgin Islands | 12 | 50% | PASS |
| 211 | 🇻🇳 | VN | Vietnam | 12 | 50% | PASS |
| 212 | 🇻🇺 | VU | Vanuatu | 12 | 50% | PASS |
| 213 | 🇼🇫 | WF | Wallis and Futuna | 12 | 50% | PASS |
| 214 | 🇼🇸 | WS | Samoa | 12 | 50% | PASS |
| 215 | 🇾🇪 | YE | Yemen | 12 | 50% | PASS |
| 216 | 🇿🇲 | ZM | Zambia | 12 | 50% | PASS |
| 217 | 🇿🇼 | ZW | Zimbabwe | 12 | 50% | PASS |
| 218 | 🇧🇦 | BA | Bosnia & Herzegovina | 12 | 42% | PASS |
| 219 | 🇧🇯 | BJ | Benin | 12 | 42% | PASS |
| 220 | 🇫🇷 | FR | France | 12 | 42% | PASS |
| 221 | 🇯🇵 | JP | Japan | 12 | 42% | PASS |
| 222 | 🇱🇮 | LI | Liechtenstein | 12 | 42% | PASS |
| 223 | 🇲🇺 | MU | Mauritius | 12 | 42% | PASS |
| 224 | 🇲🇽 | MX | Mexico | 12 | 42% | PASS |
| 225 | 🇺🇦 | UA | Ukraine | 12 | 42% | PASS |
| 226 | 🇻🇪 | VE | Venezuela | 12 | 42% | PASS |
| 227 | 🇦🇷 | AR | Argentina | 12 | 33% | PASS |

Distribution: 5 packs ≥75%, 222 packs within the 33–67% chance band, 0 packs ≤25%.

## Iteration log

(no iteration log found)

## Interpretation

The aggregate score of **51.9%** against a 50% chance baseline is the finding. These are bibliographic claims about real, recently collected official legal documents (titles, dates, publishing sources, identifiers) across 227 jurisdictions. A score near chance means the model cannot verify citations from these jurisdictions from parametric memory: it does not know which decisions, gazettes and acts exist, so it cannot tell a real citation from a controlled fabrication. **Retrieval grounding against the actual source corpus is therefore mandatory** for any citation-reliability claim — this is precisely the gap the S3 retrieval extension (Sabaio L3) is built to close.

Where scores rise well above chance, inspection shows it is mostly the FALSE mutations being caught on internal-consistency grounds (e.g. a cross-jurisdiction `wrong-source` trap pairing a Dutch ECLI with a Gibraltar gazette is detectable without knowing the document), not genuine knowledge of the documents. TRUE items — which require actually knowing the document exists — hover near or below chance for most jurisdictions, and recent documents (2025–26 sample snapshot) sit past the model's training cutoff by construction.
