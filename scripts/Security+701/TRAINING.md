# Professor Messer Security+ SY0-701 Course Structure

> The CompTIA Security+ SY0-701 is an industry-standard cybersecurity certification that validates the foundational, practical skills required to secure networks, devices, and data. It focuses on modern threats, cloud operations, zero-trust architectures, and automated security solutions

This is a personal documentation of the Professor Messer Security+ 701 Training.

---

## Section 0: The SY0-701 CompTIA Security+ Exam
**Topics:**
### 0.1 Introduction
- ComTIA - Computer Technology Industry Association

- Last Exam Released in Nov 2023, will be available until Nov 2026 with 6 months grace period.

- 90min exam, 90 questions

- 750 point scale to achieve 100-900 points

- Multiple choice, matching, sorting

- Objectives => CompTIA.org and ProfessorMesser.com/objectives

- Videos ==> ProfessorMesser.com

- Book ==> ProfessorMesser.com

- Hands-On ==> ProfessorMesser.com

<img width="1256" height="603" alt="1 0 Overview" src="https://github.com/burcuhuff/secure-agent-execution/blob/main/scripts/Security+701/1.0%20Overview.png?raw=true" />


---

## Section 1: General Security Concepts
**Topics:**
### 1.1 Security Controls
- Technical Controls (OS, System, Firewalls, Anti-virus)

- Managing Controls (Admin, Security Policies)

- Operational Controls (People instead of systems)

- Physical Controls (Guards, Locks, Badges)

<img width="1256" height="603" alt="1.1 Security Goals" src="https://github.com/burcuhuff/secure-agent-execution/blob/main/scripts/Security+701/1.1%20Security%20Goals.png?raw=true" />


### 1.2 Security Concepts
- The CIA Triad (Confidentiality, Integrity, Availability)
<img width="1256" height="603" alt="1.2 The CIA Triad" src="https://github.com/burcuhuff/secure-agent-execution/blob/main/scripts/Security+701/1.2%20The%20CIA%20Triad.png?raw=true" />

- Confidentiality: Encryption, Limits - access control, Two factor authenticaton

- Integrity: Hashing, Digital Signatures, Certificates, Non-reputation

- Availability: Redundancy (always up and running), Fault tolarance, Pathcing


### 1.3 Change Management
- Non-repudiation: Proof of integrity (encryption) + Proof of origin (authentication)

<img width="1256" height="603" alt="1.3 Authentication" src="https://github.com/burcuhuff/secure-agent-execution/blob/main/scripts/Security+701/1.2%20Authentication.png?raw=true" />

- Digital Signature:
<img width="1256" height="603" alt="1.3 Digital Signature" src="https://github.com/burcuhuff/secure-agent-execution/blob/main/scripts/Security+701/1.2%20Digital%20Signature.png?raw=true" />

- Verification of Digital Signature:
<img width="1256" height="603" alt="1.3 Verification of Digital Signature" src="https://github.com/burcuhuff/secure-agent-execution/blob/main/scripts/Security+701/1.4%20Verifying%20Digital%20Signature.png?raw=true" />

- Zero Trust:
<img width="1256" height="603" alt="1.3 Zero Trust" src="https://github.com/burcuhuff/secure-agent-execution/blob/main/scripts/Security+701/1.2%20Zero%20Trust%20.png?raw=true" />

### 1.4 Cryptographic Solutions

- Aunthentication - Authorization - Accounting

- Starts with identification -> Authorization is next -> A log of what happened shows the Accounting in terms of resources used. 

- Blockchain Ledger: Distributed Ledger keeps track of transactions, pay,ents, digital voting, etc.
<img width="1256" height="603" alt="1.4 Blockchain Process" src="https://github.com/burcuhuff/secure-agent-execution/blob/main/scripts/Security+701/1.4%20Blockchain%20Process.png?raw=true" />

- Digital Certifications: 

- Binds public key with a digital signature.

- PKI uses digital certificates to authorize for additional trust.
<img width="1256" height="603" alt="1.4 PKI" src="https://github.com/burcuhuff/secure-agent-execution/blob/main/scripts/Security+701/1.4%20Public%20Key.png?raw=true" />

- Standar format is X.509

