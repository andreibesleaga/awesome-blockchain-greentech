# **Awesome Blockchain Greentech** [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)

A curated list of awesome blockchain projects, open-source software, standards, and distributed ledger technologies dedicated to sustainability, climate action, and the green economy.

The repository contains:

* **The curated list** (this file) — third-party projects and standards, organised by theme.
* **[Innovative Projects](./Innovative%20Projects/README.md)** — six original work-in-progress system proposals (README + PRD + SPEC + ARCH per project), all aligned to a shared **Sustainability-First Consensus (SFC)** engineering profile that operationalises the framework defined in Besleaga (2026), [doi:10.1145/3809296](https://doi.org/10.1145/3809296).

**Scope:** This list focuses on software, protocols, and tools that utilize Distributed Ledger Technology (DLT) to solve environmental challenges (Regenerative Finance, dMRV, Circular Economy, Energy Grids, Digital Product Passports, Identity & Compliance).

## **Contents**

- [Standards & Frameworks](#standards--frameworks)
- [Energy Grid & P2P Trading](#energy-grid--p2p-trading)
- [Digital Carbon Markets (ReFi)](#digital-carbon-markets-refi)
- [Digital MRV (Measurement, Reporting, Verification)](#digital-mrv-measurement-reporting-verification)
- [Supply Chain & Circular Economy](#supply-chain--circular-economy)
- [Digital Product Passports (DPP)](#digital-product-passports-dpp)
- [Low-Energy Base Layers](#low-energy-base-layers)
- [Identity & Verifiable Credentials](#identity--verifiable-credentials)
- [Cross-Chain & Interoperability](#cross-chain--interoperability)
- [Decentralized Storage (Sustainable)](#decentralized-storage-sustainable)
- [Data Oracles & Climate Intelligence](#data-oracles--climate-intelligence)
- [Governance Bodies & Consortia](#governance-bodies--consortia)
- [Innovative Projects, MVPs & Proposals (2025-2026)](#innovative-projects-mvps--proposals-2025-2026)
- [Regulations, Compliance & Governance Frameworks](#regulations-compliance--governance-frameworks)


> **Note (2024 rebrand).** Most projects previously called "Hyperledger X" are now hosted under [**Linux Foundation Decentralized Trust (LFDT)**](https://www.lfdecentralizedtrust.org/), launched 16 September 2024. The "Hyperledger" name is retained for many projects (Fabric, Indy, Aries, Cacti, Identus). Some, such as Besu, dropped the prefix.

---

## **Standards & Frameworks**

*Foundational specifications and open-source standards defining the green digital economy.*

### Software & blockchain footprint
* [**Software Carbon Intensity (SCI)**](https://github.com/Green-Software-Foundation/sci) — A specification (now [ISO/IEC 21031:2024](https://www.iso.org/standard/86612.html)) from the Green Software Foundation that describes how to calculate a Software Carbon Intensity score for software applications, essential for auditing the footprint of blockchain nodes and dApps.
* [**Carbon Aware SDK**](https://github.com/Green-Software-Foundation/carbon-aware-sdk) — A tool from the Green Software Foundation that helps developers build software that runs when and where electricity is cleanest (e.g., executing heavy smart contracts during high renewable grid availability).
* [**Blockchain Carbon Accounting**](https://github.com/hyperledger-labs/blockchain-carbon-accounting) — An open-source LFDT-Labs initiative to develop a shared ledger for carbon accounting and emissions tracking.

### Token, supply-chain and integrity standards
* [**Token Taxonomy Framework (TTF)**](https://github.com/InterWorkAlliance/TokenTaxonomyFramework) — Managed by the **InterWork Alliance (IWA)**, an initiative of the [Global Blockchain Business Council (GBBC)](https://www.gbbc.io/interwork-alliance), providing a common language for defining tokenized assets, including profiles for carbon credits and ESG assets.
* [**GS1 EPCIS 2.0**](https://www.gs1.org/standards/epcis) — Event-based traceability standard (ratified June 2022). Adds JSON / JSON-LD format, sensor data ("How" dimension), and `AssociationEvent`; the de-facto interoperability vocabulary for supply-chain events.
* [**GS1 Digital Link**](https://www.gs1.org/standards/gs1-digital-link) — URI syntax that turns GS1 identifiers (GTIN, SGTIN, GLN) into resolvable Web URIs — the carrier for many DPP and traceability deployments.
* [**IETF SCITT — Supply Chain Integrity, Transparency and Trust**](https://datatracker.ietf.org/doc/charter-ietf-scitt/) — IETF working group developing standards (e.g., [`draft-ietf-scitt-architecture`](https://datatracker.ietf.org/doc/draft-ietf-scitt-architecture/)) for transparent registries of signed supply-chain statements, with verifiable data structures and notarisation flows.
* [**IEEE 2142.1**](https://standards.ieee.org/ieee/2142.1/10643/) — Recommended Practice for E-Invoice Business Using Blockchain Technology.
* [**ITU-T F.751.4**](https://www.itu.int/rec/T-REC-F.751.4) — ITU framework for electronic invoices based on distributed ledger technology.

### Climate-accounting & disclosure
* [**GHG Protocol — Corporate / Product Standards**](https://ghgprotocol.org/) — The Greenhouse Gas Protocol Corporate (Scope 1/2/3) and Product Life-Cycle Accounting Standards; the global reference for emissions accounting that on-chain MRV systems map back to.
* [**EU Corporate Sustainability Reporting Directive (CSRD) & ESRS**](https://finance.ec.europa.eu/capital-markets-union-and-financial-markets/company-reporting-and-auditing/company-reporting/corporate-sustainability-reporting_en) — EU disclosure framework; **ESRS E1 (Climate)** is the disclosure shape most blockchain MRV tools target via API export.
* [**EU Carbon Border Adjustment Mechanism (CBAM)**](https://taxation-customs.ec.europa.eu/carbon-border-adjustment-mechanism_en) — EU border-adjustment regulation driving demand for verifiable per-product embodied-carbon data.

## **Energy Grid & P2P Trading**

*Software for decentralized energy grids, renewable energy certificates (RECs), and peer-to-peer trading.*

* [**Energy Web Origin**](https://github.com/energywebfoundation/origin) — An open-source SDK and toolkits for issuing and managing **Energy Attribute Certificates (EACs)**, by the Energy Web Foundation.
* [**Energy Web X & EW-DOS**](https://www.energyweb.org/) — The Energy Web Decentralized Operating System now operates with **Energy Web X** (validator + worker-node network) alongside the Energy Web Chain. See the [2025 Yellow Paper](https://www.energyweb.org/resources) for architecture.
* [**Switchboard dApp**](https://github.com/energywebfoundation/switchboard-dapp) — Identity and access management UI for the Energy Web ecosystem, giving energy assets (batteries, EVs) self-sovereign identities (DIDs).
* [**Power Ledger**](https://www.powerledger.io/) — A leading P2P energy trading platform with live deployments across four continents (Origin Energy in Australia; CESC in India with >1 000 participants). **Migrated from Ethereum to Solana in 2026** via Wormhole NTT; dual-token model (POWR utility + Sparkz settlement).
* [**Open Charge Point Protocol (OCPP)**](https://openchargealliance.org/protocols/open-charge-point-protocol/) — Open Charge Alliance protocol for EV charge point ↔ backend communication. **OCPP 2.0.1 ed3 was approved as IEC 63584 in 2024.**
* [**Open Charge Point Interface (OCPI)**](https://evroaming.org/ocpi-protocol) — EVRoaming Foundation protocol for EV-charging roaming between charge-point operators (CPOs) and e-mobility service providers (eMSPs).

## **Digital Carbon Markets (ReFi)**

*Protocols and liquidity engines for the tokenization and trading of carbon credits.*

* [**Klima Protocol** (formerly KlimaDAO)](https://www.klimadao.finance/) — Open climate-finance infrastructure that completed its transition from KlimaDAO in February 2026, with a dual-token architecture (kVCM / K2) deployed on Base via Aerodrome / Hydrex.
* [**Carbonmark API**](https://docs.carbonmark.com/) — Open API to source, trade and retire verified carbon credits programmatically; processes 12 000+ retirement transactions/month leveraging Klima Protocol liquidity.
* [**Toucan Protocol**](https://toucan.earth/) — Carbon-credit bridge tokenising registry-backed credits (Verra, Gold Standard, Puro.earth) onto Polygon as TCO2 / batch tokens; ~21 M credits bridged to date. SDK and contracts on [GitHub](https://github.com/ToucanProtocol).
* [**Regen Network**](https://www.regen.network/) — Cosmos-SDK chain dedicated to ecological assets, with a native **Regen Registry** for scientific methodology development and a P2P **Regen Marketplace** for buying / retiring credits.
* [**Open Forest Protocol (OFP)**](https://www.openforestprotocol.org/) — Scalable open platform for forest-MRV data, validated by a network of independent experts on a NEAR-based chain.
* [**Moss.Earth**](https://moss.earth/) — Carbon-credit marketplace using on-chain MCO2 tokens, focused on Amazon rainforest preservation projects.

## **Digital MRV (Measurement, Reporting, Verification)**

*Tools that use IoT and AI to prove environmental impact on-chain.*

* [**Hedera Guardian**](https://github.com/hashgraph/guardian) — An open-source Policy Workflow Engine (PWE) that digitises ESG methodologies; creates auditable, tokenised quantitative outcomes (e.g., carbon offsets) on Hedera. [Verra integration](https://verra.org/verra-and-hedera-to-accelerate-digital-transformation-of-carbon-markets/) and [UNDP National Carbon Registry](https://hedera.foundation/blog/hedera-guardian-integrates-open-source-national-carbon-registry-initiated-by-undp) integrations are live; supports public auditability via Hedera Atlas.
* [**Open Forest Protocol (OFP)**](https://www.openforestprotocol.org/) — Forest projects of any size submit MRV data verified by independent expert nodes.
* [**GainForest**](https://github.com/GainForest) — Decentralised fund using AI to measure and reward sustainable nature stewardship (Solana / Ethereum).
* [**Veritree**](https://veritree.com/) — Cardano-based planting verification platform; the "Cardano Forest" initiative reached its 1 M-tree target and the platform continues to anchor reforestation data on-chain.
* [**dClimate**](https://www.dclimate.net/) — Decentralised climate-data marketplace (1 000+ clients; insurance, construction, finance); data publishers are scored by a DAO and integrated via Chainlink oracles.
* [**Climate Action Data (CAD) Trust**](https://climateactiondata.org/) — Open-source meta-registry founded by **IETA, the World Bank, and the Singapore Government**; links and harmonises data from Verra, the Global Carbon Council, EcoRegistry, BioCarbon Registry and the UNFCCC CDM. Operational stack runs on [Chia Network's Data Layer](https://www.chia.net/).

## **Supply Chain & Circular Economy**

*Tracking materials, waste, and product lifecycles.*

* [**Hyperledger Fabric**](https://github.com/hyperledger/fabric) — Permissioned BFT ledger hosted by **LF Decentralized Trust**; the de-facto choice for enterprise supply-chain consortia (Walmart, Maersk TradeLens — discontinued — and many active deployments). Latest major release: Fabric 3.0.
* [**VeChain**](https://www.vechain.com/) — Enterprise BaaS platform used by BMW and DNV for component traceability and circularity.
* [**IOTA DPP Demonstrator**](https://github.com/iotaledger/dpp-demonstrator) — Reference implementation for Digital Product Passports on IOTA's Tangle.
* [**IBM Food Trust**](https://www.ibm.com/think/topics/blockchain-for-supply-chain) — Production blockchain platform (built on Hyperledger Fabric) for food traceability; >2 M food products digitised; well-known mango-traceability case study (7 days → 2.2 s for Walmart).
* [**Plastic Bank**](https://plasticbank.com/) — Social fintech with a global bottle-deposit program; runs the first digitally tokenised and traceable **Plastic Credit** with blockchain-secured proof of social impact.
* [**Plastiks**](https://www.plastiks.io/) — Anti-greenwashing plastic-credits platform; PLASTIK token currently on CELO (and bridging to Cardano), with each token representing one kilogram of recovered material.

## **Digital Product Passports (DPP)**

*Tools and references for the EU Digital Product Passport regime (and beyond).*

* [**CIRPASS / CIRPASS-2**](https://cirpassproject.eu/) — EU-funded consortium developing the EU DPP roadmaps and Core Ontology (released March 2025). Pilots cover batteries, electronics, textiles, tyres and construction. The **EU Central DPP Registry** goes live with full ESPR application on **19 July 2026**.
* [**EU Battery Regulation (Regulation (EU) 2023/1542)**](https://eur-lex.europa.eu/eli/reg/2023/1542/oj) — Mandates the digital Battery Passport for EV and industrial batteries > 2 kWh from **18 February 2027**.
* [**IOTA DPP Demonstrator**](https://github.com/iotaledger/dpp-demonstrator) — DPP reference implementation on IOTA (cross-listed above).

## **Low-Energy Base Layers**

*Base-layer blockchains and rollups whose measured energy footprint fits sustainability-by-design budgets.*

* [**Algorand**](https://github.com/algorand) — Pure Proof-of-Stake L1 measured at ~0.0006 GWh/yr network-wide; [carbon-negative since 2024](https://www.algorand.foundation/sustainability) via automatic per-tx carbon-credit purchases.
* [**Hedera**](https://github.com/hashgraph/hedera-services) — aBFT Hashgraph network; [carbon-negative](https://hedera.com/sustainability), measured at ~0.00014 kWh/tx.
* [**IOTA**](https://github.com/iotaledger/iota) — DAG-based ledger; ~0.00011 kWh/tx; suited to high-frequency, low-value MRV streams.
* [**NEAR Protocol**](https://near.org/) — Sharded PoS; the [first Layer-1 to receive a *Climate Neutral Product* label](https://near.foundation/blog/near-climate-neutral-product/) (South Pole assessment, 2021).
* [**Chia Network**](https://github.com/Chia-Network/chia-blockchain) — Uses "Proof of Space and Time"; underpins the CAD Trust meta-registry. **Chia 3.0 with Proof of Space 2.0 hard-forks November 2026.**
* [**Celo** (now Ethereum L2)](https://github.com/celo-org) — **Migrated from L1 to an Ethereum L2 on the OP Stack in March 2025**, retaining mobile-first ReFi focus; #1 L2 by daily active users one year after migration.
* [**Polygon zkEVM / Polygon PoS**](https://polygon.technology/) — Low-energy EVM execution; widely used as the anchor / public-proof layer for permissioned consortium ledgers.

## **Identity & Verifiable Credentials**

*Decentralised identity infrastructure used by every credible sustainability claim system.*

* [**W3C Decentralized Identifiers (DIDs) 1.0**](https://www.w3.org/TR/did-core/) — Core W3C Recommendation for self-sovereign identifiers.
* [**W3C Verifiable Credentials Data Model**](https://www.w3.org/TR/vc-data-model/) — Core W3C standard for issuing, presenting and verifying cryptographically signed claims (certifications, audit attestations).
* [**Hyperledger Indy**](https://github.com/hyperledger/indy-node) — Distributed ledger purpose-built for decentralised identity (LFDT).
* [**Hyperledger Aries**](https://github.com/hyperledger/aries) — Toolkit and protocols for building peer-to-peer interactions on top of Indy / VCs.
* [**Sovrin Network**](https://sovrin.org/) — Public-permissioned Indy-based network governed by the Sovrin Foundation.
* [**Energy Web Credentials**](https://github.com/energywebfoundation/ew-credentials) — SSI / VC libraries for energy assets.

## **Cross-Chain & Interoperability**

*Infrastructure for connecting heterogeneous ledgers — including consortium ↔ public anchors used in sustainability designs.*

* [**Hyperledger Cacti**](https://github.com/hyperledger-cacti/cacti) — Graduated LFDT project for cross-ledger interoperability (merger of Cactus + Weaver Lab). Pluggable connectors for Fabric, Besu, Polkadot and more.
* [**IBC — Inter-Blockchain Communication Protocol**](https://ibcprotocol.org/) — Native chain-to-chain messaging across Cosmos-SDK / Substrate ecosystems; battle-tested, ~100+ IBC-enabled chains.
* [**Chainlink CCIP**](https://chain.link/cross-chain) — Cross-Chain Interoperability Protocol connecting 60+ EVM and non-EVM networks via Chainlink's oracle infrastructure.

## **Decentralized Storage (Sustainable)**

*Storage tiers used to hold the off-chain payloads that on-chain hashes anchor (DPP documents, MRV evidence, sensor logs).*

* [**Filecoin**](https://www.filecoin.io/) — Decentralised storage network; >14 exbibytes committed by >3 600 storage providers globally.
* [**Filecoin Green**](https://fil.org/ecosystem-explorer/filecoin-green) — Sustainability initiative within Filecoin; has matched **2.6 TWh of renewable energy** with storage providers (verifiable via the Filecoin Energy dashboard) and targets verifiably-below-zero impact.
* [**IPFS**](https://ipfs.tech/) — Content-addressed protocol underlying many DLT off-chain payload patterns (DPP, MRV evidence, receipts).

## **Data Oracles & Climate Intelligence**

*Connecting real-world sensors, weather data, and grid-intensity data to the blockchain.*

* [**Chainlink**](https://github.com/smartcontractkit/chainlink) — Industry-standard oracle network used to bring weather data and satellite imagery on-chain for crop insurance and carbon-removal verification.
* [**Electricity Maps**](https://www.electricitymaps.com/) — Real-time and historical grid-carbon-intensity API covering 160+ zones; the canonical source for measuring Scope 2 emissions of node operators.
* [**Crypto Carbon Ratings Institute (CCRI) Sustainability API**](https://carbon-ratings.com/) — Independent network-level energy and carbon assessments for 20+ blockchains (PoS, aBFT, DAG, permissioned BFT), using the hybrid-allocation framework jointly developed with South Pole.
* [**Cambridge Bitcoin Electricity Consumption Index (CBECI)**](https://ccaf.io/cbeci/index) — University of Cambridge methodology for measuring PoW network energy; the reference for "before/after" comparability claims.

## **Governance Bodies & Consortia**

*Open foundations, alliances and observer organisations driving the green-DLT space.*

* [**LF Decentralized Trust**](https://www.lfdecentralizedtrust.org/) — Linux Foundation umbrella (launched Sept 2024) hosting Hyperledger Fabric, Indy, Aries, Cacti, Identus, Besu and other DLT projects.
* [**Global Blockchain Business Council (GBBC) — InterWork Alliance**](https://www.gbbc.io/interwork-alliance) — Standards body for tokenised ecosystems; stewards the Token Taxonomy Framework.
* [**Energy Web Foundation**](https://www.energyweb.org/) — Non-profit advancing decentralised energy with the Energy Web Chain, EW-DOS, and Energy Web X.
* [**Hedera Foundation — Sustainable Impact Fund**](https://hedera.foundation/) — Co-funds the [DLT Earth](https://www.dltearth.com/) grant program (with Exponential Science) for climate-DLT projects.
* [**Crypto Climate Accord**](https://cryptoclimate.org/) — Industry initiative (launched by Energy Web, RMI, AIR; 250+ supporters) targeting net-zero electricity-emissions for signatories by 2030 and full crypto-industry net-zero by 2040.
* [**Climate Chain Coalition (CCC)**](https://climatechaincoalition.org/) — UNFCCC observer organisation (360+ member orgs) advancing DLT and related digital innovations for climate finance and MRV.
* [**International Emissions Trading Association (IETA)**](https://www.ieta.org/) — Founding partner of CAD Trust; sets industry voice on Article 6 / carbon markets.
* [**EVRoaming Foundation**](https://evroaming.org/) — Stewards the OCPI roaming standard for EV charging.
* [**Open Charge Alliance**](https://openchargealliance.org/) — Stewards OCPP for charger ↔ backend communication.

---

## **Innovative Projects, MVPs & Proposals (2025-2026)**

*A spotlight on recent hackathon winners, pilot programs, academic proposals, and patents driving the next wave of green innovation.*

### **🏆 Hackathon Winners & MVPs**

* [**Carbon Management Platform**](https://devpost.com/) *(Hedera "Hello Future" Winner 2025)* — An end-to-end verifiable carbon management platform that issues NFT-based carbon certificates and provides compliance-ready reporting for enterprises.
* [**Nodebility**](https://devpost.com/) *(Hedera "Hello Future" Winner 2025)* — An MVP leveraging AI-powered "Bionodes" to quantify the conversion of organic waste into clean energy and carbon credits, targeting methane emission reduction.
* [**Greenchain**](https://github.com/MVPWorkshop/greenchain) *(Open Source MVP)* — A proof-of-concept dApp for tracking waste-management lifecycles, allowing stakeholders to add certification data and enabling consumers to scan product QR codes for recycling info.
* [**IOTA DPP Reference Implementation**](https://github.com/iotaledger/dpp-demonstrator) *(Reference Implementation)* — A working prototype by the IOTA Foundation showcasing how Digital Product Passports can be orchestrated to authorise repairs and track component history in a circular economy.

### **🧪 Corporate & Government Pilots (2025-2026)**

* [**ebitts (Enel x Conio)**](https://algorand.co/case-studies/enel-tokenizing-renewable-energy-assets-on-algorand) — A pilot by Enel (Europe's largest utility) on **Algorand**; tokenises solar panels so Italian residents virtually own fractions of renewable plants and deduct generated energy value from their utility bills.
* [**Klima Protocol Japan**](https://carboncredits.com/klimadao-japan-launches-blockchain-powered-carbon-credits-market/) — Strategic pilot with **SoftBank** and **Mizuho** for a regulated digital carbon-credit market in Japan (tokenising J-Credits via the Carbonmark API). *(Klima Protocol was rebranded from KlimaDAO in Feb 2026.)*
* [**CarbonX 2.0 Finalist**](https://static.www.tencent.com/attachments/ssv/2025/CarbonX%202.0%20Finalists.pdf) — Kenya pilot selected by Tencent's CarbonX program, focused on Direct Air Capture (DAC) powered by renewable geothermal energy, with on-chain verification of carbon-removal credits.
* [**GSMA eBusiness Network**](https://www.gsma.com/solutions-and-impact/industry-services/blog/how-blockchain-is-evolving-wholesale-roaming-processes/) — Hyperledger Fabric–based commercial network (live since 2021) automating wholesale telecom-roaming settlement between major MNOs (DT, CK Hutchison, Orange, Telefónica, Verizon, Vodafone).
* [**MediLedger Network**](https://coldchaincheck.com/news/how-mediledger-blockchain-is-transforming-pharmaceutical-supply-chain-compliance) — Production pharma traceability network on Hyperledger Fabric; ~1.6 B transactions/year, 27 manufacturers, 18 distributors. The Product Verification System was acquired by [**NABP**](https://nabp.pharmacy/news/news-releases/nabp-acquires-patient-safety-tool-from-chronicled-inc/) in late 2024 for *Pulse by NABP*, aligned with US DSCSA.

### **📜 Patents & Academic Proposals**

* [**Carbon Credit Tokenization Patent**](https://ir.datavaultsite.com/news-events/press-releases/detail/338/the-carbon-credit-tokenization-patent-issued-friday-june) *(Granted 2025)* — Newly issued patent for a "Carbon Credit Tokenization System" integrating AI and blockchain; licensed to **Nature's Miracle** for agricultural sustainability.
* [**DePIN Urban Monitoring**](https://www.frontiersin.org/journals/blockchain/articles/10.3389/fbloc.2025.1626695/full) *(Academic Pilot)* — Decentralised IoT-sensor deployment in Nairobi, Kenya, monitoring environmental variables for urban green spaces; documents cost reduction and fractional income for community data collectors.
* [**AI-Enhanced Verification Framework**](https://www.researchgate.net/publication/394517770_AI-Enhanced_Blockchain_Networks_for_Climate_Change_Monitoring_and_Carbon_Credit_Verification) *(Research Proposal)* — Architecture combining "Brilliant Contracts" with satellite-imagery analysis (U-Net / ResNet-50) for automated carbon-credit verification (>94 % claimed accuracy).
* [**BlockRoam**](https://arxiv.org/abs/2005.04571) *(Academic Reference)* — Peer-reviewed blockchain-based roaming-management system for mobile networks; PoS consensus + Stackelberg-game incentive model.
* [**"Sustainability-First Consensus" Ledgers for a Green Digital Future** (Besleaga 2026)](https://doi.org/10.1145/3809296) *(Accepted,Communications of ACM)* — Defines the four-criterion SFC framework (energy, hardware, carbon, regulatory) applied by all projects in this repo's [Innovative Projects](./Innovative%20Projects/README.md) directory.

## **Regulations, Compliance & Governance Frameworks**

*Acts, regulations, standards-bodies' deliverables and authoritative policy papers specifically on Blockchain / DLT — what builders and integrators in the green-DLT space must align with.*

### International standards (ISO)
* [**ISO/TC 307 — Blockchain and Distributed Ledger Technologies**](https://www.iso.org/committee/6266604.html) — The ISO Technical Committee (secretariat: Standards Australia) producing the family of international standards on blockchain / DLT.
* [**ISO 22739:2024 — Blockchain and DLT — Vocabulary**](https://www.iso.org/standard/82208.html) — The authoritative international terminology for the field (2024 revision of the 2020 first edition).
* [**ISO 23257:2022 — Blockchain and DLT — Reference architecture**](https://www.iso.org/standard/75093.html) — Concepts, cross-cutting aspects, architectural views, functional components, roles and activities for DLT systems.
* [**ISO/IEC 21031:2024 — Software Carbon Intensity (SCI) Specification**](https://www.iso.org/standard/86612.html) — ISO/IEC publication of the Green Software Foundation SCI spec; relevant to measuring blockchain-node and dApp footprint.

### IEEE standards
* [**IEEE Blockchain — Standards portal**](https://blockchain.ieee.org/standards) — Index of active IEEE blockchain standards and working groups.
* [**IEEE 2418.1**](https://sagroups.ieee.org/2418-1/) — Framework for blockchain use, implementation and interaction with IoT (security / privacy in blockchain-IoT integration).
* [**IEEE 2418.2-2020**](https://sagroups.ieee.org/2418-2/) — Data Format for Blockchain Systems (data structure, classification, identifiers, length).
* [**IEEE 2418.5-2025 — DLT for the Energy Sector**](https://standards.ieee.org/ieee/2418.5/11217/) — Open, common, interoperable reference framework for DLT in energy; directly applicable to green-grid use cases.
* [**IEEE 2418.10-2022 — Blockchain-based Digital Asset Management**](https://ieeexplore.ieee.org/document/9810177/) — Baseline architectural framework, use cases, functional and security requirements.
* [**IEEE 2145-2023 — Framework and Definitions for Blockchain Governance**](https://standards.ieee.org/ieee/2145/10143/) — Trial-Use Recommended Practice: common nomenclature and governance framework across public, private, permissioned, permissionless and hybrid blockchains.
* [**IEEE 2142.1**](https://standards.ieee.org/ieee/2142.1/10643/) — Recommended Practice for E-Invoice Business Using Blockchain (cross-listed above).

### EU DLT-specific regulations
* [**MiCA — Markets in Crypto-Assets Regulation (EU) 2023/1114**](https://eur-lex.europa.eu/eli/reg/2023/1114/oj/eng) — Full crypto-asset regulatory framework. **ARTs & EMTs in application since 30 June 2024; full regime including CASPs in application since 30 December 2024.** [ESMA hub](https://www.esma.europa.eu/esmas-activities/digital-finance-and-innovation/markets-crypto-assets-regulation-mica).
* [**DLT Pilot Regime — Regulation (EU) 2022/858**](https://eur-lex.europa.eu/eli/reg/2022/858/oj/eng) — Tailored regime for DLT market infrastructures (DLT MTF, DLT SS, DLT TSS) issuing / settling tokenised securities; **in application since 23 March 2023**. [ESMA review (June 2025)](https://www.esma.europa.eu/sites/default/files/2025-06/ESMA75-117376770-460_Report_on_the_functioning_and_review_of_the_DLTR_-_Art.14.pdf).
* [**eIDAS 2.0 — Regulation (EU) 2024/1183 (EUDI Wallet)**](https://eur-lex.europa.eu/eli/reg/2024/1183/oj) — Establishes the European Digital Identity (EUDI) Wallet framework; **in force since 20 May 2024**, mandatory issuance by each Member State by **31 December 2026**. Most ledger-anchored identity / verifiable-credential designs in the EU will integrate with this.
* [**Data Act — Regulation (EU) 2023/2854**](https://eur-lex.europa.eu/eli/reg/2023/2854/oj) — IoT data access, sharing, portability and switching of cloud services; **applies from 12 September 2025**, with interoperability provisions phasing in through 2026-2027.
* [**DORA — Digital Operational Resilience Act (Regulation (EU) 2022/2554)**](https://eur-lex.europa.eu/eli/reg/2022/2554/oj) — Operational-resilience requirements for financial entities and their critical third-party ICT providers; **in application since 17 January 2025** (touches CASPs, DLT MIs and ledger-anchored finance services).
* [**ESPR — Ecodesign for Sustainable Products Regulation (EU) 2024/1781**](https://eur-lex.europa.eu/eli/reg/2024/1781/oj) — Enabling regulation for the EU Digital Product Passport; **EU Central DPP Registry goes live with full ESPR application on 19 July 2026**.
* [**EU Battery Regulation (EU) 2023/1542**](https://eur-lex.europa.eu/eli/reg/2023/1542/oj) — Digital Battery Passport mandatory for EV and industrial batteries > 2 kWh from **18 February 2027** (cross-listed under DPP).

### UN bodies and trade law
* [**UNCITRAL Model Law on Electronic Transferable Records (MLETR, 2017)**](https://uncitral.un.org/en/texts/ecommerce/modellaw/electronic_transferable_records) — Legal framework enabling DLT-based electronic bills of lading and other transferable records. Adopted in 11+ jurisdictions including **United Kingdom (2023), France (2024), Mauritius (2025), Timor-Leste (2024), Singapore (2021), UAE-ADGM (2021)**. [Status tracker](https://uncitral.un.org/en/texts/ecommerce/modellaw/electronic_transferable_records/status).
* [**UN/CEFACT — White Paper on Blockchain in Trade Facilitation**](https://unece.org/DAM/trade/Publications/ECE-TRADE-457E_WPBlockchainTF.pdf) — UNECE / UN/CEFACT analysis of how DLT integrates with international trade-facilitation standards.
* [**UN/CEFACT — Data Governance for Trade Facilitation (Nov 2024)**](https://unece.org/sites/default/files/2024-11/WhitePaper-DataGovernanceTradeFacilitation.pdf) — Most recent UN/CEFACT white paper covering DLT-relevant data-governance practice.
* [**UNFCCC — Article 6 of the Paris Agreement**](https://unfccc.int/process-and-meetings/the-paris-agreement/article-64-paris-agreement) — Establishes the international cooperative mechanisms (including the Article 6.4 Mechanism / "PACM") underpinning the regulated carbon-credit registries that DLT-native systems integrate with.

### NIST (US)
* [**NIST IR 8202 — Blockchain Technology Overview**](https://csrc.nist.gov/pubs/ir/8202/final) — High-level technical reference on DLT concepts, consensus models and cryptographic mechanisms; the canonical US public-sector reference text.
* [**NIST IR 8408 — Stablecoin Terminology**](https://csrc.nist.gov/pubs/ir/8408/final) — Companion vocabulary for the tokenised-money portion of the DLT landscape.

### Financial-stability, AML and prudential bodies
* [**FATF Recommendation 15 — Virtual Assets & VASPs**](https://www.fatf-gafi.org/en/topics/virtual-assets.html) — Global AML/CFT standard for virtual assets, including the **Travel Rule** for VASP-to-VASP transfers.
* [**FATF Targeted Update on VAs / VASPs (June 2025)**](https://www.fatf-gafi.org/en/publications/Fatfrecommendations/targeted-update-virtual-assets-vasps-2025.html) — Sixth targeted update; 85 jurisdictions now implementing the Travel Rule (up from 65 in 2024). [Status by jurisdiction](https://www.fatf-gafi.org/en/publications/Virtualassets/VACG-Snapshot-Jurisdictions.html).
* [**FATF — Best Practices Travel Rule Supervision (June 2025)**](https://www.fatf-gafi.org/content/dam/fatf-gafi/recommendations/Best-Practices-Travel-Rule-Supervision.pdf) — Operational supervision guidance for competent authorities.
* [**Basel Committee — SCO60: Cryptoasset exposures**](https://www.bis.org/basel_framework/chapter/SCO/60.htm) — Prudential treatment of banks' cryptoasset exposures (in force from 1 January 2026).

### BIS Innovation Hub — DLT / tokenisation projects
* [**Project Agorá**](https://www.bis.org/about/bisih/topics/fmis/agora.htm) — Public-private cross-border tokenised-payments project led by the BIS Innovation Hub with seven central banks and ~40 private financial institutions; in build / testing phase, prototype report expected H1 2026.
* [**Project mBridge**](https://www.bis.org/about/bisih/topics/fmis/mcbdc_bridge.htm) — Multi-CBDC cross-border platform (BIS exited Oct 2024; the participating central banks of China, Hong Kong, Thailand, the UAE and Saudi Arabia continue — over **$55.5 B settled** to date).
* [**BIS Innovation Hub — Projects portal**](https://www.bis.org/about/bisih/projects.htm) — Index of completed / active DLT-related Hub projects (Mariana, Helvetia, Tourbillon, Polaris, etc.).

### OECD policy work
* [**OECD Recommendation on Blockchain and other DLT**](https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0470) — OECD Council policy recommendation on responsible DLT innovation.
* [**OECD — Tokenisation of Assets and DLT in Financial Markets (Jan 2025)**](https://www.oecd.org/content/dam/oecd/en/publications/reports/2025/01/tokenisation-of-assets-and-distributed-ledger-technologies-in-financial-markets_be149012/40e7f217-en.pdf) — Risks, market trends and policy implications report adopted by the OECD Committee on Financial Markets.
* [**OECD Global Blockchain Policy Forum**](https://www.oecd-events.org/blockchain-policy-forum) — Recurring OECD policy convening on blockchain / DLT.

### EU policy coordination
* [**EU Blockchain Observatory and Forum**](https://blockchain-observatory.ec.europa.eu/) — European Commission policy / research hub publishing thematic reports on DLT (including [Digital Product Passports — A Blockchain-based Perspective](https://blockchain-observatory.ec.europa.eu/document/download/b6e3c85c-43c1-405b-aba8-e49a71249ef7_en?filename=EUBOF_DPP_report.pdf)).
* [**European Blockchain Services Infrastructure (EBSI)**](https://ec.europa.eu/digital-building-blocks/sites/display/EBSI/Home) — EU public-sector blockchain network (joint with the European Blockchain Partnership) delivering use cases including verifiable credentials, notarisation and supply-chain.


---

## **Contributing**

Contributions are welcome to the curated list. See [CONTRIBUTING.md](./CONTRIBUTING.md). Note that the [Innovative Projects](./Innovative%20Projects/) subdirectory is licensed CC BY-NC-ND 4.0 and does not require external PRs.

## **License**

This repository is dual-licensed:

* **The curated list** (this `README.md` and the [LICENSE](./LICENSE) file at the root) is licensed under the [Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/).
* **The [Innovative Projects](./Innovative%20Projects/) directory** (original system proposals: README + PRD + SPEC + ARCH per project, plus `SFC_COMPLIANCE.md`) is licensed under a [Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License (CC BY-NC-ND 4.0)](https://creativecommons.org/licenses/by-nc-nd/4.0/), © Andrei Nicolae Besleaga. See [Innovative Projects/LICENSE](./Innovative%20Projects/LICENSE) for the full text.

Repository: [https://github.com/andreibesleaga/awesome-blockchain-greentech](https://github.com/andreibesleaga/awesome-blockchain-greentech)
