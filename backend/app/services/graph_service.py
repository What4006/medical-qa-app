from neo4j import GraphDatabase
import os

class Neo4jGraph:
    def __init__(self):
        # 从 .env 中读取配置 (确保在 manage.py 或 app/__init__.py 中已加载)
        uri = os.environ.get("NEO4J_URI")
        user = os.environ.get("NEO4J_USER")
        password = os.environ.get("NEO4J_PASSWORD")

        if not uri or not user or not password:
            raise ValueError("Neo4j 环境变量未设置 (NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)")

        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def run_query(self, query, parameters=None):
        with self._driver.session() as session:
            result = session.run(query, parameters)
            return [record.data() for record in result]

# 您可以创建一个全局实例供其他服务使用
graph_db = Neo4jGraph()

# 在您的 API (如 chat_api.py) 中就可以调用
# from ..services.graph_service import graph_db
# ...
# graph_data = graph_db.run_query("MATCH (n:Symptom {name: '头痛'}) RETURN n")