- Details can be found on the certificate are Seriial #, Version, Signature algorithm, Issuer, Name, Public Key ...

- CRL - Revoked certificates go under clear list

- Example attack ==> "Heartbleed" Open SSL app library using app server private key - 2014

- OCSCP ==> Online Certificate Status Protocol (cross referencing CRL)

<img width="1256" height="603" alt="1.4 Encryption Algorithm Comparison" src="https://github.com/burcuhuff/secure-agent-execution/blob/main/scripts/Security+701/1.4%20Encryption%20Algorithm%20Comparison.png?raw=true" />

---

## Section 2: Threats, Vulnerabilities, and Mitigations
**Topics:**
### 2.1 Threat Actors and Motivations
- ART ==> Advance Resistant Threat
- Example: "Stuxnet Worm"

### 2.3 Vulnerability Identification
- Memory Injections
- Buffer Overflows
- Race Condition
- Malicious Updates
- OS System Vulnerabilities
- SQL Injection
- Cross-site Scripting
- Virtualization Vulnerabilities
- Supply Chain Vulnerabilities
- Misconfiguration Vulnerabilities
- Mobile Device Vulnerabilities
- Zero-day Vulnerabilities
### 2.4 Indicators of Malicious Activity
- Malware
- Viruses and Worms
- Spyware and Bloatware
- Physical Attacks(ex: RFID cloning done by cloners sold on Amazon)
- Denial of Service attacks
  - Forcing a service to fail
  - DDoS: Distributed Denial of Service (launching an arm pf computers)
  - DDoS is an Asymetric Threat (number of attackers vs the number of services they reach)
  - DNS amplification DDoS
  <img width="1256" height="603" alt="1.4 DOS Amplification Distributed" src="https://github.com/burcuhuff/secure-agent-execution/blob/main/scripts/Security+701/1.4%20DDoS.png?raw=true" />
  - DNS Poisoning Attacks:
      - Modifies DNS server over the client host file that precedent over DNS queries.
      - Attack takes place by sending a fake response to a valis DNS request
      - Requirs a redirectioon of the original request
      - Occurs real time redirection
      - It's an on-path attack
      <img width="1256" height="603" alt="DNS Spoofing / Poisoning" src="https://github.com/burcuhuff/secure-agent-execution/blob/main/scripts/Security+701/2.4%20DNS%20Attacks%20-%20Spoofing%20and%20Posining.png?raw=true" />
- Wireless attack
    - Disconnects wireless users frequently by deauthentication causing a significant wireless DoS attack.
    - Main vulnerability associated with this attack relates to the 802.11 management frames that are sent and recieved by the access point to and from your machine.
    - Management frames are used to connect your device to the wireless network, manage connection, and disconnect from the network when we done with the wireless connection.
    - The connection and disconnection requires authentication and deauthentication of the device and the earlier versions of these management frames (802.11) didn't have the necessary security protocols (no encryption).
    - Packet capture on 802.11
    <img width="1256" height="603" alt="Packet capture on 802.11 wireless network" src="https://github.com/burcuhuff/secure-agent-execution/blob/main/scripts/Security+701/2.4%20Packet%20Capture%20on%20802.11.png?raw=true" />
    - IEEE has upgraded the management frames to 802.11ac and newer by encrypting some of the important management frames (disassociate, deauthenticate, channel switch annoucements etc).
    - Sample Wireless Attack:
        - Getting the information from the network: Running a command with airodump-ng utility and specifying the wirelss card:
        <img width="1256" height="603" alt="Wireless Attack airodump-ng utility" src="https://github.com/burcuhuff/secure-agent-execution/blob/main/scripts/Security+701/2.4%20Wireless%20Attack%20-%20airodump-ng%20to%20list%20the%20devices.png?raw=true" />
        - Listing hardware addresses for the wireless access point and the device:
        <img width="1256" height="603" alt="Wireless Attack listed the devicess" src="https://github.com/burcuhuff/secure-agent-execution/blob/main/scripts/Security+701/2.4%20Wireless%20Attack%20-%20airodump-ng%20returning%20device%20list.png?raw=true" />
        - Running a command to send deauthentication frames across the wireless network - using the utility "aireplay-ng" and specify "-0" to send deauthentication frames, select wireless access points (hardware ID) and the device we'd like to remove from the wireless with its mac address. 
        <img width="1256" height="603" alt="Wireless Attack sending aireplay-ng to deauth the device" src="https://github.com/burcuhuff/secure-agent-execution/blob/main/scripts/Security+701/2.4%20Wireless%20Attack%20-%20aireplay%20command%20to%20remove%20the%20device.png?raw=true" />
        - Once the aireplay runs the "pm" network listed on the left side would disappear and can't connect back as long as the command is running. 
        <img width="1256" height="603" alt="aireplay-ng disappears the network" src="https://github.com/burcuhuff/secure-agent-execution/blob/main/scripts/Security+701/2.4%20Wireless%20Attack%20-%20attacked%20network%20disappears%20.png?raw=true" />
        - As long as the deauthentication frames are sent the device can't connect to the wireless
        <img width="1256" height="603" alt="Wireless Attack device can't connect while the deauth frames are sent" src="https://github.com/burcuhuff/secure-agent-execution/blob/main/scripts/Security+701/2.4%20Wireless%20Attack%20-%20device%20can't%20connect%20while%20deauth%20frames%20are%20being%20sent.png?raw=true" />
