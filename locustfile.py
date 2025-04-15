import json
import os
import random
from concurrent.futures import ThreadPoolExecutor

from locust import HttpUser, task, between
from dotenv import load_dotenv

load_dotenv()


class GatewayUser(HttpUser):
    wait_time = between(1, 5)
    host = os.environ.get('GRAPHQL_URL')

    def __init__(self, environment):
        super().__init__(environment)
        self.bearer_token = os.environ.get('BEARER_TOKEN')
        self.profile_id = os.environ.get('PROFILE_ID')
        self.profile_uuid = os.environ.get('PROFILE_UUID')

    def send_page_requests(self, requests, page_name):
        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(self.send_graphql_request, query_file, variables, page_name)
                for query_file, variables in requests
            ]
        for future in futures:
            future.result()

    def send_graphql_request(self, query_file_name, variables, page_name):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f'{self.bearer_token}',
            "apollographql-client-name": "AbacusPerformanceTest",
            "orchard-profile-type": "AbacusProfile",
            "orchard-profile-id": f"{self.profile_id}",
            "orchard-profile-uuid": f"{self.profile_uuid}",
            "Cache-Control": "no-cache"
        }
        with open(f'graphqlQueries/{query_file_name}.gql', 'r') as file:
            query = file.read()
        body = {
            "query": query,
            "variables": variables
        }
        name = f"{page_name}_{query_file_name}"
        if os.environ.get('GROUP_BY_PAGE').upper() == "TRUE":
            name = page_name
        with self.client.post(self.host, json=body, headers=headers, name=name,
                              catch_response=True) as response:
            # GQL requests fail in body not just in status so need to check for any errors
            if response.status_code == 200:
                response_json = json.loads(response.text)
                if 'errors' in response_json:
                    status_code = response_json['errors'][0]['message'].split(":", 1)[0]
                    response.failure(f"GraphQL error: {status_code}")

    @staticmethod
    def get_random_variable(key_name):
        with open('requestVariables.json', 'r') as file:
            data = json.load(file)
            values = data.get(key_name, [])
            if not values:
                raise ValueError(f"No {key_name}  found in requestVariables.json")
            return random.choice(values)

    @task(5)
    def visit_contract_page(self):
        page_name = "contractPage"
        contract_id = self.get_random_variable('contractId')
        # Common suite gql requests de-scoped, e.g. features, IdentityResources
        requests = [
            ('getContractWithAttachments', {"contractId": contract_id}),
            ('getContract', {"contractId": contract_id, "groupAdmin": "PRESENTATIONAL"}),
            ('getTransactionTypesWithGroups', {"groupAdmin": "PRESENTATIONAL"}),
            ('getStores', {}),
            ('getContractPartyList', {"includeOnlySchedules": False, "contractId": contract_id, "limit": 100,
                                      "offset": 0, "targetType": "CONTRIBUTOR"}),
            ('getContractAdvancesByStatus', {"contractId": contract_id,
                                             "status": "IN_REVIEW", "limit": 20, "offset": 0}),
            ('getContractAdvancesPaid', {"contractId": contract_id, "limit": 20, "offset": 0}),
            ('getContractAdvancesPending', {"contractId": contract_id, "limit": 20, "offset": 0})
        ]

        self.send_page_requests(requests, page_name)

    @task(5)
    def visit_account_page(self):
        page_name = "accountPage"
        account_id = self.get_random_variable('accountId')
        requests = [
            ('getAccountById', {"accountId": account_id}),
            ('getAccountFullDetail', {"accountId": account_id}),
            ('getAccountLedgerList', {"accountId": account_id, "limit": 20, "offset": 0})
        ]

        self.send_page_requests(requests, page_name)
