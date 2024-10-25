import requests
from openpyxl import Workbook
from openpyxl import load_workbook
import json


class aci_kyc:
    """ACI Know Your Contracts. A Contract exporter and visualiser tool"""

    def __init__(self, hostname, username, password):
        """Host resource definition"""
        self.hostname = hostname
        self.username = username
        self.password = password
        self.token = {}
        self.url = ""
        self.http_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        self.http_cert_verify = False

    def apic_token(self):
        """Getting a token from the ACI APIC"""
        host = "https://{}/api/aaaLogin.json".format(self.hostname)
        data = {
            "aaaUser": {"attributes": {"name": self.username, "pwd": self.password}}
        }
        cookie_key = "APIC-cookie"
        cookie_value = 'response.json()["imdata"][0]["aaaLogin"]["attributes"]["token"]'

        try:

            response = requests.post(
                host,
                headers=self.http_headers,
                data=json.dumps(data),
                verify=self.http_cert_verify,
            )
            response.raise_for_status()
            if response.status_code != 204:
                self.token = {cookie_key: eval(cookie_value)}
        except requests.exceptions.RequestException as error:
            raise SystemExit(error)

    def __api_get(self):
        """Get request for retrieving the contract data"""

        host = "https://{}{}".format(self.hostname, self.url)
        try:
            response = requests.get(
                host,
                cookies=self.token,
                headers=self.http_headers,
                verify=self.http_cert_verify,
            )
            response.raise_for_status()  # raises exception when not a 2xx response
            return response.json()
        except requests.exceptions.RequestException as error:
            raise SystemExit(error)

    def __contract_details(self, contract_dn):
        """Get a contract detail (DN)"""
        self.url = "/api/node/mo/{}.json?query-target=subtree".format(contract_dn)
        brcp_dn_data = self.__api_get()
        source_grp, destination, subject, filter = [], [], [], []
        for brcp_dn_imdata in brcp_dn_data["imdata"]:
            if "vzRtCons" in brcp_dn_imdata.keys():  # consumer/source details
                source_grp.append(
                    {
                        "name": brcp_dn_imdata["vzRtCons"]["attributes"]["tDn"].split(
                            "/"
                        )[-1][4:],
                        "app": brcp_dn_imdata["vzRtCons"]["attributes"]["dn"].split(
                            "/"
                        )[-2][3:],
                        "tenant": brcp_dn_imdata["vzRtCons"]["attributes"]["dn"].split(
                            "/"
                        )[1][3:],
                        "type": self.__object_norm(
                            brcp_dn_imdata["vzRtCons"]["attributes"]["tCl"]
                        ),
                    }
                )
            if "vzRtProv" in brcp_dn_imdata.keys():  # provider/destination details
                destination.append(
                    {
                        "name": brcp_dn_imdata["vzRtProv"]["attributes"]["tDn"].split(
                            "/"
                        )[-1][4:],
                        "app": brcp_dn_imdata["vzRtProv"]["attributes"]["dn"].split(
                            "/"
                        )[-2][3:],
                        "tenant": brcp_dn_imdata["vzRtProv"]["attributes"]["dn"].split(
                            "/"
                        )[1][3:],
                        "type": self.__object_norm(
                            brcp_dn_imdata["vzRtProv"]["attributes"]["tCl"]
                        ),
                    }
                )
            if "vzRtAnyToCons" in brcp_dn_imdata.keys():  # vzany sources
                source_grp.append(
                    {
                        "name": brcp_dn_imdata["vzRtAnyToCons"]["attributes"][
                            "tDn"
                        ].split("/")[-2][4:],
                        "app": "",
                        "tenant": brcp_dn_imdata["vzRtAnyToCons"]["attributes"][
                            "dn"
                        ].split("/")[1][3:],
                        "type": self.__object_norm(
                            brcp_dn_imdata["vzRtAnyToCons"]["attributes"]["tCl"]
                        ),
                    }
                )
            if "vzRtAnyToProv" in brcp_dn_imdata.keys():  # vzany providers
                destination.append(
                    {
                        "name": brcp_dn_imdata["vzRtAnyToProv"]["attributes"][
                            "tDn"
                        ].split("/")[-2][4:],
                        "app": "",
                        "tenant": brcp_dn_imdata["vzRtAnyToProv"]["attributes"][
                            "dn"
                        ].split("/")[1][3:],
                        "type": self.__object_norm(
                            brcp_dn_imdata["vzRtAnyToProv"]["attributes"]["tCl"]
                        ),
                    }
                )
            if "vzSubj" in brcp_dn_imdata.keys():  # subjects
                subject.append(
                    {
                        "name": brcp_dn_imdata["vzSubj"]["attributes"]["dn"].split("/")[
                            -1
                        ][5:],
                        "revfltports": brcp_dn_imdata["vzSubj"]["attributes"][
                            "revFltPorts"
                        ],
                    }
                )
            if "vzRsSubjFiltAtt" in brcp_dn_imdata.keys():
                for i in subject:
                    if (
                        brcp_dn_imdata["vzRsSubjFiltAtt"]["attributes"]["dn"].split(
                            "/"
                        )[-2][5:]
                    ) in i["name"]:
                        filter.append(
                            {
                                "action": brcp_dn_imdata["vzRsSubjFiltAtt"][
                                    "attributes"
                                ]["action"]
                            }
                        )
                        break  # if the subject attachment name mathces the subject name assiign the subject action to the filter
                if brcp_dn_imdata["vzRsSubjFiltAtt"]["attributes"]["tDn"] != "":
                    self.url = "/api/node/mo/{}.json?query-target=subtree".format(
                        brcp_dn_imdata["vzRsSubjFiltAtt"]["attributes"]["tDn"]
                    )  # set the filter url
                    filter_dn_data = self.__api_get()
                    entries = []
                    for filter_dn_imdata in filter_dn_data["imdata"]:
                        if "vzFilter" in filter_dn_imdata.keys():
                            filter[len(filter) - 1]["name"] = filter_dn_imdata[
                                "vzFilter"
                            ]["attributes"]["name"]
                        if "vzEntry" in filter_dn_imdata.keys():
                            entries.append(
                                {
                                    "name": filter_dn_imdata["vzEntry"]["attributes"][
                                        "dn"
                                    ].split("/")[-1][2:],
                                    "etht": filter_dn_imdata["vzEntry"]["attributes"][
                                        "etherT"
                                    ],
                                    "sport": "{}-{}".format(
                                        self.__object_norm(
                                            filter_dn_imdata["vzEntry"]["attributes"][
                                                "sFromPort"
                                            ]
                                        ),
                                        self.__object_norm(
                                            filter_dn_imdata["vzEntry"]["attributes"][
                                                "sToPort"
                                            ]
                                        ),
                                    ),
                                    "dport": "{}-{}".format(
                                        self.__object_norm(
                                            filter_dn_imdata["vzEntry"]["attributes"][
                                                "dFromPort"
                                            ]
                                        ),
                                        self.__object_norm(
                                            filter_dn_imdata["vzEntry"]["attributes"][
                                                "dToPort"
                                            ]
                                        ),
                                    ),
                                    "stateful": filter_dn_imdata["vzEntry"][
                                        "attributes"
                                    ]["stateful"],
                                    "tcprules": filter_dn_imdata["vzEntry"][
                                        "attributes"
                                    ]["tcpRules"],
                                }
                            )
                            # icmpV4T and icmpV6T
                    filter[len(filter) - 1]["entries"] = entries
                    i["filter"] = filter
        return source_grp, destination, subject

    def all_contracts(self):
        """Get all contracts from the fabric (Class)"""
        contract_list = []
        self.url = "/api/node/class/vzBrCP.json"
        brcp_class_data = self.__api_get()
        for brcp_class_imdata in brcp_class_data["imdata"]:
            contract_list.append(
                {
                    "name": brcp_class_imdata["vzBrCP"]["attributes"]["name"],
                    "tenant": brcp_class_imdata["vzBrCP"]["attributes"]["dn"].split(
                        "/"
                    )[1][3:],
                    "scope": brcp_class_imdata["vzBrCP"]["attributes"]["scope"],
                }
            )
            source_grp, destination, subject = self.__contract_details(
                brcp_class_imdata["vzBrCP"]["attributes"]["dn"]
            )
            contract_list[len(contract_list) - 1]["source"] = source_grp
            contract_list[len(contract_list) - 1]["destination"] = destination
            contract_list[len(contract_list) - 1]["subject"] = subject
        return contract_list

    def contract2excel(self, clist):
        """Output the contract data to excel"""
        wb = load_workbook(filename="contracts_template.xlsx")
        row_offset = 3
        for contract in clist:
            ws = wb.copy_worksheet(wb["template"])
            ws.title = "{}.{}".format(contract["tenant"], contract["name"])
            ws["B1"] = contract["name"]
            ws["D1"] = contract["tenant"]
            ws["F1"] = contract["scope"]
            for soi in range(
                len(contract["source"])
            ):  # source and destination for loop to colapse
                ws["A{}".format(soi + row_offset)] = "{}:{}:{}".format(
                    contract["source"][soi]["tenant"],
                    contract["source"][soi]["app"],
                    contract["source"][soi]["name"],
                )
                ws["B{}".format(soi + row_offset)] = "{}".format(
                    contract["source"][soi]["type"]
                )
            for dei in range(len(contract["destination"])):
                ws["L{}".format(dei + row_offset)] = "{}:{}:{}".format(
                    contract["destination"][dei]["tenant"],
                    contract["destination"][dei]["app"],
                    contract["destination"][dei]["name"],
                )
                ws["M{}".format(dei + row_offset)] = "{}".format(
                    contract["destination"][dei]["type"]
                )
            entry_row_offset = 3
            for subject_it in contract["subject"]:
                ws["C{}".format(entry_row_offset)] = subject_it["name"]
                smfrom = entry_row_offset
                if "filter" in subject_it:
                    for filter_it in subject_it["filter"]:
                        fmfrom = entry_row_offset
                        ws["D{}".format(entry_row_offset)] = filter_it["name"]
                        ws["E{}".format(entry_row_offset)] = filter_it["action"]
                        entry_size = len(filter_it["entries"])
                        for eni in range(entry_size):
                            ws["F{}".format(eni + entry_row_offset)] = filter_it[
                                "entries"
                            ][eni]["name"]
                            ws["G{}".format(eni + entry_row_offset)] = filter_it[
                                "entries"
                            ][eni]["etht"]
                            ws["H{}".format(eni + entry_row_offset)] = filter_it[
                                "entries"
                            ][eni]["sport"]
                            ws["I{}".format(eni + entry_row_offset)] = filter_it[
                                "entries"
                            ][eni]["dport"]
                            ws["J{}".format(eni + entry_row_offset)] = filter_it[
                                "entries"
                            ][eni]["stateful"]
                            ws["K{}".format(eni + entry_row_offset)] = filter_it[
                                "entries"
                            ][eni]["tcprules"]
                        entry_row_offset += entry_size
        wb.remove(wb["template"])
        wb.save("contracts.xlsx")

    def __object_norm(self, changeme):
        """Auxaliry function to replace ACI object names with meaninful ones"""
        match changeme:
            case "unspecified":
                return "any"
            case "fvAEPg":
                return "EPG"
            case "fvESg":
                return "ESG"
            case "l2extInstP":
                return "L2Out"
            case "l3extInstP":
                return "L3Out"
            case _:
                return changeme


#contracts = aci_kyc("sandboxapicdc.cisco.com", "admin", "!v3G@!4@Y")
#contracts.apic_token()
#list = contracts.all_contracts()
#contracts.contract2excel(list)
