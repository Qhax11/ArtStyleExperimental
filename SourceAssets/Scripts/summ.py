import json
a = json.load(open('plan2.json'))
i = next(i for i, x in enumerate(a) if x.get('action_summary') == 'Opens the export menu')
sel = []; k = 0
for x in a[:i]:
    if x['action'] == 'left_click' and x['coordinate'][0] == 18 and 'again' not in x['action_summary']:
        k = 0
    if x['action'] == 'scroll':
        k = x['scroll_amount']
    if x.get('action_summary', '').startswith('Selects the next'):
        sel.append((x['action_summary'].split()[3], k, x['coordinate']))
cap = []; cur = None
for x in a[i:]:
    if x['action'] == 'left_click' and x['coordinate'][0] == 18 and 'again' not in x['action_summary']:
        cur = [x['action_summary'].split()[2], 0]; cap.append(cur)
    if x['action'] == 'scroll' and x['scroll_amount'] != 50 and cur:
        cur[1] = x['scroll_amount']
path = [x['text'] for x in a if x['action'] == 'type'][0]
print('SEL', sel); print('CAP', cap); print(path)
