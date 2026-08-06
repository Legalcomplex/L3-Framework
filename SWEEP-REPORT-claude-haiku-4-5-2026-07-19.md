# S3 World Benchmark — Sweep Report

Generated 2026-07-19 08:06Z by `run_world_sweep.py` + `make_sweep_report.py`.

## Run setup

- **Model:** `claude-haiku-4-5` via `anthropic` (thinking disabled, temperature at provider default (not accepted on these models), 1 round per item, no retrieval and no web access)
- **Packs:** 224/227 passed (pass = zero unresolved API errors and 100% of items parsed or documented blocked; accuracy is NOT a pass criterion)
- **Items:** 2716 run, 2712 parsed, 0 blocked
- **Sampling:** full packs (all items)
- **Tokens:** 255,946 in / 128,003 out across 2,716 calls
- **Estimated cost:** $0.90 (at $1.0/M input, $5.0/M output)
- **Wall time:** 923s

Prompt construction and True/False parsing mirror `run_s3_claude.py` exactly (same placeholder fill, same first-`\b(true|false)\b` extraction), so numbers are comparable to prior S3 runs.

## Aggregate results

- **Aggregate accuracy: 52.3%** (1419/2712) — chance is 50%.
- **TRUE items:** 6.6% correct (1355 items)
- **FALSE items:** 98.0% correct (1357 items)
- **Model said "True"** on 4.3% of all judged items.

**Asymmetry: the model over-denies.** It rejects fabricated citations more readily than it confirms real ones (FALSE-recall 98.0% vs TRUE-recall 6.6%). This is skepticism without knowledge: it doubts everything, including real documents, rather than knowing which citations exist.

## Accuracy by mutation class (FALSE items)

| Mutation | n | Accuracy (caught) |
|---|---|---|
| wrong-source | 718 | 100.0% |
| id-mutation | 233 | 98.7% |
| date-shift | 406 | 94.1% |

## Accuracy by statement shape

| Shape | n | Accuracy |
|---|---|---|
| S1-published-via | 1533 | 51.7% |
| S2-decision | 798 | 48.7% |
| S3-identifier | 381 | 62.2% |

## Per-jurisdiction accuracy (best → worst)

