<h1 align="center">Cisco ACI Know Your Contract: an ACL like contract visualiser </h1>
<h3 align="center">ACI_KYC</h3>

  <p align="center">
    A tool to get the deployed ACI contracts from the Fabric and present it in a human readable format.
  </p>
</div>

# About the project
Cisco ACI has a sort of complex contract system. Providers (destination) and consumers (sources) and subjects and filters and also entries.
Nothing is at one place, everything is nested, not convenient to oversee it.
It is not that strait forward to see "who connects to who with what contract and what ports are allowed" on a single place.
This project helps in that by visualising the contracts like an ACL.

# The ACI_KYC script
The main purpose of the app is to visualise ACI contracts in "human readable" format in a widely used :) excel format.

## Getting Started
Pre-requisites:
- Access to the fabric APIC 

Clone and install requirements.
```
git clone https://github.com/routingalchemy/ACI_KYC.git
cd ACI_KYC
pip install -r requirements.txt 
```

The files in the directory are:
 - `acikyc_app.py` - main app
 - `contracts_template.xlsx` - template for the excel output
 - `data_model.json` - a representation how the contract data is stored

 
## Usage
```
./acikyc_app.py -a APIC_IP_OR_FQDN -u USERNAME -p PASSWORD 
./acikyc_app.py -a APIC_IP_OR_FQDN -u USERNAME -p PASSWORD -d DN_MACTH 
./acikyc_app.py -a APIC_IP_OR_FQDN -u USERNAME -p PASSWORD -c CONTRACT_MATCH
./acikyc_app.py -a APIC_IP_OR_FQDN -u USERNAME -p PASSWORD -d DN_MACTH -c CONTRACT_MATCH

"-d" is a bit more detailed search. It searches in "uni/tn-TENANT/brc-CONTRAC" DN .
"-c" is only searches in the contracts name 

```

### Example

```
All contract from the fabric:
./acikyc_app.py -a APIC_IP_OR_FQDN -u USERNAME -p PASSWORD 

Matches the default contract form the common tenant or whatever contains "common" in its contract DN and "default" in its contract name:
./acikyc_app.py -a APIC_IP_OR_FQDN -u USERNAME -p PASSWORD -d common -c default

Every contract thats name contains "http" (searches in contract's name):
./acikyc_app.py -a APIC_IP_OR_FQDN -u USERNAME -p PASSWORD -c http

Every contract thats DN contains "prod" (searches in contract's DN) it can be a tenant or a contract name:
./acikyc_app.py -a APIC_IP_OR_FQDN -u USERNAME -p PASSWORD -d prod



```
 ## Roadmap
  
  - [ ] More/various details form the contracts/subjects/filters/entries
  - [ ] Summary page for the contracts
  - [X] Get a single contract output 
  - [X] Get a tenant's all contract
  - [ ] Graphviz diagram for graphical output
  - [X] Service graph indication
  - [ ] EPG based contract representation
  - [ ] EPG/Subject lables
  - [ ] Preferred group membership
  - [ ] L3Out Ext-EPG network details
  - [ ] Master EPG membership
  - [ ] Intra-EPG contracts
  - [X] Searching/matching multiple contracts 
 
 
 ## Notes
  
  - In case of longer than 32 character contract names, Excel will notify you that some data might be lost "but not"! (working on it) 
  - Requires at least Python 3.10 [match case statement support](https://docs.python.org/3.10/tutorial/controlflow.html#match-statements)
  - The project files are formatted with [Black](https://github.com/psf/black)
  - Code has been tested on ACI 6.x only with EPG,vzAny,L3Out objects
 