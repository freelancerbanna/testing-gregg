from django.shortcuts import render
from pypardot.client import PardotAPI
from inflection import singularize


def pardot_test(request, campaign_id):
    p = PardotAPI(
        email='matthew@ragingbits.com',
        password='testThis$testThis1',
        user_key='89b36f8503d985f19abf0e4f1c3b48fc'
    )

    campaign = {'id': campaign_id,
                'name': None,
                'opportunities': [],
                'opportunities_value': 0,
                'errors': [],
                }
    if p.authenticate():
        opportunities = get_queries(p, 'opportunities')
        for opportunity in opportunities:
            this_campaign = opportunity.get('campaign')
            if this_campaign['id'] == int(campaign_id):
                campaign['name'] = this_campaign['name']
                campaign['opportunities'].append(opportunity)
                campaign['opportunities_value'] += opportunity['value']

        campaign['opportunities_count'] = len(campaign['opportunities'])
    else:
        campaign['errors'].append('Failed to connect to Pardot API.')

    return render(request, 'pardot_test.html', {"campaign": campaign})


def get_queries(p, things_string):
    things = getattr(p, things_string).query()
    print "Found %d %s" % (things['total_results'], things_string)

    pulled = 0
    thing_list = []
    for thing in things[singularize(things_string)]:
        thing_list.append(thing)
        pulled += 1
    while pulled < things['total_results']:
        print things['total_results'] - pulled
        things = getattr(p, things_string).query(offset=pulled)
        for thing in things[singularize(things_string)]:
            thing_list.append(thing)
            pulled += 1

    print "Pulled %d %s" % (pulled, things_string)
    return thing_list
