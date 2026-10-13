// Impact-analysis queries used in Step 6 (Neo4j AuraDB, Cypher 25)

// Q1. If the account record layout (copybook CVACT01Y) changes, what is affected?
MATCH path = (c:Copybook {id: 'CVACT01Y'})-[:DESCRIBES]->(d:Dataset)<-[:READS|UPDATES|WRITES]-(p:Program)<-[:EXECUTES]-(j:Job)
RETURN path;

// Q2. Which files does CBACT04C change? (files needing before/after reconciliation)
MATCH (p:Program {id: 'CBACT04C'})-[r:UPDATES|WRITES]->(d:Dataset)
RETURN d.id AS file, type(r) AS action, r.ddname AS dd_name, r.line AS code_lines;

// Q3. In what order do the jobs run?
MATCH path = (a:Job)-[:PRECEDES*]->(b:Job)
RETURN path;

// Q4. Which business rules were found?
MATCH (a)-[r]->(b)
WHERE r.detail CONTAINS 'Business rule'
RETURN a.id AS program, b.id AS file, r.detail AS rule, r.line AS lines;
