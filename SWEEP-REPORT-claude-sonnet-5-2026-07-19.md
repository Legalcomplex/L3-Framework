# S3 World Benchmark — Sweep Report

Generated 2026-07-19 08:06Z by `run_world_sweep.py` + `make_sweep_report.py`.

## Run setup

- **Model:** `claude-sonnet-5` via `anthropic` (thinking disabled, temperature at provider default (not accepted on these models), 1 round per item, no retrieval and no web access)
- **Packs:** 227/227 passed (pass = zero unresolved API errors and 100% of items parsed or documented blocked; accuracy is NOT a pass criterion)
- **Items:** 2716 run, 2716 parsed, 0 blocked
- **Sampling:** full packs (all items)
- **Tokens:** 357,203 in / 154,832 out across 2,716 calls
- **Estimated cost:** $2.26 (at $2.0/M input, $10.0/M output)
- **Wall time:** 1086s

Prompt construction and True/False parsing mirror `run_s3_claude.py` exactly (same placeholder fill, same first-`\b(true|false)\b` extraction), so numbers are comparable to prior S3 runs.

## Aggregate results

- **Aggregate accuracy: 50.5%** (1372/2716) — chance is 50%.
- **TRUE items:** 1.5% correct (1358 items)
- **FALSE items:** 99.5% correct (1358 items)
- **Model said "True"** on 1.0% of all judged items.

**Asymmetry: the model over-denies.** It rejects fabricated citations more readily than it confirms real ones (FALSE-recall 99.5% vs TRUE-recall 1.5%). This is skepticism without knowledge: it doubts everything, including real documents, rather than knowing which citations exist.

## Accuracy by mutation class (FALSE items)

| Mutation | n | Accuracy (caught) |
|---|---|---|
| wrong-source | 718 | 100.0% |
| id-mutation | 234 | 99.6% |
| date-shift | 406 | 98.5% |

## Accuracy by statement shape

| Shape | n | Accuracy |
|---|---|---|
| S1-published-via | 1536 | 49.6% |
| S2-decision | 798 | 47.0% |
| S3-identifier | 382 | 61.5% |

## Per-jurisdiction accuracy (best → worst)

