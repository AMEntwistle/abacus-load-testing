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
        }
        with open(f'graphqlQueries/{query_file_name}.gql', 'r') as file:
            query = file.read()
        variables = self.assign_random_values(query_file_name, variables)
        body = {
            "query": query,
            "variables": variables
        }
        self.client.post(self.host, json=body, headers=headers, name=query_file_name)

    @staticmethod
    def assign_random_values(query_file_name, variables):
        with open('requestVariables.json', 'r') as file:
            request_variables = json.load(file)
        for key, value in variables.items():
            if isinstance(value, str) and "RANDOM_VALUE" in value:
                available_values = request_variables[query_file_name][key]
                random_value = random.choice(available_values)
                variables[key] = random_value
        return variables

    @task
    def visit_contract_page(self):
        requests = [
            ('getContract', {"contractId": "RANDOM_VALUE", "groupAdmin": "PRESENTATIONAL"}),
            ('getTransactionTypesWithGroups', {"groupAdmin": "PRESENTATIONAL"}),
        ]

        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(self.send_graphql_request, query_file, variables)
                for query_file, variables in requests
            ]
            for future in futures:
                future.result()
