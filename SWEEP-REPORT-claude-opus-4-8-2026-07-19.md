# S3 World Benchmark — Sweep Report

Generated 2026-07-19 08:28Z by `run_world_sweep.py` + `make_sweep_report.py`.

## Run setup

- **Model:** `claude-opus-4-8` via `anthropic` (thinking disabled, temperature at provider default (not accepted on these models), 1 round per item, no retrieval and no web access)
- **Packs:** 206/227 passed (pass = zero unresolved API errors and 100% of items parsed or documented blocked; accuracy is NOT a pass criterion)
- **Items:** 2716 run, 2691 parsed, 0 blocked
- **Sampling:** full packs (all items)
- **Tokens:** 357,203 in / 137,932 out across 2,716 calls
- **Estimated cost:** $5.23 (at $5.0/M input, $25.0/M output)
- **Wall time:** 1334s

Prompt construction and True/False parsing mirror `run_s3_claude.py` exactly (same placeholder fill, same first-`\b(true|false)\b` extraction), so numbers are comparable to prior S3 runs.

## Aggregate results

- **Aggregate accuracy: 52.6%** (1416/2691) — chance is 50%.
- **TRUE items:** 7.4% correct (1342 items)
- **FALSE items:** 97.6% correct (1349 items)
- **Model said "True"** on 4.9% of all judged items.

**Asymmetry: the model over-denies.** It rejects fabricated citations more readily than it confirms real ones (FALSE-recall 97.6% vs TRUE-recall 7.4%). This is skepticism without knowledge: it doubts everything, including real documents, rather than knowing which citations exist.

## Accuracy by mutation class (FALSE items)

| Mutation | n | Accuracy (caught) |
|---|---|---|
| wrong-source | 718 | 100.0% |
| id-mutation | 232 | 99.1% |
| date-shift | 399 | 92.5% |

## Accuracy by statement shape

| Shape | n | Accuracy |
|---|---|---|
| S1-published-via | 1532 | 51.8% |
| S2-decision | 781 | 49.7% |
| S3-identifier | 378 | 62.2% |

## Per-jurisdiction accuracy (best → worst)