| # | Flag | CC | Jurisdiction | Items | Accuracy | Pass |
|---|---|---|---|---|---|---|
| 1 | 🇻🇦 | VA | Vatican City | 12 | 75% | PASS |
| 2 | 🇭🇹 | HT | Haiti | 12 | 67% | PASS |
| 3 | 🇦🇷 | AR | Argentina | 12 | 58% | PASS |
| 4 | 🇦🇺 | AU | Australia | 12 | 58% | PASS |
| 5 | 🇧🇩 | BD | Bangladesh | 12 | 58% | PASS |
| 6 | 🇧🇶 | BQ | Caribbean Netherlands | 12 | 58% | PASS |
| 7 | 🏰 | COE | Council of Europe | 12 | 58% | PASS |
| 8 | 🇫🇷 | FR | France | 12 | 58% | PASS |
| 9 | 🇬🇭 | GH | Ghana | 12 | 58% | PASS |
| 10 |  | INTL | International | 12 | 58% | PASS |
| 11 | 🇯🇵 | JP | Japan | 12 | 58% | PASS |
| 12 | 🇸🇦 | SA | Saudi Arabia | 12 | 58% | PASS |
| 13 | 🇺🇳 | UN | United Nations | 12 | 58% | PASS |
| 14 | 🇻🇳 | VN | Vietnam | 12 | 58% | PASS |
| 15 | 🇦🇩 | AD | Andorra | 12 | 50% | PASS |
| 16 | 🇦🇪 | AE | United Arab Emirates | 12 | 50% | PASS |
| 17 | 🇦🇬 | AG | Antigua and Barbuda | 12 | 50% | PASS |
| 18 | 🇦🇮 | AI | Anguilla | 12 | 50% | PASS |
| 19 | 🇦🇱 | AL | Albania | 12 | 50% | PASS |
| 20 | 🇦🇲 | AM | Armenia | 12 | 50% | PASS |
| 21 | 🇦🇴 | AO | Angola | 12 | 50% | PASS |
| 22 | 🇦🇸 | AS | American Samoa | 6 | 50% | PASS |
| 23 | 🇦🇹 | AT | Austria | 12 | 50% | PASS |
| 24 | 🇦🇼 | AW | Aruba | 12 | 50% | PASS |
| 25 | 🇦🇽 | AX | Åland Islands | 12 | 50% | PASS |
| 26 | 🇦🇿 | AZ | Azerbaijan | 12 | 50% | PASS |
| 27 | 🇧🇦 | BA | Bosnia & Herzegovina | 12 | 50% | PASS |
| 28 | 🇧🇧 | BB | Barbados | 12 | 50% | PASS |
| 29 | 🇧🇪 | BE | Belgium | 12 | 50% | PASS |
| 30 | 🇧🇫 | BF | Burkina Faso | 12 | 50% | PASS |
| 31 | 🇧🇬 | BG | Bulgaria | 12 | 50% | PASS |
| 32 | 🇧🇭 | BH | Bahrain | 12 | 50% | PASS |
| 33 | 🇧🇮 | BI | Burundi | 12 | 50% | PASS |
| 34 | 🇧🇯 | BJ | Benin | 12 | 50% | PASS |
| 35 | 🇧🇱 | BL | Saint Barthélemy | 12 | 50% | PASS |
| 36 | 🇧🇲 | BM | Bermuda | 12 | 50% | PASS |
| 37 | 🇧🇳 | BN | Brunei | 12 | 50% | PASS |
| 38 | 🇧🇴 | BO | Bolivia | 12 | 50% | PASS |
| 39 | 🇧🇷 | BR | Brazil | 12 | 50% | PASS |
| 40 | 🇧🇸 | BS | Bahamas | 12 | 50% | PASS |
| 41 | 🇧🇹 | BT | Bhutan | 12 | 50% | PASS |
| 42 | 🇧🇼 | BW | Botswana | 12 | 50% | PASS |
| 43 | 🇧🇿 | BZ | Belize | 12 | 50% | PASS |
| 44 | 🇨🇦 | CA | Canada | 12 | 50% | PASS |
| 45 | 🇨🇩 | CD | Democratic Republic of the Congo | 12 | 50% | PASS |
| 46 | 🇨🇫 | CF | Central African Republic | 12 | 50% | PASS |
| 47 | 🇨🇬 | CG | Republic of the Congo | 12 | 50% | PASS |
| 48 | 🇨🇭 | CH | Switzerland | 12 | 50% | PASS |
| 49 | 🇨🇮 | CI | Côte d'Ivoire | 12 | 50% | PASS |
| 50 | 🇨🇰 | CK | Cook Islands | 12 | 50% | PASS |
| 51 | 🇨🇱 | CL | Chile | 12 | 50% | PASS |
| 52 | 🇨🇲 | CM | Cameroon | 12 | 50% | PASS |
| 53 | 🇨🇳 | CN | China | 12 | 50% | PASS |
| 54 | 🇨🇴 | CO | Colombia | 12 | 50% | PASS |
| 55 | 🇨🇷 | CR | Costa Rica | 12 | 50% | PASS |
| 56 | 🇨🇺 | CU | Cuba | 12 | 50% | PASS |
| 57 | 🇨🇻 | CV | Cape Verde | 12 | 50% | PASS |
| 58 | 🇨🇼 | CW | Curaçao | 12 | 50% | PASS |
| 59 | 🇨🇾 | CY | Cyprus | 12 | 50% | PASS |
| 60 | 🇨🇿 | CZ | Czechia | 12 | 50% | PASS |
| 61 | 🇩🇯 | DJ | Djibouti | 12 | 50% | PASS |
| 62 | 🇩🇰 | DK | Denmark | 12 | 50% | PASS |
| 63 | 🇩🇲 | DM | Dominica | 12 | 50% | PASS |
| 64 | 🇩🇴 | DO | Dominican Republic | 12 | 50% | PASS |
| 65 | 🇩🇿 | DZ | Algeria | 12 | 50% | PASS |
| 66 | 🇪🇨 | EC | Ecuador | 12 | 50% | PASS |
| 67 | 🇪🇪 | EE | Estonia | 12 | 50% | PASS |
| 68 | 🇪🇬 | EG | Egypt | 12 | 50% | PASS |
| 69 | 🇪🇷 | ER | Eritrea | 12 | 50% | PASS |
| 70 | 🇪🇸 | ES | Spain | 12 | 50% | PASS |
| 71 | 🇪🇹 | ET | Ethiopia | 12 | 50% | PASS |
| 72 | 🇪🇺 | EU | European Union | 12 | 50% | PASS |
| 73 | 🇫🇮 | FI | Finland | 12 | 50% | PASS |
| 74 | 🇫🇯 | FJ | Fiji | 12 | 50% | PASS |
| 75 | 🇫🇰 | FK | Falkland Islands | 12 | 50% | PASS |
| 76 | 🇫🇲 | FM | Micronesia | 10 | 50% | PASS |
| 77 | 🇫🇴 | FO | Faroe Islands | 12 | 50% | PASS |
| 78 | 🇬🇦 | GA | Gabon | 12 | 50% | PASS |
| 79 | 🇬🇩 | GD | Grenada | 12 | 50% | PASS |
| 80 | 🇬🇪 | GE | Georgia | 12 | 50% | PASS |
| 81 | 🇬🇬 | GG | Guernsey | 12 | 50% | PASS |
| 82 | 🇬🇮 | GI | Gibraltar | 12 | 50% | PASS |
| 83 | 🇬🇱 | GL | Greenland | 12 | 50% | PASS |
| 84 | 🇬🇲 | GM | Gambia | 12 | 50% | PASS |
| 85 | 🇬🇳 | GN | Guinea | 12 | 50% | PASS |
| 86 | 🇬🇶 | GQ | Equatorial Guinea | 12 | 50% | PASS |
| 87 | 🇬🇷 | GR | Greece | 12 | 50% | PASS |
| 88 | 🇬🇹 | GT | Guatemala | 12 | 50% | PASS |
| 89 | 🇬🇺 | GU | Guam | 12 | 50% | PASS |
| 90 | 🇬🇼 | GW | Guinea-Bissau | 12 | 50% | PASS |
| 91 | 🇬🇾 | GY | Guyana | 12 | 50% | PASS |
| 92 | 🇭🇰 | HK | Hong Kong | 12 | 50% | PASS |
| 93 | 🇭🇳 | HN | Honduras | 12 | 50% | PASS |
| 94 | 🇭🇷 | HR | Croatia | 12 | 50% | PASS |
| 95 | 🇭🇺 | HU | Hungary | 12 | 50% | PASS |
| 96 | 🇮🇩 | ID | Indonesia | 12 | 50% | PASS |
| 97 | 🇮🇪 | IE | Ireland | 12 | 50% | PASS |
| 98 | 🇮🇱 | IL | Israel | 12 | 50% | PASS |
| 99 | 🇮🇲 | IM | Isle of Man | 12 | 50% | PASS |
| 100 | 🇮🇳 | IN | India | 12 | 50% | PASS |
| 101 | 🇮🇶 | IQ | Iraq | 12 | 50% | PASS |
| 102 | 🇮🇷 | IR | Iran | 12 | 50% | PASS |
| 103 | 🇮🇸 | IS | Iceland | 12 | 50% | PASS |
| 104 | 🇮🇹 | IT | Italy | 12 | 50% | PASS |
| 105 | 🇯🇪 | JE | Jersey | 12 | 50% | PASS |
| 106 | 🇯🇲 | JM | Jamaica | 12 | 50% | PASS |
| 107 | 🇯🇴 | JO | Jordan | 12 | 50% | PASS |
| 108 | 🇰🇪 | KE | Kenya | 12 | 50% | PASS |
| 109 | 🇰🇬 | KG | Kyrgyzstan | 12 | 50% | PASS |
| 110 | 🇰🇭 | KH | Cambodia | 12 | 50% | PASS |
| 111 | 🇰🇮 | KI | Kiribati | 12 | 50% | PASS |
| 112 | 🇰🇲 | KM | Comoros | 12 | 50% | PASS |
| 113 | 🇰🇳 | KN | Saint Kitts and Nevis | 12 | 50% | PASS |
| 114 | 🇰🇷 | KR | South Korea | 12 | 50% | PASS |
| 115 | 🇰🇾 | KY | Cayman Islands | 12 | 50% | PASS |
| 116 | 🇰🇿 | KZ | Kazakhstan | 12 | 50% | PASS |
| 117 | 🇱🇦 | LA | Laos | 12 | 50% | PASS |
| 118 | 🇱🇧 | LB | Lebanon | 12 | 50% | PASS |
| 119 | 🇱🇨 | LC | Saint Lucia | 12 | 50% | PASS |
| 120 | 🇱🇮 | LI | Liechtenstein | 12 | 50% | PASS |
| 121 | 🇱🇰 | LK | Sri Lanka | 12 | 50% | PASS |
| 122 | 🇱🇷 | LR | Liberia | 12 | 50% | PASS |
| 123 | 🇱🇸 | LS | Lesotho | 12 | 50% | PASS |
| 124 | 🇱🇹 | LT | Lithuania | 12 | 50% | PASS |
| 125 | 🇱🇺 | LU | Luxembourg | 12 | 50% | PASS |
| 126 | 🇱🇻 | LV | Latvia | 12 | 50% | PASS |
| 127 | 🇱🇾 | LY | Libya | 12 | 50% | PASS |
| 128 | 🇲🇦 | MA | Morocco | 12 | 50% | PASS |
| 129 | 🇲🇨 | MC | Monaco | 12 | 50% | PASS |
| 130 | 🇲🇩 | MD | Moldova | 12 | 50% | PASS |
| 131 | 🇲🇪 | ME | Montenegro | 12 | 50% | PASS |
| 132 | 🇲🇫 | MF | Saint Martin | 12 | 50% | PASS |
| 133 | 🇲🇬 | MG | Madagascar | 12 | 50% | PASS |
| 134 | 🇲🇭 | MH | Marshall Islands | 12 | 50% | PASS |
| 135 | 🇲🇰 | MK | North Macedonia | 12 | 50% | PASS |
| 136 | 🇲🇱 | ML | Mali | 12 | 50% | PASS |
| 137 | 🇲🇲 | MM | Myanmar | 12 | 50% | PASS |
| 138 | 🇲🇳 | MN | Mongolia | 12 | 50% | PASS |
| 139 | 🇲🇴 | MO | Macao | 12 | 50% | PASS |
| 140 | 🇲🇷 | MR | Mauritania | 12 | 50% | PASS |
| 141 | 🇲🇸 | MS | Montserrat | 12 | 50% | PASS |
| 142 | 🇲🇹 | MT | Malta | 12 | 50% | PASS |
| 143 | 🇲🇺 | MU | Mauritius | 12 | 50% | PASS |
| 144 | 🇲🇻 | MV | Maldives | 12 | 50% | PASS |
| 145 | 🇲🇼 | MW | Malawi | 12 | 50% | PASS |
| 146 | 🇲🇽 | MX | Mexico | 12 | 50% | PASS |
| 147 | 🇲🇿 | MZ | Mozambique | 12 | 50% | PASS |
| 148 | 🇳🇦 | NA | Namibia | 12 | 50% | PASS |
| 149 | 🇳🇪 | NE | Niger | 12 | 50% | PASS |
| 150 | 🇳🇬 | NG | Nigeria | 12 | 50% | PASS |
| 151 | 🇳🇮 | NI | Nicaragua | 12 | 50% | PASS |
| 152 | 🇳🇱 | NL | Netherlands | 12 | 50% | PASS |
| 153 | 🇳🇴 | NO | Norway | 12 | 50% | PASS |
| 154 | 🇳🇷 | NR | Nauru | 12 | 50% | PASS |
| 155 | 🇳🇺 | NU | Niue | 12 | 50% | PASS |
| 156 | 🇳🇿 | NZ | New Zealand | 12 | 50% | PASS |
| 157 | 🇴🇲 | OM | Oman | 12 | 50% | PASS |
| 158 | 🇵🇦 | PA | Panama | 12 | 50% | PASS |
| 159 | 🇵🇪 | PE | Peru | 12 | 50% | PASS |
| 160 | 🇵🇫 | PF | French Polynesia | 12 | 50% | PASS |
| 161 | 🇵🇬 | PG | Papua New Guinea | 12 | 50% | PASS |
| 162 | 🇵🇭 | PH | Philippines | 12 | 50% | PASS |
| 163 | 🇵🇰 | PK | Pakistan | 12 | 50% | PASS |
| 164 | 🇵🇱 | PL | Poland | 12 | 50% | PASS |
| 165 | 🇵🇲 | PM | Saint Pierre and Miquelon | 12 | 50% | PASS |
| 166 | 🇵🇳 | PN | Pitcairn Islands | 12 | 50% | PASS |
| 167 | 🇵🇷 | PR | Puerto Rico | 12 | 50% | PASS |
| 168 | 🇵🇸 | PS | Palestine | 12 | 50% | PASS |
| 169 | 🇵🇹 | PT | Portugal | 12 | 50% | PASS |
| 170 | 🇵🇼 | PW | Palau | 12 | 50% | PASS |
| 171 | 🇵🇾 | PY | Paraguay | 12 | 50% | PASS |
| 172 | 🇶🇦 | QA | Qatar | 12 | 50% | PASS |
| 173 | 🇷🇴 | RO | Romania | 12 | 50% | PASS |
| 174 | 🇷🇸 | RS | Serbia | 12 | 50% | PASS |
| 175 | 🇷🇺 | RU | Russia | 12 | 50% | PASS |
| 176 | 🇷🇼 | RW | Rwanda | 12 | 50% | PASS |
| 177 | 🇸🇧 | SB | Solomon Islands | 12 | 50% | PASS |
| 178 | 🇸🇨 | SC | Seychelles | 12 | 50% | PASS |
| 179 | 🇸🇩 | SD | Sudan | 12 | 50% | PASS |
| 180 | 🇸🇪 | SE | Sweden | 12 | 50% | PASS |
| 181 | 🇸🇭 | SH | Saint Helena | 12 | 50% | PASS |
| 182 | 🇸🇮 | SI | Slovenia | 12 | 50% | PASS |
| 183 | 🇸🇰 | SK | Slovakia | 12 | 50% | PASS |
| 184 | 🇸🇱 | SL | Sierra Leone | 12 | 50% | PASS |
| 185 | 🇸🇲 | SM | San Marino | 12 | 50% | PASS |
| 186 | 🇸🇳 | SN | Senegal | 12 | 50% | PASS |
| 187 | 🇸🇴 | SO | Somalia | 12 | 50% | PASS |
| 188 | 🇸🇷 | SR | Suriname | 12 | 50% | PASS |
| 189 | 🇸🇸 | SS | South Sudan | 12 | 50% | PASS |
| 190 | 🇸🇻 | SV | El Salvador | 12 | 50% | PASS |
| 191 | 🇸🇽 | SX | Sint Maarten | 12 | 50% | PASS |
| 192 | 🇸🇾 | SY | Syria | 12 | 50% | PASS |
| 193 | 🇸🇿 | SZ | Eswatini | 12 | 50% | PASS |
| 194 | 🇹🇨 | TC | Turks and Caicos Islands | 12 | 50% | PASS |
| 195 | 🇹🇩 | TD | Chad | 12 | 50% | PASS |
| 196 | 🇹🇬 | TG | Togo | 12 | 50% | PASS |
| 197 | 🇹🇭 | TH | Thailand | 12 | 50% | PASS |
| 198 | 🇹🇯 | TJ | Tajikistan | 12 | 50% | PASS |
| 199 | 🇹🇱 | TL | Timor-Leste | 12 | 50% | PASS |
| 200 | 🇹🇲 | TM | Turkmenistan | 12 | 50% | PASS |
| 201 | 🇹🇳 | TN | Tunisia | 12 | 50% | PASS |
| 202 | 🇹🇴 | TO | Tonga | 12 | 50% | PASS |
| 203 | 🇹🇷 | TR | Turkey | 12 | 50% | PASS |
| 204 | 🇹🇹 | TT | Trinidad and Tobago | 12 | 50% | PASS |
| 205 | 🇹🇻 | TV | Tuvalu | 12 | 50% | PASS |
| 206 | 🇹🇼 | TW | Taiwan | 12 | 50% | PASS |
| 207 | 🇹🇿 | TZ | Tanzania | 12 | 50% | PASS |
| 208 | 🇺🇦 | UA | Ukraine | 12 | 50% | PASS |
| 209 | 🇬🇧 | UK | United Kingdom | 12 | 50% | PASS |
| 210 | 🇺🇸 | US | United States | 12 | 50% | PASS |
| 211 | 🇺🇾 | UY | Uruguay | 12 | 50% | PASS |
| 212 | 🇺🇿 | UZ | Uzbekistan | 12 | 50% | PASS |
| 213 | 🇻🇨 | VC | Saint Vincent and the Grenadines | 12 | 50% | PASS |
| 214 | 🇻🇪 | VE | Venezuela | 12 | 50% | PASS |
| 215 | 🇻🇬 | VG | British Virgin Islands | 12 | 50% | PASS |
| 216 | 🇻🇮 | VI | U.S. Virgin Islands | 12 | 50% | PASS |
| 217 | 🇻🇺 | VU | Vanuatu | 12 | 50% | PASS |
| 218 | 🇼🇫 | WF | Wallis and Futuna | 12 | 50% | PASS |
| 219 | 🇼🇸 | WS | Samoa | 12 | 50% | PASS |
| 220 | 🇽🇰 | XK | Kosovo | 12 | 50% | PASS |
| 221 | 🇾🇪 | YE | Yemen | 12 | 50% | PASS |
| 222 | 🇿🇦 | ZA | South Africa | 12 | 50% | PASS |
| 223 | 🇿🇲 | ZM | Zambia | 12 | 50% | PASS |
| 224 | 🇿🇼 | ZW | Zimbabwe | 12 | 50% | PASS |
| 225 | 🇩🇪 | DE | Germany | 12 | 42% | PASS |
| 226 | 🇸🇬 | SG | Singapore | 12 | 42% | PASS |
| 227 | 🇺🇬 | UG | Uganda | 12 | 42% | PASS |

Distribution: 1 packs ≥75%, 226 packs within the 33–67% chance band, 0 packs ≤25%.

## Iteration log

(no iteration log found)

## Interpretation

The aggregate score of **50.5%** against a 50% chance baseline is the finding. These are bibliographic claims about real, recently collected official legal documents (titles, dates, publishing sources, identifiers) across 227 jurisdictions. A score near chance means the model cannot verify citations from these jurisdictions from parametric memory: it does not know which decisions, gazettes and acts exist, so it cannot tell a real citation from a controlled fabrication. **Retrieval grounding against the actual source corpus is therefore mandatory** for any citation-reliability claim — this is precisely the gap the S3 retrieval extension (Sabaio L3) is built to close.

Where scores rise well above chance, inspection shows it is mostly the FALSE mutations being caught on internal-consistency grounds (e.g. a cross-jurisdiction `wrong-source` trap pairing a Dutch ECLI with a Gibraltar gazette is detectable without knowing the document), not genuine knowledge of the documents. TRUE items — which require actually knowing the document exists — hover near or below chance for most jurisdictions, and recent documents (2025–26 sample snapshot) sit past the model's training cutoff by construction.
