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
1. Define an instance and provide the login credentials
2. Login to the fabric and get a token
3. Retrieve the Contract details
4. print contract details to file 

### Example

```
contracts = aci_kyc("sandboxapicdc.cisco.com", "admin", "!v3G@!4@Y")
contracts.apic_token()
list = contracts.all_contracts()
contracts.contract2excel(list)

```
 ## Roadmap
  
  - [ ] More/various details form the contracts/subjects/filters
  - [ ] Getting single/some contract output 
  - [ ] Graphviz diagram for graphical output
  - [ ] Service graph indication
  - [ ] EPG based contract representation
  - [ ] EPG/Subject lables
  - [ ] Preferred group membership
  - [ ] L3Out Ext-EPG network details
  - [ ] Master EPG membership
  - [ ] Intra-EPG contracts
 
 
 ## Notes
 
  - Requires at least Python 3.10 [match case statement support](https://docs.python.org/3.10/tutorial/controlflow.html#match-statements)
  - The project files are formatted with [Black](https://github.com/psf/black)
  - Code has been tested on ACI 6.x only with EPG,vzAny,L3Out objects
 