| # | Flag | CC | Jurisdiction | Items | Accuracy | Pass |
|---|---|---|---|---|---|---|
| 1 | 🇦🇼 | AW | Aruba | 12 | 83% | PASS |
| 2 | 🇰🇮 | KI | Kiribati | 12 | 82% | FAIL |
| 3 | 🇦🇺 | AU | Australia | 12 | 75% | PASS |
| 4 | 🏰 | COE | Council of Europe | 12 | 75% | PASS |
| 5 | 🇺🇳 | UN | United Nations | 12 | 75% | PASS |
| 6 | 🇦🇩 | AD | Andorra | 12 | 67% | PASS |
| 7 | 🇧🇶 | BQ | Caribbean Netherlands | 12 | 67% | PASS |
| 8 | 🇩🇿 | DZ | Algeria | 12 | 67% | PASS |
| 9 | 🇫🇮 | FI | Finland | 12 | 67% | PASS |
| 10 | 🇬🇭 | GH | Ghana | 12 | 67% | PASS |
| 11 | 🇮🇱 | IL | Israel | 12 | 67% | PASS |
| 12 | 🇮🇸 | IS | Iceland | 12 | 67% | PASS |
| 13 | 🇯🇪 | JE | Jersey | 12 | 67% | PASS |
| 14 | 🇯🇵 | JP | Japan | 12 | 67% | PASS |
| 15 | 🇱🇮 | LI | Liechtenstein | 12 | 67% | PASS |
| 16 | 🇵🇱 | PL | Poland | 12 | 67% | PASS |
| 17 | 🇹🇼 | TW | Taiwan | 12 | 67% | PASS |
| 18 | 🇻🇦 | VA | Vatican City | 12 | 67% | PASS |
| 19 | 🇧🇦 | BA | Bosnia & Herzegovina | 12 | 64% | FAIL |
| 20 | 🇨🇴 | CO | Colombia | 12 | 64% | FAIL |
| 21 | 🇵🇳 | PN | Pitcairn Islands | 12 | 64% | FAIL |
| 22 | 🇶🇦 | QA | Qatar | 12 | 64% | FAIL |
| 23 | 🇰🇷 | KR | South Korea | 12 | 60% | FAIL |
| 24 | 🇦🇴 | AO | Angola | 12 | 58% | PASS |
| 25 | 🇦🇷 | AR | Argentina | 12 | 58% | PASS |
| 26 | 🇧🇪 | BE | Belgium | 12 | 58% | PASS |
| 27 | 🇧🇹 | BT | Bhutan | 12 | 58% | PASS |
| 28 | 🇧🇼 | BW | Botswana | 12 | 58% | PASS |
| 29 | 🇨🇾 | CY | Cyprus | 12 | 58% | PASS |
| 30 | 🇫🇷 | FR | France | 12 | 58% | PASS |
| 31 | 🇭🇰 | HK | Hong Kong | 12 | 58% | PASS |
| 32 | 🇭🇹 | HT | Haiti | 12 | 58% | PASS |
| 33 | 🇮🇪 | IE | Ireland | 12 | 58% | PASS |
| 34 | 🇮🇳 | IN | India | 12 | 58% | PASS |
| 35 |  | INTL | International | 12 | 58% | PASS |
| 36 | 🇮🇹 | IT | Italy | 12 | 58% | PASS |
| 37 | 🇰🇭 | KH | Cambodia | 12 | 58% | PASS |
| 38 | 🇱🇦 | LA | Laos | 12 | 58% | PASS |
| 39 | 🇱🇨 | LC | Saint Lucia | 12 | 58% | PASS |
| 40 | 🇱🇷 | LR | Liberia | 12 | 58% | PASS |
| 41 | 🇱🇹 | LT | Lithuania | 12 | 58% | PASS |
| 42 | 🇲🇱 | ML | Mali | 12 | 58% | PASS |
| 43 | 🇲🇽 | MX | Mexico | 12 | 58% | PASS |
| 44 | 🇳🇬 | NG | Nigeria | 12 | 58% | PASS |
| 45 | 🇳🇮 | NI | Nicaragua | 12 | 58% | PASS |
| 46 | 🇴🇲 | OM | Oman | 12 | 58% | PASS |
| 47 | 🇵🇪 | PE | Peru | 12 | 58% | PASS |
| 48 | 🇵🇰 | PK | Pakistan | 12 | 58% | PASS |
| 49 | 🇵🇸 | PS | Palestine | 12 | 58% | PASS |
| 50 | 🇸🇦 | SA | Saudi Arabia | 12 | 58% | PASS |
| 51 | 🇹🇬 | TG | Togo | 12 | 58% | PASS |
| 52 | 🇹🇲 | TM | Turkmenistan | 12 | 58% | PASS |
| 53 | 🇺🇸 | US | United States | 12 | 58% | PASS |
| 54 | 🇺🇿 | UZ | Uzbekistan | 12 | 58% | PASS |
| 55 | 🇻🇳 | VN | Vietnam | 12 | 58% | PASS |
| 56 | 🇿🇲 | ZM | Zambia | 12 | 58% | PASS |
| 57 | 🇿🇦 | ZA | South Africa | 12 | 56% | FAIL |
| 58 | 🇨🇰 | CK | Cook Islands | 12 | 55% | FAIL |
| 59 | 🇨🇷 | CR | Costa Rica | 12 | 55% | FAIL |
| 60 | 🇪🇨 | EC | Ecuador | 12 | 55% | FAIL |
| 61 | 🇳🇴 | NO | Norway | 12 | 55% | FAIL |
| 62 | 🇵🇼 | PW | Palau | 12 | 55% | FAIL |
| 63 | 🇹🇳 | TN | Tunisia | 12 | 55% | FAIL |
| 64 | 🇬🇧 | UK | United Kingdom | 12 | 55% | FAIL |
| 65 | 🇺🇾 | UY | Uruguay | 12 | 55% | FAIL |
| 66 | 🇾🇪 | YE | Yemen | 12 | 55% | FAIL |
| 67 | 🇦🇪 | AE | United Arab Emirates | 12 | 50% | PASS |
| 68 | 🇦🇬 | AG | Antigua and Barbuda | 12 | 50% | PASS |
| 69 | 🇦🇮 | AI | Anguilla | 12 | 50% | PASS |
| 70 | 🇦🇱 | AL | Albania | 12 | 50% | PASS |
| 71 | 🇦🇲 | AM | Armenia | 12 | 50% | PASS |
| 72 | 🇦🇸 | AS | American Samoa | 6 | 50% | PASS |
| 73 | 🇦🇹 | AT | Austria | 12 | 50% | PASS |
| 74 | 🇦🇽 | AX | Åland Islands | 12 | 50% | PASS |
| 75 | 🇦🇿 | AZ | Azerbaijan | 12 | 50% | PASS |
| 76 | 🇧🇧 | BB | Barbados | 12 | 50% | PASS |
| 77 | 🇧🇩 | BD | Bangladesh | 12 | 50% | PASS |
| 78 | 🇧🇫 | BF | Burkina Faso | 12 | 50% | PASS |
| 79 | 🇧🇭 | BH | Bahrain | 12 | 50% | PASS |
| 80 | 🇧🇮 | BI | Burundi | 12 | 50% | PASS |
| 81 | 🇧🇯 | BJ | Benin | 12 | 50% | PASS |
| 82 | 🇧🇱 | BL | Saint Barthélemy | 12 | 50% | PASS |
| 83 | 🇧🇳 | BN | Brunei | 12 | 50% | PASS |
| 84 | 🇧🇴 | BO | Bolivia | 12 | 50% | PASS |
| 85 | 🇧🇸 | BS | Bahamas | 12 | 50% | PASS |
| 86 | 🇧🇿 | BZ | Belize | 12 | 50% | PASS |
| 87 | 🇨🇩 | CD | Democratic Republic of the Congo | 12 | 50% | PASS |
| 88 | 🇨🇫 | CF | Central African Republic | 12 | 50% | PASS |
| 89 | 🇨🇬 | CG | Republic of the Congo | 12 | 50% | PASS |
| 90 | 🇨🇭 | CH | Switzerland | 12 | 50% | PASS |
| 91 | 🇨🇮 | CI | Côte d'Ivoire | 12 | 50% | PASS |
| 92 | 🇨🇲 | CM | Cameroon | 12 | 50% | PASS |
| 93 | 🇨🇳 | CN | China | 12 | 50% | PASS |
| 94 | 🇨🇺 | CU | Cuba | 12 | 50% | PASS |
| 95 | 🇨🇻 | CV | Cape Verde | 12 | 50% | PASS |
| 96 | 🇨🇿 | CZ | Czechia | 12 | 50% | PASS |
| 97 | 🇩🇪 | DE | Germany | 12 | 50% | PASS |
| 98 | 🇩🇯 | DJ | Djibouti | 12 | 50% | PASS |
| 99 | 🇩🇰 | DK | Denmark | 12 | 50% | PASS |
| 100 | 🇩🇲 | DM | Dominica | 12 | 50% | PASS |
| 101 | 🇩🇴 | DO | Dominican Republic | 12 | 50% | PASS |
| 102 | 🇪🇪 | EE | Estonia | 12 | 50% | PASS |
| 103 | 🇪🇬 | EG | Egypt | 12 | 50% | PASS |
| 104 | 🇪🇷 | ER | Eritrea | 12 | 50% | PASS |
| 105 | 🇪🇸 | ES | Spain | 12 | 50% | PASS |
| 106 | 🇪🇺 | EU | European Union | 12 | 50% | PASS |
| 107 | 🇫🇯 | FJ | Fiji | 12 | 50% | PASS |
| 108 | 🇫🇰 | FK | Falkland Islands | 12 | 50% | PASS |
| 109 | 🇫🇲 | FM | Micronesia | 10 | 50% | PASS |
| 110 | 🇫🇴 | FO | Faroe Islands | 12 | 50% | PASS |
| 111 | 🇬🇦 | GA | Gabon | 12 | 50% | PASS |
| 112 | 🇬🇩 | GD | Grenada | 12 | 50% | PASS |
| 113 | 🇬🇪 | GE | Georgia | 12 | 50% | FAIL |
| 114 | 🇬🇬 | GG | Guernsey | 12 | 50% | PASS |
| 115 | 🇬🇮 | GI | Gibraltar | 12 | 50% | PASS |
| 116 | 🇬🇱 | GL | Greenland | 12 | 50% | PASS |
| 117 | 🇬🇲 | GM | Gambia | 12 | 50% | PASS |
| 118 | 🇬🇳 | GN | Guinea | 12 | 50% | PASS |
| 119 | 🇬🇶 | GQ | Equatorial Guinea | 12 | 50% | PASS |
| 120 | 🇬🇷 | GR | Greece | 12 | 50% | PASS |
| 121 | 🇬🇺 | GU | Guam | 12 | 50% | PASS |
| 122 | 🇬🇼 | GW | Guinea-Bissau | 12 | 50% | PASS |
| 123 | 🇬🇾 | GY | Guyana | 12 | 50% | PASS |
| 124 | 🇭🇳 | HN | Honduras | 12 | 50% | PASS |
| 125 | 🇭🇺 | HU | Hungary | 12 | 50% | PASS |
| 126 | 🇮🇩 | ID | Indonesia | 12 | 50% | PASS |
| 127 | 🇮🇲 | IM | Isle of Man | 12 | 50% | PASS |
| 128 | 🇮🇶 | IQ | Iraq | 12 | 50% | PASS |
| 129 | 🇮🇷 | IR | Iran | 12 | 50% | PASS |
| 130 | 🇯🇲 | JM | Jamaica | 12 | 50% | PASS |
| 131 | 🇯🇴 | JO | Jordan | 12 | 50% | PASS |
| 132 | 🇰🇪 | KE | Kenya | 12 | 50% | PASS |
| 133 | 🇰🇬 | KG | Kyrgyzstan | 12 | 50% | PASS |
| 134 | 🇰🇲 | KM | Comoros | 12 | 50% | PASS |
| 135 | 🇰🇳 | KN | Saint Kitts and Nevis | 12 | 50% | PASS |
| 136 | 🇰🇾 | KY | Cayman Islands | 12 | 50% | PASS |
| 137 | 🇰🇿 | KZ | Kazakhstan | 12 | 50% | PASS |
| 138 | 🇱🇧 | LB | Lebanon | 12 | 50% | PASS |
| 139 | 🇱🇰 | LK | Sri Lanka | 12 | 50% | PASS |
| 140 | 🇱🇸 | LS | Lesotho | 12 | 50% | PASS |
| 141 | 🇱🇺 | LU | Luxembourg | 12 | 50% | PASS |
| 142 | 🇱🇻 | LV | Latvia | 12 | 50% | PASS |
| 143 | 🇱🇾 | LY | Libya | 12 | 50% | PASS |
| 144 | 🇲🇦 | MA | Morocco | 12 | 50% | PASS |
| 145 | 🇲🇨 | MC | Monaco | 12 | 50% | PASS |
| 146 | 🇲🇩 | MD | Moldova | 12 | 50% | PASS |
| 147 | 🇲🇪 | ME | Montenegro | 12 | 50% | PASS |
| 148 | 🇲🇫 | MF | Saint Martin | 12 | 50% | PASS |
| 149 | 🇲🇬 | MG | Madagascar | 12 | 50% | PASS |
| 150 | 🇲🇭 | MH | Marshall Islands | 12 | 50% | PASS |
| 151 | 🇲🇰 | MK | North Macedonia | 12 | 50% | PASS |
| 152 | 🇲🇳 | MN | Mongolia | 12 | 50% | PASS |
| 153 | 🇲🇷 | MR | Mauritania | 12 | 50% | PASS |
| 154 | 🇲🇸 | MS | Montserrat | 12 | 50% | PASS |
| 155 | 🇲🇹 | MT | Malta | 12 | 50% | PASS |
| 156 | 🇲🇻 | MV | Maldives | 12 | 50% | PASS |
| 157 | 🇲🇿 | MZ | Mozambique | 12 | 50% | PASS |
| 158 | 🇳🇦 | NA | Namibia | 12 | 50% | PASS |
| 159 | 🇳🇪 | NE | Niger | 12 | 50% | PASS |
| 160 | 🇳🇱 | NL | Netherlands | 12 | 50% | PASS |
| 161 | 🇳🇷 | NR | Nauru | 12 | 50% | PASS |
| 162 | 🇳🇺 | NU | Niue | 12 | 50% | PASS |
| 163 | 🇵🇦 | PA | Panama | 12 | 50% | PASS |
| 164 | 🇵🇫 | PF | French Polynesia | 12 | 50% | PASS |
| 165 | 🇵🇬 | PG | Papua New Guinea | 12 | 50% | PASS |
| 166 | 🇵🇭 | PH | Philippines | 12 | 50% | PASS |
| 167 | 🇵🇲 | PM | Saint Pierre and Miquelon | 12 | 50% | PASS |
| 168 | 🇵🇷 | PR | Puerto Rico | 12 | 50% | PASS |
| 169 | 🇵🇾 | PY | Paraguay | 12 | 50% | PASS |
| 170 | 🇷🇴 | RO | Romania | 12 | 50% | PASS |
| 171 | 🇷🇸 | RS | Serbia | 12 | 50% | PASS |
| 172 | 🇷🇺 | RU | Russia | 12 | 50% | PASS |
| 173 | 🇷🇼 | RW | Rwanda | 12 | 50% | PASS |
| 174 | 🇸🇧 | SB | Solomon Islands | 12 | 50% | PASS |
| 175 | 🇸🇨 | SC | Seychelles | 12 | 50% | PASS |
| 176 | 🇸🇩 | SD | Sudan | 12 | 50% | PASS |
| 177 | 🇸🇪 | SE | Sweden | 12 | 50% | PASS |
| 178 | 🇸🇭 | SH | Saint Helena | 12 | 50% | PASS |
| 179 | 🇸🇮 | SI | Slovenia | 12 | 50% | PASS |
| 180 | 🇸🇰 | SK | Slovakia | 12 | 50% | PASS |
| 181 | 🇸🇱 | SL | Sierra Leone | 12 | 50% | PASS |
| 182 | 🇸🇲 | SM | San Marino | 12 | 50% | PASS |
| 183 | 🇸🇳 | SN | Senegal | 12 | 50% | PASS |
| 184 | 🇸🇴 | SO | Somalia | 12 | 50% | PASS |
| 185 | 🇸🇷 | SR | Suriname | 12 | 50% | PASS |
| 186 | 🇸🇸 | SS | South Sudan | 12 | 50% | PASS |
| 187 | 🇸🇻 | SV | El Salvador | 12 | 50% | PASS |
| 188 | 🇸🇽 | SX | Sint Maarten | 12 | 50% | PASS |
| 189 | 🇸🇾 | SY | Syria | 12 | 50% | PASS |
| 190 | 🇸🇿 | SZ | Eswatini | 12 | 50% | PASS |
| 191 | 🇹🇨 | TC | Turks and Caicos Islands | 12 | 50% | PASS |
| 192 | 🇹🇩 | TD | Chad | 12 | 50% | PASS |
| 193 | 🇹🇭 | TH | Thailand | 12 | 50% | PASS |
| 194 | 🇹🇯 | TJ | Tajikistan | 12 | 50% | PASS |
| 195 | 🇹🇴 | TO | Tonga | 12 | 50% | PASS |
| 196 | 🇹🇷 | TR | Turkey | 12 | 50% | PASS |
| 197 | 🇹🇹 | TT | Trinidad and Tobago | 12 | 50% | PASS |
| 198 | 🇹🇻 | TV | Tuvalu | 12 | 50% | PASS |
| 199 | 🇹🇿 | TZ | Tanzania | 12 | 50% | PASS |
| 200 | 🇺🇬 | UG | Uganda | 12 | 50% | PASS |
| 201 | 🇻🇨 | VC | Saint Vincent and the Grenadines | 12 | 50% | PASS |
| 202 | 🇻🇪 | VE | Venezuela | 12 | 50% | PASS |
| 203 | 🇻🇬 | VG | British Virgin Islands | 12 | 50% | PASS |
| 204 | 🇻🇺 | VU | Vanuatu | 12 | 50% | PASS |
| 205 | 🇼🇫 | WF | Wallis and Futuna | 12 | 50% | PASS |
| 206 | 🇼🇸 | WS | Samoa | 12 | 50% | PASS |
| 207 | 🇽🇰 | XK | Kosovo | 12 | 50% | PASS |
| 208 | 🇿🇼 | ZW | Zimbabwe | 12 | 50% | PASS |
| 209 | 🇧🇲 | BM | Bermuda | 12 | 45% | FAIL |
| 210 | 🇪🇹 | ET | Ethiopia | 12 | 45% | FAIL |
| 211 | 🇬🇹 | GT | Guatemala | 12 | 45% | FAIL |
| 212 | 🇻🇮 | VI | U.S. Virgin Islands | 12 | 45% | FAIL |
| 213 | 🇧🇬 | BG | Bulgaria | 12 | 42% | PASS |
| 214 | 🇧🇷 | BR | Brazil | 12 | 42% | PASS |
| 215 | 🇨🇦 | CA | Canada | 12 | 42% | PASS |
| 216 | 🇨🇱 | CL | Chile | 12 | 42% | PASS |
| 217 | 🇨🇼 | CW | Curaçao | 12 | 42% | PASS |
| 218 | 🇭🇷 | HR | Croatia | 12 | 42% | PASS |
| 219 | 🇲🇲 | MM | Myanmar | 12 | 42% | PASS |
| 220 | 🇲🇴 | MO | Macao | 12 | 42% | PASS |
| 221 | 🇲🇺 | MU | Mauritius | 12 | 42% | PASS |
| 222 | 🇲🇼 | MW | Malawi | 12 | 42% | PASS |
| 223 | 🇳🇿 | NZ | New Zealand | 12 | 42% | PASS |
| 224 | 🇵🇹 | PT | Portugal | 12 | 42% | PASS |
| 225 | 🇸🇬 | SG | Singapore | 12 | 42% | PASS |
| 226 | 🇹🇱 | TL | Timor-Leste | 12 | 42% | PASS |
| 227 | 🇺🇦 | UA | Ukraine | 12 | 42% | PASS |

Distribution: 5 packs ≥75%, 222 packs within the 33–67% chance band, 0 packs ≤25%.

## Iteration log

(no iteration log found)

## Interpretation

The aggregate score of **52.6%** against a 50% chance baseline is the finding. These are bibliographic claims about real, recently collected official legal documents (titles, dates, publishing sources, identifiers) across 227 jurisdictions. A score near chance means the model cannot verify citations from these jurisdictions from parametric memory: it does not know which decisions, gazettes and acts exist, so it cannot tell a real citation from a controlled fabrication. **Retrieval grounding against the actual source corpus is therefore mandatory** for any citation-reliability claim — this is precisely the gap the S3 retrieval extension (Sabaio L3) is built to close.

Where scores rise well above chance, inspection shows it is mostly the FALSE mutations being caught on internal-consistency grounds (e.g. a cross-jurisdiction `wrong-source` trap pairing a Dutch ECLI with a Gibraltar gazette is detectable without knowing the document), not genuine knowledge of the documents. TRUE items — which require actually knowing the document exists — hover near or below chance for most jurisdictions, and recent documents (2025–26 sample snapshot) sit past the model's training cutoff by construction.