| # | Flag | CC | Jurisdiction | Items | Accuracy | Pass |
|---|---|---|---|---|---|---|
| 1 | 🇦🇲 | AM | Armenia | 12 | 75% | PASS |
| 2 | 🇰🇲 | KM | Comoros | 12 | 75% | PASS |
| 3 | 🇹🇩 | TD | Chad | 12 | 75% | PASS |
| 4 | 🇺🇾 | UY | Uruguay | 12 | 75% | PASS |
| 5 | 🇽🇰 | XK | Kosovo | 12 | 75% | PASS |
| 6 | 🇧🇫 | BF | Burkina Faso | 12 | 67% | PASS |
| 7 | 🇱🇻 | LV | Latvia | 12 | 67% | PASS |
| 8 | 🇶🇦 | QA | Qatar | 12 | 67% | PASS |
| 9 | 🇸🇮 | SI | Slovenia | 12 | 67% | PASS |
| 10 | 🇹🇷 | TR | Turkey | 12 | 67% | PASS |
| 11 | 🇹🇼 | TW | Taiwan | 12 | 67% | PASS |
| 12 | 🇻🇳 | VN | Vietnam | 12 | 67% | PASS |
| 13 | 🇧🇯 | BJ | Benin | 12 | 60% | FAIL |
| 14 | 🇦🇴 | AO | Angola | 12 | 58% | PASS |
| 15 | 🇦🇼 | AW | Aruba | 12 | 58% | PASS |
| 16 | 🇦🇽 | AX | Åland Islands | 12 | 58% | PASS |
| 17 | 🇧🇴 | BO | Bolivia | 12 | 58% | PASS |
| 18 | 🇧🇿 | BZ | Belize | 12 | 58% | PASS |
| 19 | 🇨🇦 | CA | Canada | 12 | 58% | PASS |
| 20 | 🇨🇫 | CF | Central African Republic | 12 | 58% | PASS |
| 21 | 🇨🇭 | CH | Switzerland | 12 | 58% | PASS |
| 22 | 🇨🇲 | CM | Cameroon | 12 | 58% | PASS |
| 23 | 🇨🇴 | CO | Colombia | 12 | 58% | PASS |
| 24 | 🇨🇾 | CY | Cyprus | 12 | 58% | PASS |
| 25 | 🇨🇿 | CZ | Czechia | 12 | 58% | PASS |
| 26 | 🇪🇬 | EG | Egypt | 12 | 58% | PASS |
| 27 | 🇪🇸 | ES | Spain | 12 | 58% | PASS |
| 28 | 🇪🇺 | EU | European Union | 12 | 58% | PASS |
| 29 | 🇫🇮 | FI | Finland | 12 | 58% | PASS |
| 30 | 🇫🇷 | FR | France | 12 | 58% | PASS |
| 31 | 🇬🇪 | GE | Georgia | 12 | 58% | PASS |
| 32 | 🇬🇭 | GH | Ghana | 12 | 58% | PASS |
| 33 | 🇬🇳 | GN | Guinea | 12 | 58% | PASS |
| 34 | 🇬🇹 | GT | Guatemala | 12 | 58% | PASS |
| 35 | 🇭🇹 | HT | Haiti | 12 | 58% | PASS |
| 36 | 🇮🇱 | IL | Israel | 12 | 58% | PASS |
| 37 | 🇮🇶 | IQ | Iraq | 12 | 58% | PASS |
| 38 | 🇯🇵 | JP | Japan | 12 | 58% | PASS |
| 39 | 🇱🇧 | LB | Lebanon | 12 | 58% | PASS |
| 40 | 🇱🇹 | LT | Lithuania | 12 | 58% | PASS |
| 41 | 🇱🇾 | LY | Libya | 12 | 58% | PASS |
| 42 | 🇲🇪 | ME | Montenegro | 12 | 58% | PASS |
| 43 | 🇲🇭 | MH | Marshall Islands | 12 | 58% | PASS |
| 44 | 🇲🇴 | MO | Macao | 12 | 58% | PASS |
| 45 | 🇳🇱 | NL | Netherlands | 12 | 58% | PASS |
| 46 | 🇳🇴 | NO | Norway | 12 | 58% | PASS |
| 47 | 🇵🇪 | PE | Peru | 12 | 58% | PASS |
| 48 | 🇵🇰 | PK | Pakistan | 12 | 58% | PASS |
| 49 | 🇵🇱 | PL | Poland | 12 | 58% | PASS |
| 50 | 🇸🇩 | SD | Sudan | 12 | 58% | PASS |
| 51 | 🇸🇭 | SH | Saint Helena | 12 | 58% | PASS |
| 52 | 🇸🇲 | SM | San Marino | 12 | 58% | PASS |
| 53 | 🇹🇭 | TH | Thailand | 12 | 58% | PASS |
| 54 | 🇹🇯 | TJ | Tajikistan | 12 | 58% | PASS |
| 55 | 🇹🇲 | TM | Turkmenistan | 12 | 58% | PASS |
| 56 | 🇹🇹 | TT | Trinidad and Tobago | 12 | 58% | PASS |
| 57 | 🇺🇳 | UN | United Nations | 12 | 58% | PASS |
| 58 | 🇺🇿 | UZ | Uzbekistan | 12 | 58% | PASS |
| 59 | 🇻🇦 | VA | Vatican City | 12 | 58% | PASS |
| 60 | 🇼🇸 | WS | Samoa | 12 | 58% | PASS |
| 61 | 🇦🇩 | AD | Andorra | 12 | 50% | PASS |
| 62 | 🇦🇪 | AE | United Arab Emirates | 12 | 50% | PASS |
| 63 | 🇦🇬 | AG | Antigua and Barbuda | 12 | 50% | PASS |
| 64 | 🇦🇮 | AI | Anguilla | 12 | 50% | PASS |
| 65 | 🇦🇱 | AL | Albania | 12 | 50% | PASS |
| 66 | 🇦🇷 | AR | Argentina | 12 | 50% | PASS |
| 67 | 🇦🇸 | AS | American Samoa | 6 | 50% | PASS |
| 68 | 🇦🇹 | AT | Austria | 12 | 50% | PASS |
| 69 | 🇦🇿 | AZ | Azerbaijan | 12 | 50% | PASS |
| 70 | 🇧🇧 | BB | Barbados | 12 | 50% | PASS |
| 71 | 🇧🇩 | BD | Bangladesh | 12 | 50% | PASS |
| 72 | 🇧🇪 | BE | Belgium | 12 | 50% | PASS |
| 73 | 🇧🇬 | BG | Bulgaria | 12 | 50% | PASS |
| 74 | 🇧🇭 | BH | Bahrain | 12 | 50% | PASS |
| 75 | 🇧🇮 | BI | Burundi | 12 | 50% | PASS |
| 76 | 🇧🇱 | BL | Saint Barthélemy | 12 | 50% | PASS |
| 77 | 🇧🇲 | BM | Bermuda | 12 | 50% | PASS |
| 78 | 🇧🇳 | BN | Brunei | 12 | 50% | PASS |
| 79 | 🇧🇶 | BQ | Caribbean Netherlands | 12 | 50% | PASS |
| 80 | 🇧🇷 | BR | Brazil | 12 | 50% | PASS |
| 81 | 🇧🇹 | BT | Bhutan | 12 | 50% | PASS |
| 82 | 🇧🇼 | BW | Botswana | 12 | 50% | PASS |
| 83 | 🇨🇩 | CD | Democratic Republic of the Congo | 12 | 50% | PASS |
| 84 | 🇨🇬 | CG | Republic of the Congo | 12 | 50% | PASS |
| 85 | 🇨🇮 | CI | Côte d'Ivoire | 12 | 50% | PASS |
| 86 | 🇨🇰 | CK | Cook Islands | 12 | 50% | PASS |
| 87 | 🇨🇱 | CL | Chile | 12 | 50% | PASS |
| 88 | 🏰 | COE | Council of Europe | 12 | 50% | PASS |
| 89 | 🇨🇷 | CR | Costa Rica | 12 | 50% | PASS |
| 90 | 🇨🇺 | CU | Cuba | 12 | 50% | PASS |
| 91 | 🇨🇻 | CV | Cape Verde | 12 | 50% | PASS |
| 92 | 🇨🇼 | CW | Curaçao | 12 | 50% | PASS |
| 93 | 🇩🇪 | DE | Germany | 12 | 50% | PASS |
| 94 | 🇩🇯 | DJ | Djibouti | 12 | 50% | PASS |
| 95 | 🇩🇰 | DK | Denmark | 12 | 50% | PASS |
| 96 | 🇩🇲 | DM | Dominica | 12 | 50% | PASS |
| 97 | 🇩🇴 | DO | Dominican Republic | 12 | 50% | PASS |
| 98 | 🇩🇿 | DZ | Algeria | 12 | 50% | PASS |
| 99 | 🇪🇨 | EC | Ecuador | 12 | 50% | PASS |
| 100 | 🇪🇪 | EE | Estonia | 12 | 50% | PASS |
| 101 | 🇪🇷 | ER | Eritrea | 12 | 50% | PASS |
| 102 | 🇪🇹 | ET | Ethiopia | 12 | 50% | PASS |
| 103 | 🇫🇯 | FJ | Fiji | 12 | 50% | PASS |
| 104 | 🇫🇰 | FK | Falkland Islands | 12 | 50% | PASS |
| 105 | 🇫🇲 | FM | Micronesia | 10 | 50% | PASS |
| 106 | 🇫🇴 | FO | Faroe Islands | 12 | 50% | PASS |
| 107 | 🇬🇦 | GA | Gabon | 12 | 50% | PASS |
| 108 | 🇬🇩 | GD | Grenada | 12 | 50% | PASS |
| 109 | 🇬🇬 | GG | Guernsey | 12 | 50% | PASS |
| 110 | 🇬🇮 | GI | Gibraltar | 12 | 50% | PASS |
| 111 | 🇬🇱 | GL | Greenland | 12 | 50% | PASS |
| 112 | 🇬🇲 | GM | Gambia | 12 | 50% | PASS |
| 113 | 🇬🇶 | GQ | Equatorial Guinea | 12 | 50% | PASS |
| 114 | 🇬🇷 | GR | Greece | 12 | 50% | PASS |
| 115 | 🇬🇼 | GW | Guinea-Bissau | 12 | 50% | PASS |
| 116 | 🇬🇾 | GY | Guyana | 12 | 50% | PASS |
| 117 | 🇭🇰 | HK | Hong Kong | 12 | 50% | PASS |
| 118 | 🇭🇳 | HN | Honduras | 12 | 50% | PASS |
| 119 | 🇭🇺 | HU | Hungary | 12 | 50% | PASS |
| 120 | 🇮🇩 | ID | Indonesia | 12 | 50% | PASS |
| 121 | 🇮🇪 | IE | Ireland | 12 | 50% | PASS |
| 122 | 🇮🇲 | IM | Isle of Man | 12 | 50% | PASS |
| 123 | 🇮🇳 | IN | India | 12 | 50% | PASS |
| 124 | 🇮🇷 | IR | Iran | 12 | 50% | PASS |
| 125 | 🇮🇸 | IS | Iceland | 12 | 50% | PASS |
| 126 | 🇮🇹 | IT | Italy | 12 | 50% | PASS |
| 127 | 🇯🇪 | JE | Jersey | 12 | 50% | PASS |
| 128 | 🇯🇲 | JM | Jamaica | 12 | 50% | PASS |
| 129 | 🇰🇪 | KE | Kenya | 12 | 50% | PASS |
| 130 | 🇰🇬 | KG | Kyrgyzstan | 12 | 50% | PASS |
| 131 | 🇰🇭 | KH | Cambodia | 12 | 50% | PASS |
| 132 | 🇰🇮 | KI | Kiribati | 12 | 50% | PASS |
| 133 | 🇰🇳 | KN | Saint Kitts and Nevis | 12 | 50% | PASS |
| 134 | 🇰🇷 | KR | South Korea | 12 | 50% | PASS |
| 135 | 🇰🇾 | KY | Cayman Islands | 12 | 50% | PASS |
| 136 | 🇰🇿 | KZ | Kazakhstan | 12 | 50% | PASS |
| 137 | 🇱🇦 | LA | Laos | 12 | 50% | PASS |
| 138 | 🇱🇨 | LC | Saint Lucia | 12 | 50% | PASS |
| 139 | 🇱🇰 | LK | Sri Lanka | 12 | 50% | PASS |
| 140 | 🇱🇷 | LR | Liberia | 12 | 50% | PASS |
| 141 | 🇱🇸 | LS | Lesotho | 12 | 50% | PASS |
| 142 | 🇱🇺 | LU | Luxembourg | 12 | 50% | PASS |
| 143 | 🇲🇦 | MA | Morocco | 12 | 50% | PASS |
| 144 | 🇲🇨 | MC | Monaco | 12 | 50% | PASS |
| 145 | 🇲🇩 | MD | Moldova | 12 | 50% | PASS |
| 146 | 🇲🇫 | MF | Saint Martin | 12 | 50% | PASS |
| 147 | 🇲🇬 | MG | Madagascar | 12 | 50% | PASS |
| 148 | 🇲🇰 | MK | North Macedonia | 12 | 50% | PASS |
| 149 | 🇲🇱 | ML | Mali | 12 | 50% | PASS |
| 150 | 🇲🇲 | MM | Myanmar | 12 | 50% | PASS |
| 151 | 🇲🇳 | MN | Mongolia | 12 | 50% | PASS |
| 152 | 🇲🇷 | MR | Mauritania | 12 | 50% | PASS |
| 153 | 🇲🇸 | MS | Montserrat | 12 | 50% | PASS |
| 154 | 🇲🇹 | MT | Malta | 12 | 50% | PASS |
| 155 | 🇲🇺 | MU | Mauritius | 12 | 50% | PASS |
| 156 | 🇲🇻 | MV | Maldives | 12 | 50% | PASS |
| 157 | 🇲🇼 | MW | Malawi | 12 | 50% | PASS |
| 158 | 🇲🇽 | MX | Mexico | 12 | 50% | PASS |
| 159 | 🇲🇿 | MZ | Mozambique | 12 | 50% | PASS |
| 160 | 🇳🇦 | NA | Namibia | 12 | 50% | PASS |
| 161 | 🇳🇪 | NE | Niger | 12 | 50% | PASS |
| 162 | 🇳🇬 | NG | Nigeria | 12 | 50% | PASS |
| 163 | 🇳🇮 | NI | Nicaragua | 12 | 50% | PASS |
| 164 | 🇳🇷 | NR | Nauru | 12 | 50% | PASS |
| 165 | 🇳🇺 | NU | Niue | 12 | 50% | PASS |
| 166 | 🇴🇲 | OM | Oman | 12 | 50% | PASS |
| 167 | 🇵🇦 | PA | Panama | 12 | 50% | PASS |
| 168 | 🇵🇫 | PF | French Polynesia | 12 | 50% | PASS |
| 169 | 🇵🇬 | PG | Papua New Guinea | 12 | 50% | PASS |
| 170 | 🇵🇭 | PH | Philippines | 12 | 50% | PASS |
| 171 | 🇵🇲 | PM | Saint Pierre and Miquelon | 12 | 50% | PASS |
| 172 | 🇵🇳 | PN | Pitcairn Islands | 12 | 50% | PASS |
| 173 | 🇵🇷 | PR | Puerto Rico | 12 | 50% | PASS |
| 174 | 🇵🇸 | PS | Palestine | 12 | 50% | PASS |
| 175 | 🇵🇹 | PT | Portugal | 12 | 50% | PASS |
| 176 | 🇵🇼 | PW | Palau | 12 | 50% | PASS |
| 177 | 🇷🇴 | RO | Romania | 12 | 50% | PASS |
| 178 | 🇷🇺 | RU | Russia | 12 | 50% | PASS |
| 179 | 🇷🇼 | RW | Rwanda | 12 | 50% | PASS |
| 180 | 🇸🇦 | SA | Saudi Arabia | 12 | 50% | PASS |
| 181 | 🇸🇧 | SB | Solomon Islands | 12 | 50% | PASS |
| 182 | 🇸🇨 | SC | Seychelles | 12 | 50% | PASS |
| 183 | 🇸🇪 | SE | Sweden | 12 | 50% | PASS |
| 184 | 🇸🇬 | SG | Singapore | 12 | 50% | PASS |
| 185 | 🇸🇰 | SK | Slovakia | 12 | 50% | PASS |
| 186 | 🇸🇱 | SL | Sierra Leone | 12 | 50% | PASS |
| 187 | 🇸🇴 | SO | Somalia | 12 | 50% | PASS |
| 188 | 🇸🇷 | SR | Suriname | 12 | 50% | PASS |
| 189 | 🇸🇸 | SS | South Sudan | 12 | 50% | PASS |
| 190 | 🇸🇻 | SV | El Salvador | 12 | 50% | PASS |
| 191 | 🇸🇽 | SX | Sint Maarten | 12 | 50% | PASS |
| 192 | 🇸🇾 | SY | Syria | 12 | 50% | PASS |
| 193 | 🇸🇿 | SZ | Eswatini | 12 | 50% | PASS |
| 194 | 🇹🇨 | TC | Turks and Caicos Islands | 12 | 50% | PASS |
| 195 | 🇹🇬 | TG | Togo | 12 | 50% | PASS |
| 196 | 🇹🇱 | TL | Timor-Leste | 12 | 50% | PASS |
| 197 | 🇹🇳 | TN | Tunisia | 12 | 50% | PASS |
| 198 | 🇹🇴 | TO | Tonga | 12 | 50% | PASS |
| 199 | 🇹🇻 | TV | Tuvalu | 12 | 50% | PASS |
| 200 | 🇺🇬 | UG | Uganda | 12 | 50% | PASS |
| 201 | 🇬🇧 | UK | United Kingdom | 12 | 50% | PASS |
| 202 | 🇺🇸 | US | United States | 12 | 50% | PASS |
| 203 | 🇻🇨 | VC | Saint Vincent and the Grenadines | 12 | 50% | PASS |
| 204 | 🇻🇪 | VE | Venezuela | 12 | 50% | PASS |
| 205 | 🇻🇬 | VG | British Virgin Islands | 12 | 50% | PASS |
| 206 | 🇻🇮 | VI | U.S. Virgin Islands | 12 | 50% | PASS |
| 207 | 🇻🇺 | VU | Vanuatu | 12 | 50% | PASS |
| 208 | 🇼🇫 | WF | Wallis and Futuna | 12 | 50% | PASS |
| 209 | 🇾🇪 | YE | Yemen | 12 | 50% | PASS |
| 210 | 🇿🇦 | ZA | South Africa | 12 | 50% | PASS |
| 211 | 🇿🇲 | ZM | Zambia | 12 | 50% | PASS |
| 212 | 🇿🇼 | ZW | Zimbabwe | 12 | 50% | PASS |
| 213 | 🇧🇸 | BS | Bahamas | 12 | 45% | FAIL |
| 214 | 🇵🇾 | PY | Paraguay | 12 | 45% | FAIL |
| 215 | 🇦🇺 | AU | Australia | 12 | 42% | PASS |
| 216 | 🇧🇦 | BA | Bosnia & Herzegovina | 12 | 42% | PASS |
| 217 | 🇨🇳 | CN | China | 12 | 42% | PASS |
| 218 | 🇬🇺 | GU | Guam | 12 | 42% | PASS |
| 219 | 🇭🇷 | HR | Croatia | 12 | 42% | PASS |
| 220 |  | INTL | International | 12 | 42% | PASS |
| 221 | 🇯🇴 | JO | Jordan | 12 | 42% | PASS |
| 222 | 🇱🇮 | LI | Liechtenstein | 12 | 42% | PASS |
| 223 | 🇳🇿 | NZ | New Zealand | 12 | 42% | PASS |
| 224 | 🇷🇸 | RS | Serbia | 12 | 42% | PASS |
| 225 | 🇸🇳 | SN | Senegal | 12 | 42% | PASS |
| 226 | 🇹🇿 | TZ | Tanzania | 12 | 42% | PASS |
| 227 | 🇺🇦 | UA | Ukraine | 12 | 42% | PASS |

Distribution: 5 packs ≥75%, 222 packs within the 33–67% chance band, 0 packs ≤25%.

## Iteration log

(no iteration log found)

## Interpretation

The aggregate score of **52.3%** against a 50% chance baseline is the finding. These are bibliographic claims about real, recently collected official legal documents (titles, dates, publishing sources, identifiers) across 227 jurisdictions. A score near chance means the model cannot verify citations from these jurisdictions from parametric memory: it does not know which decisions, gazettes and acts exist, so it cannot tell a real citation from a controlled fabrication. **Retrieval grounding against the actual source corpus is therefore mandatory** for any citation-reliability claim — this is precisely the gap the S3 retrieval extension (Sabaio L3) is built to close.

Where scores rise well above chance, inspection shows it is mostly the FALSE mutations being caught on internal-consistency grounds (e.g. a cross-jurisdiction `wrong-source` trap pairing a Dutch ECLI with a Gibraltar gazette is detectable without knowing the document), not genuine knowledge of the documents. TRUE items — which require actually knowing the document exists — hover near or below chance for most jurisdictions, and recent documents (2025–26 sample snapshot) sit past the model's training cutoff by construction.
