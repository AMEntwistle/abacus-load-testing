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

    def send_graphql_request(self, query_file_name, variables):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f'{self.bearer_token}',
            "apollographql-client-name": "AbacusPerformanceTest",
            "orchard-profile-type": "AbacusProfile",
            "orchard-profile-uuid": "277f57b2-937c-42d0-8cdb-7f05d3f64155",
            "Cache-Control": "no-cache"
        }
        with open(f'graphqlQueries/{query_file_name}.gql', 'r') as file:
            query = file.read()
        body = {
            "query": query,
            "variables": variables
        }
        self.client.post(self.host, json=body, headers=headers, name=query_file_name)

    @staticmethod
    def get_random_variable(key_name):
        with open('requestVariables.json', 'r') as file:
            data = json.load(file)
            values = data.get(key_name, [])
            if not values:
                raise ValueError(f"No {key_name}  found in requestVariables.json")
            return random.choice(values)

    @task
    def visit_contract_page(self):
        contract_id = self.get_random_variable('contractId')
        requests = [
            ('getContractWithAttachments', {"contractId": contract_id}),
            ('getContract', {"contractId": contract_id, "groupAdmin": "PRESENTATIONAL"}),
            ('getTransactionTypesWithGroups', {"groupAdmin": "PRESENTATIONAL"}),
            ('getStores', {}),
            ('getContractPartyList', {"includeOnlySchedules": False, "contractId": contract_id, "limit": 100,
                                      "offset": 0, "targetType": "CONTRIBUTOR"})
        ]

        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(self.send_graphql_request, query_file, variables)
                for query_file, variables in requests
            ]
            for future in futures:
                future.result()
