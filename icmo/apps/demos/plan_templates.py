from decimal import Decimal
from random import randint


class BaseRevenuePlanTemplate(object):
    target_annual_revenue = 0
    segments = None
    quarter_shares = None
    programs = None
    cost_per_lead = 0
    growth_range = (10, 30)

    budget_actuals_fuzz = 20
    campaign_actuals_fuzz = 20
    campaigns_per_program_range = (1, 3)
    max_program_share = 50

    @classmethod
    def get_random_growth_multiplier(cls):
        return 1 - randint(*cls.growth_range) / Decimal(100)

    @classmethod
    def get_random_program(cls):
        return cls.programs[randint(0, len(cls.programs) - 1)]

    @classmethod
    def get_random_program_set(cls):
        marketing_mix = 0
        progs = []
        while marketing_mix < 100:
            prog = cls.get_new_random_program(progs)
            if not prog:
                break
            prog['share'] = cls.get_random_program_marketing_share(prog['min_share'])
            marketing_mix += prog['share']
            progs.append(prog)
        if marketing_mix < 100:
            progs[-1]['share'] += 100 - marketing_mix
        elif marketing_mix > 100:
            progs[-1]['share'] -= marketing_mix - 100
        return progs

    @classmethod
    def get_new_random_program(cls, current_progs):
        if len(current_progs) == len(cls.programs):
            return None
        prog = cls.get_random_program()
        if prog in current_progs:
            return cls.get_new_random_program(current_progs)
        return prog

    @classmethod
    def get_random_budget_actuals_fuzz_multiplier(cls):
        budget_fuzz_range = (100 - cls.budget_actuals_fuzz, 100 + cls.budget_actuals_fuzz)
        return randint(*budget_fuzz_range) / Decimal(100)

    @classmethod
    def get_random_program_marketing_share(cls, min_share, max_share=max_program_share):
        return randint(min_share, max_share)

    @classmethod
    def get_random_campaign_actuals_fuzz_multiplier(cls):
        campaign_actuals_fuzz_range = (
            100 - cls.campaign_actuals_fuzz, 100 + cls.campaign_actuals_fuzz)
        return randint(*campaign_actuals_fuzz_range) / Decimal(100)

    @classmethod
    def get_random_campaigns_per_program(cls):
        return randint(*cls.campaigns_per_program_range)


class TenMRevenuePlanTemplate(BaseRevenuePlanTemplate):
    target_annual_revenue = 10000000
    cost_per_lead = 150
    segments = [
        dict(name='Healthcare', target=2000000, average_sale=25000),
        dict(name='Financial Services', target=3500000, average_sale=25000),
        dict(name='Manufacturing', target=2500000, average_sale=35000),
        dict(name='Current Customers', target=1000000, average_sale=15000),
        dict(name='Sell-Thru Partners', target=1000000, average_sale=20000),
    ]
    quarter_shares = [Decimal(.15), Decimal(.225), Decimal(.275), Decimal(.35)]

    programs = [
        dict(name='Email Content Syndication Program', min_share=25),
        dict(name='Webinar Program', min_share=15),
        dict(name='Seminar Program', min_share=15),
        dict(name='Tradeshow & Events Program', min_share=15),
        dict(name='Social Media Program', min_share=15),
        dict(name='SEO Program', min_share=15),
        dict(name='PPC Program', min_share=15),
        dict(name='Referral Program', min_share=15),
        dict(name='Survey2Lead Program', min_share=15),
        dict(name='Telemarketing Program', min_share=15),
        dict(name='Advertising Program', min_share=1),
        dict(name='Affiliate Program', min_share=1),
    ]

    custom_budget_line_items = {
        'Infrastructure': [
            dict(name='Marketing Automation Solution', cost_per_month=1500),
            dict(name='CRM Solution', cost_per_month=1500),
            dict(name='intelligentRevenue', cost_per_month=500),
        ],
        'PR': [
            dict(name='Press Relations', cost_per_month=6000),
            dict(name='Investor Relations', cost_per_month=1000),
            dict(name='Internal Communications', cost_per_month=500),
        ],
        'Product Marketing': [
            dict(name='Collateral Creation & Distribution', cost_per_month=5000),
        ],
        'Corporate Communications': [
            dict(name='Website', cost_per_month=2000),
            dict(name='Branding', cost_per_month=1000),
            dict(name='Misc Design & Communication', cost_per_month=1000),
        ]
    }


