"""Small data-only Boolean rule language for mechanical task keys.

No eval(), Python expressions, or model-produced code are executed.
"""


class RuleError(ValueError):
    pass


def evaluate(node, facts, fields):
    if not isinstance(node, dict) or len(node) != 1:
        raise RuleError('Rule node must be a one-key object')
    op, value = next(iter(node.items()))
    if op in {'all', 'any'}:
        if not isinstance(value, list) or not value:
            raise RuleError(f'{op} requires a nonempty list')
        answers = [evaluate(child, facts, fields) for child in value]
        return all(answers) if op == 'all' else any(answers)
    if op == 'not':
        return not evaluate(value, facts, fields)
    if op == 'eq':
        if not isinstance(value, dict) or set(value) != {'field', 'value'}:
            raise RuleError('eq requires field and value')
        field = value['field']
        if field not in fields or field not in facts:
            raise RuleError('Unknown or missing field: ' + str(field))
        if value['value'] not in fields[field]:
            raise RuleError('Value outside declared field domain')
        return facts[field] == value['value']
    if op == 'in':
        if not isinstance(value, dict) or set(value) != {'field', 'values'}:
            raise RuleError('in requires field and values')
        field = value['field']
        if field not in fields or field not in facts or not isinstance(value['values'], list) or not value['values']:
            raise RuleError('Invalid in field/values')
        if not set(value['values']) <= set(fields[field]):
            raise RuleError('Value outside declared field domain')
        return facts[field] in value['values']
    raise RuleError('Unsupported operator: ' + str(op))


def check_card(card):
    if not isinstance(card, dict):
        raise RuleError('Card must be an object')
    raw_fields = card.get('fields')
    if not isinstance(raw_fields, list) or not raw_fields:
        raise RuleError('Card needs fields')
    fields = {}
    for field in raw_fields:
        if not isinstance(field, dict) or not {'name', 'values'} <= set(field):
            raise RuleError('Invalid field definition')
        name = field['name']
        values = field['values']
        if not isinstance(name, str) or not name.isidentifier() or name in fields:
            raise RuleError('Invalid/duplicate field name')
        if not isinstance(values, list) or len(values) < 2 or len(set(map(str, values))) != len(values):
            raise RuleError('Field needs at least two unique values')
        fields[name] = values
    cases = card.get('cases')
    if not isinstance(cases, list) or len(cases) < 10:
        raise RuleError('At least ten distinct controlled facts required')
    ids, texts, vectors = set(), set(), set()
    labels = []
    for case in cases:
        if not isinstance(case, dict) or not {'id', 'fact_text', 'facts'} <= set(case):
            raise RuleError('Case needs id, fact_text, facts')
        if not isinstance(case['id'], str) or not case['id'] or case['id'] in ids:
            raise RuleError('Duplicate/empty case id')
        if not isinstance(case['fact_text'], str) or len(case['fact_text'].strip()) < 12 or case['fact_text'] in texts:
            raise RuleError('Duplicate/short fact text')
        facts = case['facts']
        if not isinstance(facts, dict) or set(facts) != set(fields):
            raise RuleError('Case facts must specify every declared field exactly once')
        for name, value in facts.items():
            if value not in fields[name]:
                raise RuleError('Case value outside declared field domain')
        vector = tuple((k, str(facts[k])) for k in sorted(facts))
        ids.add(case['id'])
        texts.add(case['fact_text'])
        vectors.add(vector)
        labels.append(evaluate(card['predicate'], facts, fields))
    if sum(labels) < 4 or len(labels) - sum(labels) < 4:
        raise RuleError('Need at least four positive and four negative facts')
    return {'field_domains': fields, 'n_cases': len(cases), 'n_positive': sum(labels),
            'n_negative': len(labels) - sum(labels),
            'n_unique_fact_vectors': len(vectors),
            'n_repeated_fact_vectors': len(cases) - len(vectors)}