- On-Path attacks:
    - Invisible to the victim.
    - ARP poisoning (Address Resolution Protocol spoofing) to redirect the traffic to attacker›
    <img width="1256" height="603" alt="legiminate ARP connection" src="https://github.com/burcuhuff/secure-agent-execution/blob/main/scripts/Security+701/2.4%20ARP%20Poisoning%201.png?raw=true" />
    <img width="1256" height="603" alt="attacker overwriting the cache" src="https://github.com/burcuhuff/secure-agent-execution/blob/main/scripts/Security+701/2.4%20ARP%20Poisoning%202.png?raw=true" />
    <img width="1256" height="603" alt="attacker taking over the communication with the router" src="https://github.com/burcuhuff/secure-agent-execution/blob/main/scripts/Security+701/2.4%20ARP%20Poisoning%203.png?raw=true" />
- Replay attacks
    - Use salting to change hashing time
    - Information stored in cookies, especially sessionIDs --> Tools like Wireshark or Kismet can capture packets containing cookies and sessionIDs.
    - Exploits Cross-sire scripting
    - Headers can be modifed
    - Everything can be crypted, Force-TLS
- Malicious code
    - WannaCry ransomware: Executable expoited a vulnerability in Windows SMBv1
    - British Airways cross-site scripting with 22 lines of malicous JavaScript code
    - Estonian Central Health Database: SQL injection breaching all healtcare information for an entire country
- Application attacks
    - Code injection by adding your own information, enabled by bad programming (not handling input/outut), driven by multiple injectables like HTML, SQL, XML, LDAP etc.
    - Buffer overflow writes into the memory and explicitly tries to spill over into the other memory areas, enabled by bad programming not checking inout/output errors causing bound check failures, not an easy exploit because memory allocation works differently in different systems and applications but once a consistent buffer overflow exploited it a system can be compromised.
    - Replay attacks, transmitted over network, information can be reserved to the server to gain access. ARP poisoning, sessionId hacking etc are one of the replay attacks.
    - Privilege esclation by gaining higher-level access to a system, a common attack type - or horizontal access to gain access to another user. CVE-2023-29336 May 2023 Win32k Kernel driver on Windows10 to give SYSTEM privilege.
    - Cross-site request, Cross-site request forgery (XSRF, CSRF - sea surf), many websites use anti-forgery techniques added usually with a cryptographic token to prevent a forgery. Attacker sends a link targetting to a secure login application flow and if the victim clicks on the link while they're logged in, the web server can take the attacker's request while the user is securely logged in to their system.
    <img width="1256" height="603" alt="XSRF" src="https://github.com/burcuhuff/secure-agent-execution/blob/main/scripts/Security+701/2.4%20XSRF.png?raw=true" />
    - Directory traversal / path traversal - read files from a webserver that are outside of the website file directory. Example: "GET http:.//www.example.com/show.asp?view=../../Windows/system.ini HTTP/1.1"