class FourMRevenuePlanTemplate(BaseRevenuePlanTemplate):
    target_annual_revenue = 4000000
    cost_per_lead = 150
    segments = [
        dict(name='Healthcare', target=500000, average_sale=25000),
        dict(name='Financial Services', target=1000000, average_sale=25000),
        dict(name='Manufacturing', target=500000, average_sale=35000),
        dict(name='Current Customers', target=1000000, average_sale=15000),
        dict(name='Sell-Thru Partners', target=1000000, average_sale=20000),
    ]
    quarter_shares = [Decimal(.15), Decimal(.225), Decimal(.275), Decimal(.35)]

    programs = [
        dict(name='Email Content Syndication Program', min_share=25),
        dict(name='Webinar Program', min_share=15),
        dict(name='Seminar Program', min_share=15),
        dict(name='Tradeshow & Events Program', min_share=15),
        dict(name='Social Media Program', min_share=15),
        dict(name='SEO Program', min_share=15),
        dict(name='PPC Program', min_share=15),
        dict(name='Referral Program', min_share=15),
        dict(name='Survey2Lead Program', min_share=15),
        dict(name='Telemarketing Program', min_share=15),
        dict(name='Advertising Program', min_share=1),
        dict(name='Affiliate Program', min_share=1),
    ]

    custom_budget_line_items = {
        'Infrastructure': [
            dict(name='Marketing Automation Solution', cost_per_month=1500),
            dict(name='CRM Solution', cost_per_month=1500),
            dict(name='intelligentRevenue', cost_per_month=500),
        ],
        'PR': [
            dict(name='Press Relations', cost_per_month=6000),
            dict(name='Investor Relations', cost_per_month=1000),
            dict(name='Internal Communications', cost_per_month=500),
        ],
        'Product Marketing': [
            dict(name='Collateral Creation & Distribution', cost_per_month=5000),
        ],
        'Corporate Communications': [
            dict(name='Website', cost_per_month=2000),
            dict(name='Branding', cost_per_month=1000),
            dict(name='Misc Design & Communication', cost_per_month=1000),
        ]
    }


class SampleRevenuePlanTemplate(BaseRevenuePlanTemplate):
    target_annual_revenue = 10000000
    cost_per_lead = 150
    segments = [
        dict(name='Healthcare', target=2000000, average_sale=25000),
        dict(name='Construction', target=2500000, average_sale=35000),
        dict(name='Financial Services', target=3500000, average_sale=25000),
    ]
    quarter_shares = [Decimal(.15), Decimal(.225), Decimal(.275), Decimal(.35)]

    programs = [
        dict(name='Email Content Syndication Program', min_share=50),
        dict(name='Webinar Program', min_share=50),
        dict(name='Seminar Program', min_share=50),
        dict(name='Tradeshow & Events Program', min_share=50),
        dict(name='Social Media Program', min_share=50),
        dict(name='SEO Program', min_share=50),
        dict(name='PPC Program', min_share=50),
        dict(name='Referral Program', min_share=50),
        dict(name='Advertising Program', min_share=50),
        dict(name='Affiliate Program', min_share=50),
    ]

    custom_budget_line_items = {
        'Infrastructure': [
            dict(name='Marketing Automation Solution', cost_per_month=1500),
            dict(name='CRM Solution', cost_per_month=1500),
            dict(name='intelligentRevenue', cost_per_month=500),
        ],
    }