- Cryptographic attacks
    - Implementation of cryptography is most common
    - Brithday attack - in a classroom of 23 students the chance of sharing a birthday is about 50% => Hash collision is the same idea, shorter the hash output size, higher the chances of an attacker to find a hash collision.
    - MD5 (Message Digest Algorithm 5) published in 1992, collision identified in 1996, in 2008 researchers created  CA certificate that wasn't signed for a digital certificate but marked legitimate when MD5 is checked.
    - With 2 plain texts with differences highlited in red, MD5 creates the same hash causing collision
    <img width="1256" height="603" alt="MD5 Hash Collision" src="https://github.com/burcuhuff/secure-agent-execution/blob/main/scripts/Security+701/2.4%20Hash%20Collision%20MD5.png?raw=true" />
    - Downgrade attacks
        - SSL stripping
            - Combines an on-path attack with a downgrade attack
            - Difficult to implement
            - Attacker takes advantage of HTTP request instead of HTTPS, user sends a http request to a webserver, using on-path attack the attacker interjects the http request and sends it to the web server.
            - Web server responds to the attacker with 301, attacker sends the request again with https and recieves 200 HTTPS and forwards that 200 in HTTP to the client visitor. After this everthing the client sends occurs on the clear as the attacker captures, views, and some cases modifies the communication in the middle.
            <img width="1256" height="603" alt="SSL Stripping" src="https://github.com/burcuhuff/secure-agent-execution/blob/main/scripts/Security+701/2.4%20SSL%20Stripping.png?raw=true" />
- Password attacks
     - Spraying attacks: Try without error attack on passwords using most commonly used passwords only for 3 times to move to the next account.
     - Brute-Force: Trying the password until it matched to the hash
     <img width="1256" height="603" alt="Password Hash Brute-Force" src="https://github.com/burcuhuff/secure-agent-execution/blob/main/scripts/Security+701/2.4%20Password%20Hash%20Brute-Force.png?raw=true" />
- IOC (Indicators of Compromise)
    - An event that indicates an intrusion
    - Account locked out with exceed login attemps
    - Checking authentication logs
    - Resource consumption, file transfers use bandwitdh
    - Out-of-cycle logs showing patches occuring unsual schedule could be an indicator
    - Firewall log activity
    - Log information is evidence - creater report based on log activity before the logs modified and cleaned by attacker
### 2.5 Mitigation Techniques
- Segmentation and Access control
    - Pyhsical, logical, or virtual segmentations
    - High-bandwith applications can be segmented for perfromance reasons
    - Users to resources can be segmented for security reasons
    - Mandated segmentation for compliane reasons to make controls much easier
    - ACLs (Access Control Lists) allowing or diallowing traffic to groups, categories, source IPs, port number, time of the day, application etc.
- Mitigation echniques
    - Patching (System stability, security fixes)
    - Monthly updates
    - Third-party updates
    - Auto-updates
    - Emergency out-of-band updates
    - Encryption to prevent access to application data files (EFS - encrypting file system, FDE - full disk encryption BitLocker, FileVault etc)
    - Application data encryption
    - Aggregte information from devices built-in sensors, servers, switches, routers, filewalls => SIEM consoles to collect all the information and monitor the data
    - Least privilege
    - Decommisioning old devices
- Harderning Techniques
    - System or hardware hardening with encryption
    - EDR - Endpoint detetion and response
    - Host-based firewall
    - HIPS (Host-based Intrusion Prevension System)
    - Nmap scans open ports for an application
---

## Section 3: Security Architecture
**Topics:**
### 3.1 Security Implications of Architecture Models
### 3.2 Enterprise Infrastructure Security
### 3.3 Data Protection
### 3.4 Resilience and Recovery



---

## Section 4: Security Operations
Topics:
### 4.1 Security Techniques in Computing Resources
### 4.2 Asset Management
### 4.3 Vulnerability Management
### 4.4 Incident Response
### 4.5 Security Monitoring
### 4.6 Disaster Recovery and Business Continuity



---

## Section 5: Security Program Management and Oversight
Topics:
### 5.1 Security Governance
### 5.2 Risk Management
### 5.3 Third-Party Risk Management
### 5.4 Compliance
### 5.5 Audits and Assessments
### 5.6 Security Awareness



---
